# Agent, Experiments & Puzzle Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện toàn diện phân hệ Agent & Thực nghiệm đo đạc (LogicAgent verification, Hint system, Puzzle validator, 3x3/4x4/5x5 benchmark puzzle suites, metrics collection, CSV/LaTeX/Chart export, và Isolation/Oracle tests) trên nền bộ giải DPLL từ nhánh `feature/dpll-solver`.

**Architecture:** Kế thừa bộ giải `sat/dpll.py` đã hoàn thiện từ `origin/feature/dpll-solver` (không đụng `typst/`). Sử dụng kiến trúc hướng sự kiện và Protocol: `LogicAgent` và `suggest_hint` chỉ giao tiếp qua `PublicGame` và `PublicKnowledge` (Rule 1). Toàn bộ puzzle mới được kiểm chứng tính duy nhất (uniqueness) và tính giải được không cần đoán (no-guess solvable) bằng `validate_puzzle_file` trước khi nạp vào bộ thực nghiệm benchmark.

**Tech Stack:** Python 3.14, SAT propositional logic (CNF, DPLL solver), Matplotlib (vẽ biểu đồ), CSV/LaTeX exporter, unittest/pytest.

**Spec:** [design-spec.md](file:///home/quang/.gemini/antigravity/brain/b9ae89d9-c996-4516-b655-1e8ff8221c5d/design-spec.md) và [AI - Project 2.pdf](file:///home/quang/Workspace/24120127/NM_AI/2_project_griductive_solver/AI%20-%20Project%202.pdf).

## Global Constraints

- **Rule 1 (Data Isolation):** `agent/` tuyệt đối không import `engine/`, `gui/`, hoặc `app/`. Agent chỉ nhận `PublicState` và `PublicKnowledge`.
- **Rule 5 (No Guessing):** Mọi bước đi của `LogicAgent` và `Hint` đều phải được chứng minh bởi entailment qua SAT (`KB ∧ ¬C_i` là UNSAT). Tuyệt đối không chọn bừa một model khả dĩ hay đọc `puzzle.solution`.
- **Mã hóa không hard-code:** Không được hard-code CNF cho bất kỳ puzzle nào; mọi clue phải được phân tích và encode tự động.
- **Tính chuẩn tắc của Puzzle:** Mọi puzzle trong `Source/puzzles/` phải có đúng 1 nghiệm duy nhất (UNIQUE) trên các biến chính và giải được 100% bằng suy luận suy diễn thuần túy.
- **Thực nghiệm đầy đủ:** Ghi nhận đủ 6 nhóm chỉ số cho mọi puzzle, không bỏ sót các trường hợp failure/timeout.
- **Phạm vi file:** Chỉ can thiệp vào `Source/griductive/agent/`, `Source/griductive/experiments/`, `Source/puzzles/`, `Source/results/`, `Source/tests/`. Tuyệt đối không sửa `typst/` để tránh xung đột với Minh.

## Review Focus

1. `validate_puzzle_file` phải tính cả các ô `initially_revealed` vào mệnh đề đơn vị khi kiểm tra tính duy nhất (nếu không sẽ báo sai thành `MULTIPLE`).
2. `LogicAgent.iter_steps` và `suggest_hint` phải duyệt các ô chưa mở theo thứ tự determinism chuẩn (row-major: A1, B1, C1, A2,...) để đảm bảo tái lập kết quả.
3. `LogicAgent` phải cập nhật chính xác các trường thống kê DPLL (`total_sat_calls`, `total_decisions`, `total_propagations`, `total_backtracks`) từ `CountingSolver`.
4. `experiments/export.py` phải xử lý an toàn khi thiếu thư viện `matplotlib` (fallback ghi log cảnh báo, không làm crash toàn bộ benchmark).
5. AST test trong `Source/tests/test_isolation.py` phải quét đệ quy mọi file `.py` trong `agent/` để chặn mọi hành vi vi phạm kiến trúc.

---

### Task 1: Thiết lập nhánh làm việc & Chữa lỗi `validate_puzzle_file`

**Files:**
- Modify: `Source/griductive/experiments/validate_puzzle.py`
- Branch: Tạo nhánh `feature/agent-experiments` từ `origin/feature/dpll-solver`

**Interfaces:**
- Consumes: `origin/feature/dpll-solver` (DPLLSolver in `Source/griductive/sat/dpll.py`)
- Produces: `validate_puzzle_file(path: str | Path) -> tuple[bool, str]` hỗ trợ đầy đủ `initially_revealed`

- [ ] **Step 1: Checkout nhánh mới từ `origin/feature/dpll-solver`**

```bash
git checkout -b feature/agent-experiments origin/feature/dpll-solver
git checkout origin/develop -- typst/
```

- [ ] **Step 2: Viết test kiểm tra `validate_puzzle_file` trên `json_example.json`**

Chạy lệnh kiểm tra hiện tại:
`PYTHONPATH=Source python3 -c "from griductive.experiments.validate_puzzle import validate_puzzle_file; valid, msg = validate_puzzle_file('Source/puzzles/json_example.json'); assert valid, msg"`
Expected: FAIL với thông báo `Kiểm tra Uniqueness thất bại: kết quả là UniquenessResult.MULTIPLE`.

- [ ] **Step 3: Cập nhật `validate_puzzle_file` trong `Source/griductive/experiments/validate_puzzle.py`**

Bổ sung các unit clause cho các ô trong `puzzle.initially_revealed` vào công thức CNF trước khi gọi `check_uniqueness`:
```python
# Bổ sung các ô đã lộ ban đầu vào CNF
for cell in puzzle.initially_revealed:
    var = varmap.coord_to_var(cell)
    lit = var if puzzle.solution[cell] else -var
    cnf.add_clause([lit])
```

- [ ] **Step 4: Chạy kiểm tra lại để đảm bảo test PASS**

Run: `PYTHONPATH=Source python3 Source/main.py --validate --puzzle Source/puzzles/json_example.json`
Expected: In ra `Validation result for Source/puzzles/json_example.json: VALID` và trả về mã 0.

- [ ] **Step 5: Commit**

```bash
git add Source/griductive/experiments/validate_puzzle.py
git commit -m "fix(experiments): include initially_revealed unit clauses in puzzle uniqueness check"
```

---

### Task 2: Xây dựng Bộ Kiểm thử Độc lập & Cô lập (Isolation, Entailment & Oracle)

**Files:**
- Modify: `Source/tests/test_isolation.py`
- Modify: `Source/tests/test_entailment.py`
- Modify: `Source/tests/oracle.py`
- Create: `Source/tests/run_tests.py` (Script chạy test độc lập không phụ thuộc pytest hệ thống)

**Interfaces:**
- Consumes: `agent/ports.py`, `agent/logic_agent.py`, `domain/types.py`, `reasoning/entailment.py`, `sat/dpll.py`
- Produces: Bộ test hoàn chỉnh kiểm tra 2 lớp bảo vệ Rule 1 (AST check + MockGame check) và tính đúng đắn của Entailment

- [ ] **Step 1: Viết test MockGame động trong `Source/tests/test_isolation.py`**

Bổ sung lớp `MockGame(PublicGame)` ghi nhận mọi truy cập:
- Nếu agent cố tình truy cập bất kỳ thuộc tính nào ngoài `public_state` và `submit_verdict`, ném `AssertionError`.
- Kiểm tra `LogicAgent.run(mock_game)` chạy an toàn và không vi phạm ranh giới dữ liệu.

- [ ] **Step 2: Cập nhật `Source/tests/test_entailment.py`**

Bổ sung các test case:
- Ví dụ kinh điển trong đề bài (§3.4): `KB = (A ∨ B) ∧ (¬A ∨ B)` -> `B` là `CRIMINAL`, `A` là `UNKNOWN`.
- Trường hợp ép `INNOCENT`: `KB = (A ∨ ¬B) ∧ (¬A ∨ ¬B)` -> `B` là `INNOCENT`.
- Trường hợp `KB` mâu thuẫn ngay từ đầu -> `check_kb_consistent` trả về `SatStatus.UNSAT`.
- Trường hợp `TIMEOUT` -> `classify` trả về `Classification.TIMEOUT`.

- [ ] **Step 3: Tạo test runner tích hợp `Source/tests/run_tests.py`**

Tạo script tự động discover và thực thi toàn bộ test functions trong `Source/tests/` bằng Python chuẩn (`unittest` hoặc function runner), xuất kết quả rõ ràng (PASS/FAIL) mà không phụ thuộc vào `pytest` bên ngoài.

- [ ] **Step 4: Chạy test runner để xác nhận toàn bộ test PASS**

Run: `PYTHONPATH=Source python3 Source/tests/run_tests.py`
Expected: Toàn bộ test isolation, entailment, dpll, oracle đều PASS (0 errors, 0 failures).

- [ ] **Step 5: Commit**

```bash
git add Source/tests/test_isolation.py Source/tests/test_entailment.py Source/tests/oracle.py Source/tests/run_tests.py
git commit -m "test(agent): add dynamic MockGame isolation test, entailment cases and unified test runner"
```

---

### Task 3: Sinh & Xác thực Bộ Câu đố Chuẩn tắc (Puzzles Benchmark Suite)

**Files:**
- Create: `Source/puzzles/3x3/puzzle_01.json`, `puzzle_02.json`, `puzzle_03.json`
- Create: `Source/puzzles/4x4/puzzle_01.json`, `puzzle_02.json`, `puzzle_03.json`
- Create: `Source/puzzles/5x5/puzzle_01.json` (Stress case)
- Script helper: `Source/puzzles/generate_puzzles.py` (công cụ hỗ trợ tạo và kiểm tra cấu trúc puzzle)

**Interfaces:**
- Consumes: `Source/griductive/experiments/validate_puzzle.py`
- Produces: Bộ dữ liệu benchmark đầy đủ (3x3, 4x4, 5x5) tuân thủ schema JSON của dự án

- [ ] **Step 1: Thiết kế schema và bộ sinh câu đố `Source/puzzles/generate_puzzles.py`**

Script sinh puzzle với các loại manh mối đa dạng:
- Core clues: `FACT`, `SAME`, `DIFFERENT`, `EXACTLY`, `AT_LEAST`, `AT_MOST`.
- Extension clues: `PARITY` (EVEN/ODD).
- Đảm bảo mỗi puzzle có tên nhân vật, nghề nghiệp, `solution`, `clues`, và `initially_revealed`.

- [ ] **Step 2: Sinh và ghi các file câu đố 3x3, 4x4, 5x5**

Tạo ít nhất:
- 3 puzzle cho `Source/puzzles/3x3/`
- 3 puzzle cho `Source/puzzles/4x4/`
- 1 puzzle cho `Source/puzzles/5x5/` (stress case kích thước lớn)

- [ ] **Step 3: Chạy nghiệm thu toàn bộ file puzzle qua `validate_puzzle_file`**

Run script nghiệm thu duyệt qua từng file:
`PYTHONPATH=Source python3 -c "from pathlib import Path; from griductive.experiments.validate_puzzle import validate_puzzle_file; files = sorted(Path('Source/puzzles').glob('*/*.json')); [print(f'{f}:', validate_puzzle_file(f)[1]) for f in files]; assert all(validate_puzzle_file(f)[0] for f in files)"`
Expected: 100% puzzle đạt `VALID: UNIQUE và giải thành công`.

- [ ] **Step 4: Commit**

```bash
git add Source/puzzles/
git commit -m "feat(puzzles): add verified 3x3, 4x4, and 5x5 benchmark puzzle suites"
```

---

### Task 4: Hoàn thiện Bộ Thực nghiệm Đo đạc (Experiments Runner & Exporters)

**Files:**
- Modify: `Source/griductive/experiments/runner.py`
- Modify: `Source/griductive/experiments/export.py`
- Modify: `Source/griductive/experiments/metrics.py`
- Test: `Source/tests/test_experiments.py`

**Interfaces:**
- Consumes: `Source/puzzles/**/*.json`, `LogicAgent`, `GameEngine`, `VarMap`, `Encoder`
- Produces: `Source/results/metrics.csv`, `Source/results/metrics.tex`, `Source/results/runtime_by_grid.png`

- [ ] **Step 1: Viết test cho luồng runner và export trong `Source/tests/test_experiments.py`**

Test kiểm tra:
- `run_benchmark_on_puzzle` trả về `PuzzleMetrics` có đầy đủ 6 nhóm thông số (>0 cho clauses, sat_calls, runtime).
- `export_to_csv` ghi file đúng định dạng cột CSV.
- `export_to_latex` sinh ra khối `\begin{table}` hợp lệ cho báo cáo.

- [ ] **Step 2: Hoàn thiện `plot_runtime_chart` trong `Source/griductive/experiments/export.py`**

Cài đặt hàm vẽ biểu đồ thời gian chạy gom nhóm theo kích thước bàn cờ (3x3, 4x4, 5x5). Sử dụng `matplotlib` nếu có sẵn, hoặc xuất dữ liệu text/SVG an toàn mà không làm gián đoạn chương trình.

- [ ] **Step 3: Cập nhật CLI `--cli` trong `Source/main.py` để chạy toàn bộ benchmark**

Bổ sung tham số:
- `python Source/main.py --benchmark` -> Chạy toàn bộ benchmark trong `Source/puzzles/` và tự động xuất ra `Source/results/`.

- [ ] **Step 4: Thực thi benchmark thực tế và kiểm tra output**

Run: `PYTHONPATH=Source python3 Source/main.py --benchmark`
Expected:
- Tạo ra `Source/results/metrics.csv`
- Tạo ra `Source/results/metrics.tex`
- Bảng số liệu hiển thị đầy đủ trên terminal.

- [ ] **Step 5: Commit**

```bash
git add Source/griductive/experiments/ Source/main.py Source/results/ Source/tests/test_experiments.py
git commit -m "feat(experiments): complete benchmark runner, CSV/LaTeX export, and benchmark CLI"
```

---

### Task 5: Kiểm tra Toàn diện, Đối chiếu Chân lý Oracle & Sẵn sàng Bàn giao

**Files:**
- Test verification toàn bộ hệ thống
- Tài liệu tóm tắt kết quả đo đạc

- [ ] **Step 1: Chạy đối chiếu chéo giữa Entailment và `BruteForceOracle` trên lưới nhỏ**

Kiểm tra: với mọi puzzle $N \le 4$, tập nghiệm duy nhất tìm được bởi SAT/DPLL khớp 100% với tập nghiệm vét cạn của `BruteForceOracle`.

- [ ] **Step 2: Chạy toàn bộ test suite**

Run: `PYTHONPATH=Source python3 Source/tests/run_tests.py`
Expected: 100% tests PASS.

- [ ] **Step 3: Kiểm tra trạng thái Git và ranh giới với các thành viên**

Run: `git status && git diff --stat origin/develop`
Đảm bảo:
- Không chỉnh sửa file nào trong `typst/`
- Không chỉnh sửa file nào trong `gui/` (thuộc về Hưng)
- Mọi thay đổi tập trung đúng phạm vi phụ trách của Quang: `agent/`, `experiments/`, `puzzles/`, `results/`, `tests/`.

- [ ] **Step 4: Commit và thông báo hoàn thành**

```bash
git commit --allow-empty -m "chore: complete agent and experiment benchmark milestone"
```
