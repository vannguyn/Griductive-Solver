# Quy trình Phát triển & Bộ Quy tắc Bắt buộc (Team Rules) – Griductive Solver

> **Tài liệu này là hiến pháp kỹ thuật của dự án Griductive Solver.**
> Mọi thành viên trong nhóm và các công cụ hỗ trợ lập trình (AI Coding Assistants) **BẮT BUỘC** phải tuân thủ 100% các quy định dưới đây. Mọi Pull Request vi phạm quy tắc sẽ bị từ chối merge.
>
> **Deadline nộp bài chính thức:** `[Cập nhật ngày giờ chốt theo thông báo môn học]`

---

## 1. Phân công Trách nhiệm & Phạm vi Module

Tuyệt đối không ai tự ý sửa đổi mã nguồn nằm ngoài module được giao nếu chưa trao đổi với người phụ trách và Team Leader.

| Thành viên | Vai trò | Phạm vi phụ trách chính (Modules) |
|:---|:---|:---|
| **Trần Văn Nguyên** | **Team Leader / Domain & Integrator** | • Phụ trách `domain/` (`errors.py`, `types.py`, `grid.py`, `regions.py`, `clue.py`, `public_state.py`), `Source/main.py`, `Source/requirements.txt`, `Source/pytest.ini`, `Source/README.md`.<br>• Thiết lập repo, kiểm soát kiến trúc DAG, ghép nối tổng thể & merge PR.<br>• Chủ biên **Final Report (30 điểm)**. |
| **Gia Hưng** | **Game Engine, App Session & PyQt6 GUI** | • Phụ trách `engine/` (`puzzle.py`, `loader.py`, `game_engine.py` thực thi `PublicGame` không import `agent`).<br>• Phụ trách `app/session.py` (`GameSession` mỏng bọc `GameEngine` + `LogicAgent`).<br>• Thiết kế Desktop GUI bằng **`PyQt6`** (`gui/`): vẽ lưới, flip, highlight ô theo clue, Load/Restart/Hint/Auto Solve. |
| **Nhật Minh** | **SAT, Reasoning & Clue Semantics** | • Phụ trách `sat/` (`cnf.py`, `stats.py`, `solver.py`, `dpll.py`).<br>• Phụ trách `reasoning/` (`knowledge.py`, `kb_builder.py`, `entailment.py`, `uniqueness.py`).<br>• Phụ trách ngữ nghĩa clue trong `clues/` (`base.py`, `core.py`, `extensions.py` với `PARITY` + `COMPOUND`, `evaluate()`).<br>• Viết test `Source/tests/` (`test_dpll.py`, `test_uniqueness.py`, `test_encoder_vs_eval.py`). |
| **Nhật Tân** | **CNF Encoding & Clue Parsing/Validation** | • Phụ trách `encoding/` (`varmap.py`, `cardinality.py` + Sequential Counter fallback, `clue_encoders.py`, `encoder.py`, `stats.py`).<br>• Phụ trách `clues/parser.py`, `clues/validator.py` (tách hoàn toàn khỏi `evaluate()` của Minh để `test_encoder_vs_eval.py` đối chiếu độc lập). |
| **Ngọc Quang** | **Agent, Experiments & Reviewer 2** | • Phụ trách `agent/` (`ports.py`, `logic_agent.py`, `hint.py`, `trace.py`).<br>• Phụ trách `experiments/` (`runner.py`, `metrics.py`, `export.py`, `validate_puzzle.py`), `Source/puzzles/` (`3x3`, `4x4`, `5x5`), `Source/results/`.<br>• Viết `Source/tests/` (`oracle.py`, `test_isolation.py`, `test_entailment.py`), quay dựng **Video Demo (10 điểm)** và review chéo PR của Leader. |

---

## 2. Quy trình Quản lý Mã nguồn (Git Workflow)

### 2.1. Chiến lược Phân nhánh (Gitflow)
- **`main`**: Nhánh sản phẩm ổn định cuối cùng để nộp bài. **TUYỆT ĐỐI KHÔNG** push code trực tiếp lên đây.
- **`develop`**: Nhánh tích hợp chính của nhóm. Mọi tính năng đều tách nhánh từ đây và tạo Pull Request (PR) quay về đây.
- **Nhánh công việc (Working Branches)**: Phải đặt tên theo cú pháp:
  * Tính năng mới: `feature/<ten-module>-<mo-ta>` (VD: `feature/gui-draw-grid`, `feature/cnf-exactly-clue`)
  * Sửa lỗi: `fix/<ten-module>-<mo-ta>` (VD: `fix/dpll-infinite-loop`)
  * Cấu hình / Tài liệu: `docs/<mo-ta>` hoặc `chore/<mo-ta>`

### 2.2. Quy trình 5 bước làm việc
```bash
# Bước 1: Lấy code mới nhất từ nhánh tích hợp về máy
git fetch origin
git switch develop
git pull origin develop

# Bước 2: Tạo nhánh riêng cho công việc của mình
git switch -c feature/cnf-exactly-clue

# Bước 3: Code, chạy thử nghiệm ở máy cá nhân (Local)
# Bước 4: Commit theo chuẩn Conventional Commits (xem mục 2.3)
# Bước 5: Push lên GitHub và tạo Pull Request vào nhánh `develop`
git push -u origin feature/cnf-exactly-clue
```

### 2.3. Quy chuẩn Commit Message
Mọi commit message **BẮT BUỘC** tuân theo định dạng:
`<type>(<scope>): <mô tả ngắn gọn, viết thường đầu câu>`

- **`<type>` hợp lệ**:
  * `feat`: Thêm hàm/tính năng mới.
  * `fix`: Sửa lỗi logic, lỗi crash.
  * `docs`: Cập nhật README, báo cáo.
  * `refactor`: Viết lại code cho gọn/sạch hơn.
- **Ví dụ ĐÚNG**:
  * `feat(dpll): implement unit propagation logic`
  * `fix(gui): resolve card flip animation lag`
- **Ví dụ SAI**: `update code`, `fix bug`, `xong phan cnf`.

### 2.4. Quy tắc Pull Request (PR) & Code Review
1. **Một PR - Một Nhiệm vụ**: Không gộp chung việc sửa GUI và viết thuật toán DPLL vào cùng 1 PR.
2. **Quyền Merge & Review chéo**: Tác giả PR **không được tự bấm Merge**. PR của thành viên do Trưởng nhóm (Nguyên) duyệt và merge vào `develop`; PR của chính Trưởng nhóm phải có ít nhất 1 thành viên khác (Quang hoặc Hưng) review chéo trước khi merge.
3. **Không commit rác**: Đưa các thư mục/file sau vào `.gitignore`: `__pycache__/`, `.venv/`, `env/`, `.pytest_cache/`, `*.pyc`.

---

## 3. Quy tắc Kiến trúc & Coding Standards

### 3.1. Cấu trúc thư mục
Toàn bộ code phải nằm trong các module rõ ràng, không viết tất cả vào 1 file.
```text
StudentID1_StudentID2_.../
├── Report.pdf                      # có link video Google Drive
└── Source/
    ├── main.py                     # entry point: chạy PyQt6 GUI / CLI
    ├── pytest.ini                  # cấu hình pythonpath = . và testpaths = tests
    ├── README.md                   # cách cài đặt & chạy
    ├── requirements.txt            # PyQt6>=6.6, pytest>=8.0
    │
    ├── griductive/
    │   ├── domain/                 # TẦNG 0: kiểu dữ liệu thuần & biên công khai
    │   │   ├── types.py            # Status, Classification, VerdictResult, SolveStatus, UniquenessResult, RegionKind
    │   │   ├── grid.py             # Coord ("C2"), parse/format, kích thước lưới (row-major)
    │   │   ├── regions.py          # RegionSpec, resolve_region() → tuple[Coord, ...]
    │   │   ├── clue.py             # Clue ABC (id, owner, clue_type, cells(), evaluate())
    │   │   ├── public_state.py     # PublicCell, PublicState, VerdictOutcome
    │   │   └── errors.py           # GriductiveError, InvalidCoordError, InvalidClueError, InvalidPuzzleError
    │   │
    │   ├── clues/                  # TẦNG 1: cài đặt clue + ngữ nghĩa + parser
    │   │   ├── base.py             # re-export Clue từ domain.clue
    │   │   ├── core.py             # Fact, Same, Different, Exactly, AtLeast, AtMost
    │   │   ├── extensions.py       # Parity, Compound (bắt buộc ≥2; CompareCount tùy chọn)
    │   │   ├── validator.py        # kiểm tra k, region, ô tham chiếu
    │   │   └── parser.py           # dict/JSON → Clue (registry theo "type")
    │   │
    │   ├── sat/                    # TẦNG 1: SAT thuần, không biết gì về Griductive
    │   │   ├── cnf.py              # Literal=int, Clause, SatStatus, CNF(num_vars, clauses), SatResult
    │   │   ├── stats.py            # SolverStats: decisions, propagations, backtracks, runtime_ms
    │   │   ├── solver.py           # SatSolver Protocol + CountingSolver wrapper
    │   │   └── dpll.py             # DPLLSolver.solve(cnf, assumptions, deadline) → SatResult
    │   │
    │   ├── encoding/               # TẦNG 2: Clue → CNF
    │   │   ├── varmap.py           # VarMap: Coord ↔ var id; cấp phát biến phụ riêng
    │   │   ├── cardinality.py      # exactly/at_least/at_most (ước lượng clause ≤ threshold + sequential counter)
    │   │   ├── clue_encoders.py    # encoder cho từng clue (dispatch theo type)
    │   │   ├── encoder.py          # Encoder.encode(clues) → tuple[CNF, EncodingStats]
    │   │   └── stats.py            # EncodingStats: primary_vars, aux_vars, clauses
    │   │
    │   ├── reasoning/              # TẦNG 3: suy diễn trên KB
    │   │   ├── knowledge.py        # PublicKnowledge (revealed clues + proved verdicts)
    │   │   ├── kb_builder.py       # build_kb_cnf(kb, varmap, direct_threshold) → (CNF, VarMap, EncodingStats)
    │   │   ├── entailment.py       # SatQuery, ClassifyOutcome, check_kb_consistent, classify(cnf_kb, var_id, solver, deadline)
    │   │   └── uniqueness.py       # UniquenessOutput, check_uniqueness() bằng blocking clause biến chính
    │   │
    │   ├── agent/                  # TẦNG 4
    │   │   ├── ports.py            # PublicGame Protocol (public_state, submit_verdict)
    │   │   ├── logic_agent.py      # AutoSolveStep, LogicAgent (bọc CountingSolver, iter_steps, run)
    │   │   ├── hint.py             # Hint, suggest_hint() chọn ô forced + clue liên quan
    │   │   └── trace.py            # TraceSatQuery, TraceStep, SolveTrace
    │   │
    │   ├── engine/                 # TẦNG 5: chỉ Engine được biết lời giải ẩn
    │   │   ├── puzzle.py           # Puzzle: lưới, solution ẩn, initially_revealed, mọi clue
    │   │   ├── loader.py           # đọc JSON → Puzzle (validate schema + khớp solution nhanh)
    │   │   └── game_engine.py      # GameEngine (thỏa PublicGame không import agent): submit_verdict, restart, public_state
    │   │
    │   ├── app/                    # TẦNG 6: facade điều phối mỏng (chủ duy nhất: Gia Hưng)
    │   │   └── session.py          # GameSession (load_puzzle, restart, submit_verdict, hint, auto_solve_steps)
    │   │
    │   ├── gui/                    # TẦNG 7: Desktop PyQt6
    │   │   ├── app.py              # khởi tạo PyQt6 app
    │   │   ├── board_view.py       # vẽ lưới, card flip, tọa độ
    │   │   ├── clue_panel.py       # chọn clue → highlight ô liên quan
    │   │   ├── controls.py         # Load (QFileDialog) / Restart / Hint / Auto Solve (QTimer/QThread)
    │   │   └── assets/             # avatar, QSS/ảnh
    │   │
    │   └── experiments/
    │       ├── validate_puzzle.py  # CLI offline kiểm tra uniqueness + giải được không đoán
    │       ├── runner.py           # chạy toàn bộ puzzle, có timeout
    │       ├── metrics.py          # gom 6 nhóm số liệu thành bảng
    │       └── export.py           # xuất CSV/LaTeX/biểu đồ
    │
    ├── puzzles/
    │   ├── 3x3/ p01.json ...
    │   ├── 4x4/ ...
    │   └── 5x5/ ...                # stress case
    ├── results/                    # CSV, biểu đồ, log trace (output của experiments)
    └── tests/
        ├── oracle.py               # brute-force 2^(N^2) phép gán biến chính qua clue.evaluate()
        ├── test_dpll.py            # so với brute force CNF ≤ 16 biến
        ├── test_encoder_vs_eval.py # CNF ≡ evaluator trên mọi phép gán
        ├── test_entailment.py      # ví dụ KB trong đề (A, B) + INCONSISTENT + TIMEOUT
        ├── test_uniqueness.py      # UNIQUE / MULTIPLE / UNSAT / TIMEOUT
        └── test_isolation.py       # kiểm tra AST + dynamic MockGame cô lập agent khỏi engine
```

### 3.2. Tiêu chuẩn viết Code Python (PEP 8)
1. **Type Hinting**: Bắt buộc dùng Type Hints cho tham số và giá trị trả về của mọi hàm (VD: `def solve(self, cnf: CNF, assumptions: Sequence[int] = (), deadline: float | None = None) -> SatResult:`).
2. **Docstrings**: Mọi class và hàm quan trọng phải có chú thích docstring mô tả đầu vào/đầu ra.
3. **Decoupling**: Các module giao tiếp bằng tham số truyền vào hàm và các lớp dữ liệu chuẩn hóa, **tuyệt đối không** dùng biến toàn cục (global variables) để truyền dữ liệu giữa GUI và Solver.

---

## 4. Năm Quy tắc Nghiệp vụ Bất khả xâm phạm (Game Rules)

1. **Rule 1 (Phân tách Dữ liệu)**: Logic Agent **tuyệt đối không được phép** import `engine` hay truy cập vào danh sách thẻ đang úp / `solution` ẩn. Nó chỉ giao tiếp qua `PublicGame` Protocol và `PublicState`.
2. **Rule 2 (Không Đoán Mò)**: Agent chỉ đưa ra kết luận (`CRIMINAL`/`INNOCENT`) dựa trên chuẩn **2 truy vấn entailment theo đề §3.4** (`KB_t ∧ ¬C_i` là `UNSAT` cho `CRIMINAL`; `KB_t ∧ C_i` là `UNSAT` cho `INNOCENT`, kiểm tra `SAT(KB_t)` ở đầu mỗi wave và giữ nhánh `TIMEOUT` tách khỏi `UNSAT`). Tối ưu dùng model `M` là tùy chọn nâng cao và phải cho kết quả tương đương 100%.
3. **Rule 3 (Định dạng CNF)**: Module CNF phải tự động gen ra clauses, tuyệt đối không hard-code (viết sẵn) mảng CNF cho từng bài test cụ thể.
4. **Rule 4 (Bắt lỗi Logic)**: Khi người chơi chơi tay, hệ thống phải phân biệt rõ các trạng thái từ chối: `NOT_PROVABLE` (chưa đủ dữ kiện), `CONTRADICTED` (ngược với logic bị ép hiện tại) và `ALREADY_REVEALED` (ô đã lật trước đó).
5. **Rule 5 (Tính độc lập của DPLL)**: DPLL Solver phải được viết thuần túy số nguyên, nhận đối tượng `CNF(num_vars: int, clauses: list[list[int]])` (kèm `assumptions` và `deadline`) để trả complete assignment trên `1..num_vars` khi `SAT` hoặc `SatStatus.TIMEOUT` khi quá giờ. Không import `domain`, GUI hay đọc/ghi file bên trong `sat/`.

---

## 5. Định nghĩa Hoàn thành (Definition of Done - DoD)

Một task phân công chỉ được coi là **Hoàn thành** khi thỏa mãn:
- [ ] Code và unit test chạy sạch bằng `pytest` trong môi trường ảo (`.venv`) đã cài từ `Source/requirements.txt`.
- [ ] Hàm/Class đã được gắn Type Hints và Docstrings đầy đủ.
- [ ] Không chứa file rác hay thư mục môi trường trong Git.
- [ ] Đã tạo PR lên GitHub và được review chéo (Leader review PR thành viên; PR của Leader có thành viên khác review chéo), test tích hợp thành công trước khi merge vào `develop`.
- [ ] Báo cáo lại số liệu/thuật toán (nếu có) vào file nháp chung để Trưởng nhóm tổng hợp Final Report.