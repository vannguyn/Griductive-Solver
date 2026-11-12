# Analysis Report: Project 2 – Griductive Solver

**Môn học:** CSC14003 – Introduction to Artificial Intelligence
**Nội dung tài liệu:** Phân tích đề bài, kiến trúc, cấu trúc thư mục, kế hoạch làm việc và dàn ý báo cáo.

---

## 1. Phân tích đề bài

### 1.1. Bài toán cốt lõi

- Lưới N×N (N = 3, 4, 5). Mỗi ô là một nhân vật **Criminal** (`C_i = True`) hoặc **Innocent** (`C_i = False`).
- Mỗi thẻ có 1 clue luôn đúng, chỉ lộ ra khi thẻ được lật. Thẻ chỉ lật khi verdict được **chứng minh**.
- Quy tắc cốt lõi là **không đoán**:
  - `KB_t ⊨ C_i  ⟺  KB_t ∧ ¬C_i là UNSAT`
  - `KB_t ⊨ ¬C_i ⟺  KB_t ∧ C_i là UNSAT`
- Chuỗi xử lý toàn hệ thống:

```
Clue (JSON) → CNF → DPLL → Entailment → Agent / Game loop
```

### 1.2. Bảng điểm và mức ưu tiên

| Hạng mục | Điểm | Nội dung chính | Mức rủi ro |
|---|---|---|---|
| Game + GUI | 10 | Chơi được, flip, highlight clue, Hint / Auto Solve / Load / Restart | Trung bình (tốn thời gian) |
| Encoder CNF | 10 | Map biến, 6 clue core + ≥2 extension, evaluator ngữ nghĩa riêng | Cao (dễ sai logic) |
| DPLL | 10 | Unit propagation, conflict, branching, thống kê | Thấp |
| Logic Agent | 20 | Phân loại, trace, uniqueness check, không đọc hidden | Cao |
| Thí nghiệm | 10 | Bảng số liệu 3×3, 4×4 (5×5 là stress case) | Thấp nếu thiết kế log từ đầu |
| Báo cáo | 30 | Phân công, công thức, dẫn xuất CNF, thuật toán, kết quả | **Điểm lớn nhất, không để cuối** |
| Video | 10 | GUI 5đ + tính năng 5đ, 5–10 phút, link Google Drive | Thấp |

### 1.3. Các ràng buộc dễ mất điểm

1. **Tách vai trò:** Logic Agent chỉ nhận *public knowledge* (clue đã lật + verdict đã chứng minh). Agent không được import module `engine` và không đọc hidden solution.
2. **Không hardcode CNF** cho từng puzzle. Mọi clue phải được encode tự động.
3. **Evaluator ngữ nghĩa độc lập với encoder** (không gọi encoder), dùng để kiểm chứng chéo.
4. **Biến chính `C_i` tách biệt biến phụ (auxiliary)**, vì phải báo cáo riêng số lượng từng loại.
5. **Hint không được đọc hidden solution.**
6. **Báo cáo cả failure/timeout**, không xóa khỏi bảng kết quả.
7. Phải có **≥ 2 extension** ngoài 6 clue core.
8. Các trạng thái trả về:
   - Agent: `CRIMINAL / INNOCENT / UNKNOWN / INCONSISTENT / TIMEOUT` (tuyệt đối không nhầm `TIMEOUT` thành `UNSAT`).
   - Khi người chơi gọi sai: `NOT_PROVABLE` (chưa forced), `CONTRADICTED` (verdict ngược lại đang forced) và `ALREADY_REVEALED` (ô đã lật).
9. Puzzle hợp lệ phải có **đúng một** nghiệm, nên cần uniqueness check riêng qua CLI offline (`experiments/validate_puzzle.py`, không làm treo GUI khi Load).
10. Báo cáo số biến chính, biến phụ và số clause cho **mỗi puzzle**.
11. Có thể bị phỏng vấn thêm, vì vậy mọi thành viên phải hiểu toàn bộ hệ thống.

### 1.4. Sáu clue core cần hỗ trợ

| Clue | Ý nghĩa | Nội dung logic |
|---|---|---|
| `FACT` | Một người có trạng thái cho trước | Literal `C_i` hoặc `¬C_i` |
| `SAME` | Hai người cùng trạng thái | `C_i ↔ C_j` |
| `DIFFERENT` | Hai người khác trạng thái | `C_i ⊕ C_j` |
| `EXACTLY(k, R)` | Đúng k Criminal trong vùng R | `Σ C_i = k` |
| `AT_LEAST(k, R)` | Ít nhất k Criminal | `Σ C_i ≥ k` |
| `AT_MOST(k, R)` | Nhiều nhất k Criminal | `Σ C_i ≤ k` |

Vùng R có thể là: **hàng**, **cột**, **neighbors của một ô** (8 hướng, loại trừ chính ô đó) hoặc **danh sách ô tường minh**. Với `0 ≤ k ≤ |R|`. Clue "NO" được render thành `EXACTLY(0, R)`.

---

## 2. Kiến trúc tổng thể

```text
        ┌──────────────────┐     QFileDialog / QTimer      ┌───────────────────────┐
        │   PyQt6 GUI      │ ────────────────────────────► │  GameSession          │
        │ (gui/: View only)│ ◄──────────────────────────── │  (app/session.py)     │
        └──────────────────┘   PublicState / AutoSolveStep └───┬───────────────┬───┘
                                                               │               │
                              public state only                ▼               ▼
                     ┌─────────────────────────────────┐  ┌──────────┐   ┌───────────┐
                     │  GameEngine (engine/)           │  │LogicAgent│   │  Public   │
                     │  (hidden solution, all clues)   │◄─┼─(agent/)─┼──►│  Game     │
                     └────────────────┬────────────────┘  └────┬─────┘   │ (Protocol)│
                                      │                        │         └───────────┘
                                      ▼                        ▼
                              ┌────────────────────────────────────────┐
                              │  reasoning/ → encoding/ → sat/ (DPLL)  │
                              └────────────────────────────────────────┘
```

**Quy tắc phụ thuộc (một chiều, không vòng):**

```text
domain (types, grid, regions, clue, public_state, errors)
  ▲              ▲
  │        clues (re-export Clue, core, extensions, parser, validator)
  │              ▲
  ├────── encoding (varmap, cardinality, clue_encoders, encoder, stats)
  │         ▲                       ▲
  └──── reasoning (knowledge, kb_builder, entailment, uniqueness) ◄── sat (cnf, stats, solver, dpll)
            ▲                         ▲                                      ▲
            │                         └─────── agent (ports, trace, hint, logic_agent)
            │                                                  ▲
          engine (puzzle, loader, game_engine)                 │
            ▲                                                  │
            └─────────────── app/session.py (GameSession) ─────┘
                                      ▲
                                gui (PyQt6) / experiments / main
```

- `sat/` **không bao giờ** import `domain/`, `clues/` hoặc bất kỳ gói Griductive nào.
- `domain/` **không bao giờ** import `clues/` (`Clue` ABC nằm ngay trong `domain/clue.py`; `clues/base.py` chỉ re-export).
- `agent/` **không bao giờ** import `engine/`, chỉ giao tiếp qua `PublicGame` Protocol (`agent/ports.py`) và `PublicState` (`domain/public_state.py`).
- `reasoning/` **không bao giờ** import `agent/`; `classify` nhận `SatSolver` Protocol từ `sat/solver.py`.
- `app/session.py` (`GameSession`) tách khỏi `engine/` (do Gia Hưng giữ), giúp `GameEngine` và `LogicAgent` độc lập hai chiều với nhau.

---

## 3. Cấu trúc thư mục

```text
StudentID1_StudentID2_.../
├── Report.pdf                      # có link video Google Drive
└── Source/
    ├── main.py                     # entry point: chạy PyQt6 GUI / CLI
    ├── pytest.ini                  # pythonpath = ., testpaths = tests
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
    │   │   ├── entailment.py       # SatQuery, ClassifyOutcome, check_kb_consistent, classify()
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
    │   │   └── game_engine.py      # GameEngine (thỏa PublicGame): submit_verdict, restart, public_state
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

### Lý do tổ chức như vậy

- `sat/` hoàn toàn độc lập (chỉ nhận đối tượng `CNF(num_vars, clauses)` thuần số nguyên), nên test riêng và tái sử dụng dễ.
- Thêm extension chỉ cần sửa `clues/extensions.py` (`evaluate()`), `clues/parser.py`, `clues/validator.py`, và `encoding/clue_encoders.py`. GUI, agent, DPLL không cần chỉnh sửa.
- Mỗi folder là một tầng với trách nhiệm duy nhất, và phụ thuộc chỉ đi theo một chiều.

---

## 4. Hợp đồng giao tiếp giữa các module

```python
# domain/clue.py (re-exported by clues/base.py)
class Clue(ABC):
    id: str
    owner: Coord
    clue_type: str                                                # không có trường text; GUI tự render mô tả
    def cells(self) -> tuple[Coord, ...]: ...                     # cho GUI highlight
    def evaluate(self, assign: Mapping[Coord, bool]) -> bool: ... # semantic evaluator

# encoding/encoder.py
class Encoder:
    def __init__(self, varmap: VarMap, direct_threshold: int = 64): ...
    def encode(self, clues: Sequence[Clue]) -> tuple[CNF, EncodingStats]: ...

# sat/cnf.py, sat/solver.py & sat/dpll.py
class SatSolver(Protocol):
    def solve(self, cnf: CNF, assumptions: Sequence[int] = (), deadline: float | None = None) -> SatResult: ...

class CountingSolver:
    calls: int
    def solve(self, cnf: CNF, assumptions: Sequence[int] = (), deadline: float | None = None) -> SatResult: ...

class DPLLSolver:
    def solve(self, cnf: CNF, assumptions: Sequence[int] = (), deadline: float | None = None) -> SatResult: ...
    # SatResult: status (SatStatus: SAT | UNSAT | TIMEOUT), model: dict[int, bool] | None, stats: SolverStats

# reasoning/kb_builder.py & reasoning/entailment.py & reasoning/uniqueness.py
def build_kb_cnf(kb: PublicKnowledge, varmap: VarMap | None = None,
                 direct_threshold: int = 64) -> tuple[CNF, VarMap, EncodingStats]: ...
def check_kb_consistent(cnf_kb: CNF, solver: SatSolver, deadline: float | None = None) -> SatStatus: ...
def classify(cnf_kb: CNF, var_id: int, solver: SatSolver, deadline: float | None = None) -> ClassifyOutcome: ...
    # ClassifyOutcome(classification: Classification, queries: tuple[SatQuery, ...])
def check_uniqueness(cnf: CNF, num_primary_vars: int, solver: SatSolver,
                     deadline: float | None = None) -> UniquenessOutput: ...

# agent/ports.py & engine/game_engine.py
class PublicGame(Protocol):
    def public_state(self) -> PublicState: ...
    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome: ...

class GameEngine:  # thực thi PublicGame không import agent/
    def public_state(self) -> PublicState: ...
    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome: ...
    def restart(self) -> PublicState: ...

# agent/logic_agent.py & app/session.py
class LogicAgent:
    def __init__(self, solver: SatSolver): ...  # tự bọc solver bằng CountingSolver nếu chưa bọc
    def iter_steps(self, game: PublicGame, deadline: float | None = None) -> Iterator[AutoSolveStep]: ...
    def run(self, game: PublicGame, deadline: float | None = None) -> SolveTrace: ...

class GameSession:  # app/session.py (facade mỏng do Gia Hưng giữ)
    def load_puzzle(self, path: str | Path) -> PublicState: ...
    def restart(self) -> PublicState: ...
    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome: ...
    def hint(self) -> Hint | None: ...
    def auto_solve_steps(self, timeout_ms: int | None = None) -> Iterator[AutoSolveStep]: ...
```

### Quy ước entailment chuẩn và tối ưu tùy chọn

- **Baseline bắt buộc (theo PDF §3.4):** Đầu mỗi wave kiểm tra `check_kb_consistent(cnf_kb, solver)` 1 lần; nếu `KB` thỏa, với mỗi ô chưa lật chạy tối đa 2 truy vấn `KB ∧ ¬C_i` và `KB ∧ C_i` qua `classify()`, giữ riêng `SatStatus.TIMEOUT` thành `Classification.TIMEOUT`.
- **Tối ưu tùy chọn (nếu mở rộng sau):** Có thể giữ 1 model `M` của `KB` và chỉ thử phản chứng `KB ∧ (C_i = ¬M[i])` — tuy nhiên mọi kết quả trả về phải trùng khớp 100% với baseline 2-query.

---

## 5. Chiến lược kiểm thử

1. **Encoder ≡ Evaluator** (quan trọng nhất): với mỗi clue và mọi phép gán trên vùng liên quan, `CNF thỏa ⟺ evaluate() = True`. Với biến phụ thì kiểm tra tồn tại một phép gán biến phụ thỏa CNF (`test_encoder_vs_eval.py`).
2. **Oracle tách đúng phạm vi:**
   - Pure DPLL (`test_dpll.py`): so sánh SAT/UNSAT với brute-force trên CNF ngẫu nhiên nhỏ (**≤ 16 biến**, không áp cho CNF đầy đủ của puzzle vốn có thêm biến phụ).
   - Puzzle / Entailment (`tests/oracle.py`): với lưới nhỏ ($N \le 4$), duyệt $2^{N^2}$ phép gán **biến chính** trực tiếp qua `clue.evaluate()`.
3. Ví dụ KB trong đề `(A ∨ B) ∧ (¬A ∨ B)` làm unit test cho entailment (`test_entailment.py`): `B` là `CRIMINAL`, `A` là `UNKNOWN`.
4. Kiểm tra các ca biên: `INCONSISTENT` (KB tự mâu thuẫn), `TIMEOUT` (deadline vượt quá, không nhầm thành `UNSAT`), `ALREADY_REVEALED`, `STUCK`.
5. Mỗi puzzle trong `Source/puzzles/` phải qua CLI offline `experiments/validate_puzzle.py` (uniqueness + giải được không đoán) trước khi dùng cho thí nghiệm.
6. **`test_isolation.py`:** kết hợp kiểm tra **AST tĩnh** (`agent/` không import `engine/`, `sat/` không import `domain/`, `domain/` không import `clues/`, `reasoning/` không import `agent/`) và **dynamic `MockGame` test** (các thuộc tính ẩn ném `AssertionError` nếu bị truy cập).

---

## 6. Lựa chọn extension (≥ 2)

Ảnh minh họa trong đề cho thấy game thật dùng các clue như "Tom là 1 trong 2 neighbor criminal của Priya" (compound), "2 innocent hàng xóm của Mara nằm ở cột B" (đếm có điều kiện), "2 innocent bên phải Abel liền nhau" (connectivity).

| Extension | Độ khó | Trạng thái | Cách encode |
|---|---|---|---|
| **Parity** (số Criminal chẵn/lẻ) | Dễ | **Bắt buộc** | Cấm các tổ hợp parity sai hoặc chuỗi XOR Tseitin nếu vùng lớn |
| **Compound** (AND/OR/NOT của clue con) | Dễ–Vừa | **Bắt buộc** | Biến phụ kích hoạt / Tseitin cho từng clue con |
| **CompareCount** (vùng R1 nhiều hơn R2) | Vừa | *Tùy chọn* | Bộ đếm sequential/totalizer, dùng biến phụ (làm thêm nếu dư thời gian) |
| Region nâng cao (giao, hàng xóm chung, giữa 2 ô) | Dễ | *Tùy chọn* | Chỉ là cách sinh vùng, tái sử dụng encoder đếm |

**Chốt triển khai:** Làm chắc chắn **2 extension `PARITY` + `COMPOUND`** trước để đảm bảo chất lượng test đối chiếu chéo và báo cáo biến phụ; `COMPARE_COUNT` để mở rộng tùy chọn.

---

## 7. Kế hoạch 3 tuần (Nhóm 5 thành viên)

> **Deadline nộp bài chính thức:** `[Cập nhật ngày giờ chốt theo thông báo môn học]`

### 7.1. Phân công thống nhất (phủ 100% file, tách Evaluator khỏi Encoder)

| Thành viên | Phụ trách | Bàn giao chính |
|---|---|---|
| **Trần Văn Nguyên** (Leader) | `domain/` (`errors`, `types`, `grid`, `regions`, `clue`, `public_state`), `Source/main.py`, `requirements.txt`, `pytest.ini`, `README.md` | Hợp đồng nền tảng, ghép nối tổng thể, review PR & **Report (30đ)** |
| **Gia Hưng** | `engine/` (`puzzle`, `loader`, `game_engine`), `app/session.py`, `gui/` (**PyQt6**) | Game Engine, facade `GameSession`, Desktop GUI (`QFileDialog`, `QTimer`/`QThread`) |
| **Nhật Minh** | `sat/` (`cnf`, `stats`, `solver`, `dpll`), `reasoning/` (`knowledge`, `kb_builder`, `entailment`, `uniqueness`), `clues/` (`base`, `core`, `extensions` `PARITY`/`COMPOUND`, `evaluate()`), `tests/test_dpll.py`, `test_uniqueness.py`, `test_encoder_vs_eval.py` | DPLL + `CountingSolver`, suy diễn 2-query & uniqueness, semantic evaluator |
| **Nhật Tân** | `encoding/` (`varmap`, `cardinality`, `clue_encoders`, `encoder`, `stats`), `clues/parser.py`, `clues/validator.py` | JSON parser + validator clue, VarMap, CNF encoder + Sequential Counter fallback |
| **Ngọc Quang** | `agent/` (`ports`, `logic_agent`, `hint`, `trace`), `experiments/` (`validate_puzzle`, `runner`, `metrics`, `export`), `Source/puzzles/`, `Source/results/`, `tests/` (`oracle.py`, `test_isolation.py`, `test_entailment.py`), **Video Demo (10đ)** | Deductive Agent (`iter_steps`), Hint/Trace, offline puzzle validator, benchmark 6 chỉ số, Video + Reviewer 2 |

Cả nhóm cùng viết báo cáo, mỗi người viết phần mình làm. **Ghi % đóng góp ngay từ tuần 1 và cập nhật hằng tuần**, vì phần này quyết định điểm cá nhân (ví dụ: điểm nhóm 9.0 × 90% = 8.1).

### 7.2. Tiến độ

**Tuần 1: Nền tảng** (làm song song sau khi chốt hợp đồng biên PR A & B)

- Chốt **định dạng JSON** của puzzle/clue (có `"initially_revealed"`) trước tiên vì mọi người phụ thuộc vào nó.
- Nguyên: `domain/` (`errors`, `types`, `grid`, `regions`, `clue`, `public_state`).
- Minh: `sat/` (`cnf`, `stats`, `solver`, `dpll`), `clues/core.py` (`evaluate()`).
- Tân: `clues/parser.py`, `clues/validator.py`, `encoding/` (`varmap`, `cardinality`, `clue_encoders`, `encoder` cho 6 core clue).
- Quang: tạo 3–4 puzzle 3×3 kèm `tests/oracle.py` kiểm chứng $2^{N^2}$ phép gán biến chính.
- **Mốc:** encoder + DPLL giải được puzzle 3×3 đầy đủ clue, `test_dpll.py` và `test_encoder_vs_eval.py` xanh.

**Tuần 2: Suy diễn, Engine và PyQt6 GUI**

- Minh: `reasoning/` (`knowledge`, `kb_builder`, `entailment`, `uniqueness`) + 2 extension `PARITY`, `COMPOUND` (`evaluate()`).
- Tân: encoder cho `PARITY`, `COMPOUND` + parser/validator mở rộng + Sequential Counter fallback.
- Hưng: `engine/` (`puzzle`, `loader`, `game_engine`), `app/session.py`, và **PyQt6 GUI cơ bản** (vẽ lưới, flip, gọi verdict `NOT_PROVABLE`/`CONTRADICTED`/`ALREADY_REVEALED`).
- Quang: `agent/` (`logic_agent` với `iter_steps()`, `hint`, `trace`), `test_isolation.py`, `test_entailment.py`.
- **Mốc:** Auto Solve chạy được trên 3×3 và 4×4; GUI PyQt6 chơi tay được và khôi phục về $KB_0$ khi Restart.

**Tuần 3: Hoàn thiện & Thực nghiệm**

- Hưng: highlight ô theo clue được chọn, nối Hint, Load (`QFileDialog`), Restart, Auto Solve (`QTimer`/`QThread`) mượt không treo cửa sổ.
- Quang: hoàn thiện bộ puzzle `3×3`, `4×4`, `5×5` (qua `validate_puzzle.py`), chạy `experiments/runner.py` xuất CSV/biểu đồ giữ nguyên ca `STUCK`/`INCONSISTENT`/`TIMEOUT`.
- Cả nhóm: hoàn thiện `Report.pdf` (30đ), quay **Video Demo** (10đ), kiểm tra cài sạch trong `.venv` từ `Source/requirements.txt` và `cd Source && pytest`.
- **Mốc:** dư 2–3 ngày đệm trước deadline chính thức; kiểm tra link Google Drive bằng cửa sổ ẩn danh; nén nộp đúng cấu trúc `StudentID1_StudentID2_.../` (`Source/` + `Report.pdf`); không nộp link YouTube.

---

## 8. Dàn ý báo cáo (30 điểm)

1. **Phân công và % hoàn thành** (kèm ví dụ cách tính điểm cá nhân).
2. **Mô hình hóa:** biến `C_i`, ngữ nghĩa clue (6 core + `PARITY` + `COMPOUND`), khởi tạo $KB_0$ (`initially_revealed`), reveal protocol qua `PublicGame` / `PublicState`.
3. **Dẫn xuất CNF:**
   - Một clue nhị phân, ví dụ `C_i ⊕ C_j = (C_i ∨ C_j) ∧ (¬C_i ∨ ¬C_j)`.
   - Một clue đếm, ví dụ `EXACTLY(2, R)` với |R| = 4: liệt kê mệnh đề AT_LEAST + AT_MOST; trình bày cơ chế ước lượng clause và Sequential Counter fallback.
4. **Thuật toán:** DPLL (`CNF` + `SatStatus.TIMEOUT`), phân loại entailment 2-query chuẩn PDF §3.4 (và tối ưu model nếu cài), uniqueness check chỉ block biến chính, vòng lặp suy diễn theo Wave & Step, ghi nhận SAT calls từ `CountingSolver` của Agent.
5. **Thí nghiệm:** bảng đủ 6 chỉ số, quan sát, failure/timeout cases (`STUCK`, `INCONSISTENT`, `TIMEOUT`), hạn chế (ví dụ bùng nổ clause khi encode trực tiếp vùng lớn).
6. **Tài liệu tham khảo và Phụ lục:** cách dùng AI/LLM và các prompt.
7. Link video demo Google Drive (đặt trong `Report.pdf`).

### Sáu chỉ số cần ghi cho mỗi puzzle

| # | Chỉ số | Nguồn thu thập |
|---|---|---|
| 1 | Số biến chính / biến phụ | `EncodingStats` (`primary_vars`, `aux_vars`) |
| 2 | Số clause CNF | `EncodingStats.clauses` |
| 3 | Số SAT call | `CountingSolver.calls` của Agent (gồm cả `UNKNOWN` và `SAT(KB)` đầu wave) |
| 4 | Decisions, propagations, backtracks | `CountingSolver` tích lũy từ `SolverStats` |
| 5 | Số bước suy diễn hoặc reveal waves | `SolveTrace` (`len(steps)`, `reveal_waves`) |
| 6 | Runtime | `CountingSolver.total_runtime_ms` / `SolveTrace.total_runtime_ms` |

---

## 9. Quyết định đã chốt

1. **GUI:** Chốt **Desktop GUI thuần Python (`PyQt6`)** để chạy ổn định offline trong `Source/`, bỏ hoàn toàn Web Flask/HTTP/JS. Load puzzle qua `QFileDialog` (mặc định `Source/puzzles/`), Auto Solve duyệt `GameSession.auto_solve_steps()` qua `QTimer`/`QThread`.
2. **Định nghĩa Step vs Wave:** **Wave $k$** là tập toàn bộ các ô đang bị ép được phát hiện đồng thời tại đầu wave $k$ (sau 1 lần kiểm tra `SAT(KB)`); mỗi **Step** nộp một ô forced trong wave đó theo thứ tự `row-major` và lưu vào `TraceStep` kèm `active_clue_ids` và `sat_queries` (danh sách `TraceSatQuery`).
3. **Ánh xạ biến:** Dùng thứ tự **`row-major` (hàng-rồi-cột)** trên lưới $N \times N$ ($N \in \{3, 4, 5\}$): `var_id = row * N + col + 1` (`A1=1, B1=2, ..., A2=N+1`), cố định từ `A..` trái sang phải, `1..N` trên xuống dưới. Lưu ý Hình 1 ($4\times 5$) trong đề bài cũng đánh tên theo **hàng-rồi-cột** (`Abel A1, Bea B1, Clara C1, Derek D1, Eliza A2`) và chỉ mang tính minh họa gameplay.
4. **Định dạng JSON & $KB_0$:** Bắt buộc trường `"initially_revealed": [...]` trong schema JSON puzzle và kiểm tra ánh xạ 1-1 `owner` cho đủ $N^2$ ô; `Restart` luôn khôi phục trạng thái về $KB_0$.
5. **Cardinality encoding:** Không cắt cứng theo `|R| <= 8`. Trong `cardinality.py`, ước lượng số clause trực tiếp theo từng loại clue (`AT_MOST`: $\binom{|R|}{k+1}$, `AT_LEAST`: $\binom{|R|}{|R|-k+1}$, `EXACTLY`: tổng hai vế) và chỉ chuyển sang Sequential Counter khi vượt quá tham số `direct_threshold` (mặc định `64`).

---

## 10. Checklist trước khi nộp

- [ ] Cấu trúc thư mục khớp §5 PDF: `StudentID1_StudentID2_.../` chứa `Report.pdf` + `Source/` (`main.py`, `pytest.ini`, `README.md`, `requirements.txt`, `griductive/`, `puzzles/`, `results/`, `tests/`).
- [ ] `PyQt6` GUI đủ: lưới, tọa độ `row-major`, tên + nghề, thẻ úp/ngửa, status, Load (`QFileDialog`), Restart về $KB_0$, Hint, Auto Solve không treo UI.
- [ ] Phân biệt rõ `NOT_PROVABLE`, `CONTRADICTED`, `ALREADY_REVEALED`; verdict bị từ chối không lộ clue ẩn.
- [ ] Chọn clue → highlight các ô trong `clue.cells()` được tham chiếu.
- [ ] `test_isolation.py` xanh cả AST check và dynamic `MockGame` check (`agent` không import `engine`, Hint không đọc lời giải, `sat` thuần số nguyên).
- [ ] Mọi clue encode tự động; có `evaluate()` riêng cho 6 core + `PARITY` + `COMPOUND`; `test_encoder_vs_eval.py` xanh.
- [ ] Báo cáo số biến chính, biến phụ, clause và đầy đủ 6 chỉ số cho mỗi puzzle (kể cả `STUCK`/`INCONSISTENT`/`TIMEOUT`).
- [ ] Puzzle qua `experiments/validate_puzzle.py` offline (`UniquenessResult.UNIQUE` trên biến chính + giải được không đoán).
- [ ] Báo cáo (30đ) có phân công 5 người + % đóng góp, dẫn xuất CNF, tài liệu tham khảo, phụ lục AI.
- [ ] Video 5–10 phút (10đ), có phụ đề/thuyết minh, link Google Drive kiểm tra bằng cửa sổ ẩn danh (không dùng link YouTube).
