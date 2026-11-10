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
   - Agent: `CRIMINAL / INNOCENT / UNKNOWN / INCONSISTENT`
   - Khi người chơi gọi sai: `NOT_PROVABLE` (cả hai đều chưa forced) và `CONTRADICTED` (verdict ngược lại đang forced).
9. Puzzle hợp lệ phải có **đúng một** nghiệm, nên cần uniqueness check riêng.
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

```
        ┌──────────────┐   public state only    ┌───────────────┐
        │  GameEngine  │ ─────────────────────► │  LogicAgent   │
        │ (hidden sol, │ ◄───────────────────── │ (KB, DPLL)    │
        │  all clues)  │  verdict / hint query  └───────┬───────┘
        └──────▲───────┘                                │
               │ API (JSON)                    ┌────────▼────────┐
        ┌──────┴───────┐                       │ Encoder → CNF   │
        │     GUI      │                       │ → DPLL solver   │
        └──────────────┘                       └─────────────────┘
```

**Quy tắc phụ thuộc (một chiều, không vòng):**

```
domain  ←  clues  ←  encoding  ←  sat (DPLL)
                          ↑           ↑
                          └── reasoning (KB, entailment, uniqueness)
                                         ↑
                                       agent
                                         ↑
                                      engine  ←  gui / experiments / main
```

- `agent` **không bao giờ** import `engine`.
- `engine` dùng `reasoning` làm trọng tài (phân biệt `NOT_PROVABLE` và `CONTRADICTED`), nhưng chỉ truyền vào `PublicKnowledge`.
- `PublicState` là **biên giới duy nhất** giữa Engine và Agent, nên dễ chứng minh trong báo cáo rằng không có rò rỉ thông tin ẩn.

---

## 3. Cấu trúc thư mục

```
StudentID1_StudentID2_.../
├── Report.pdf                      # có link video Google Drive
└── Source/
    ├── main.py                     # entry point: chạy GUI / CLI
    ├── README.md                   # cách cài đặt & chạy
    ├── requirements.txt
    │
    ├── griductive/
    │   ├── domain/                 # TẦNG 0: kiểu dữ liệu thuần, không logic
    │   │   ├── types.py            # Status, VerdictResult, SolveStatus (enum)
    │   │   ├── grid.py             # Coord ("C2"), parse/format, kích thước lưới
    │   │   ├── regions.py          # row(), col(), neighbors(), explicit() → tuple[Coord]
    │   │   └── errors.py           # InvalidClueError, InvalidPuzzleError...
    │   │
    │   ├── clues/                  # TẦNG 1: định nghĩa clue + ngữ nghĩa
    │   │   ├── base.py             # class Clue (id, owner, cells(), evaluate())
    │   │   ├── core.py             # Fact, Same, Different, Exactly, AtLeast, AtMost
    │   │   ├── extensions.py       # Parity, CompareCount, Compound... (≥2 loại)
    │   │   ├── validator.py        # kiểm tra k, region, ô tham chiếu
    │   │   └── parser.py           # dict/JSON → Clue (registry theo "type")
    │   │
    │   ├── sat/                    # TẦNG 1: SAT thuần, không biết gì về Griductive
    │   │   ├── cnf.py              # Literal=int, Clause, CNF, to_dimacs()
    │   │   ├── dpll.py             # DPLLSolver.solve(cnf, assumptions) → SatResult
    │   │   └── stats.py            # SolverStats: decisions, propagations, backtracks, time
    │   │
    │   ├── encoding/               # TẦNG 2: Clue → CNF
    │   │   ├── varmap.py           # VarMap: Coord ↔ var id; cấp phát biến phụ riêng
    │   │   ├── cardinality.py      # exactly/at_least/at_most (trực tiếp + sequential counter)
    │   │   ├── clue_encoders.py    # encoder cho từng clue (dispatch theo type)
    │   │   ├── encoder.py          # Encoder.encode(clues) → CNF + EncodingStats
    │   │   └── stats.py            # #primary vars, #aux vars, #clauses
    │   │
    │   ├── reasoning/              # TẦNG 3: suy diễn trên KB
    │   │   ├── knowledge.py        # PublicKnowledge (revealed clues + proved verdicts)
    │   │   ├── kb_builder.py       # PublicKnowledge → CNF (unit clauses cho verdict)
    │   │   ├── entailment.py       # classify(kb, cell) → CRIMINAL/INNOCENT/UNKNOWN/INCONSISTENT
    │   │   └── uniqueness.py       # đếm nghiệm (tối đa 2) bằng blocking clause
    │   │
    │   ├── agent/                  # TẦNG 4
    │   │   ├── logic_agent.py      # vòng lặp suy diễn; hỏi Engine clue mới
    │   │   ├── hint.py             # chọn ô forced + clue liên quan
    │   │   └── trace.py            # TraceStep: step, active clues, SAT queries, verdict, clue mới
    │   │
    │   ├── engine/                 # TẦNG 5: chỉ Engine được biết lời giải
    │   │   ├── puzzle.py           # Puzzle: lưới, solution ẩn, mọi clue
    │   │   ├── loader.py           # đọc JSON → Puzzle (+ kiểm tra tính nhất quán)
    │   │   ├── game_engine.py      # submit_verdict, reveal, restart, get_public_state
    │   │   └── public_state.py     # PublicState (chỉ phần được phép lộ ra)
    │   │
    │   ├── gui/                    # TẦNG 6
    │   │   ├── app.py              # khởi tạo GUI
    │   │   ├── board_view.py       # vẽ lưới, card flip, tọa độ
    │   │   ├── clue_panel.py       # chọn clue → highlight ô liên quan
    │   │   ├── controls.py         # Load / Restart / Hint / Auto Solve
    │   │   └── assets/             # avatar, CSS/ảnh
    │   │
    │   └── experiments/
    │       ├── runner.py           # chạy toàn bộ puzzle, có timeout
    │       ├── metrics.py          # gom số liệu thành bảng
    │       └── export.py           # xuất CSV/LaTeX/biểu đồ
    │
    ├── puzzles/
    │   ├── 3x3/ p01.json ...
    │   ├── 4x4/ ...
    │   └── 5x5/ ...                # stress case
    ├── results/                    # CSV, biểu đồ, log trace (output của experiments)
    └── tests/
        ├── test_dpll.py            # so với brute force
        ├── test_encoder_vs_eval.py # CNF ≡ evaluator trên mọi phép gán
        ├── test_entailment.py      # ví dụ KB trong đề (A, B)
        ├── test_uniqueness.py
        └── test_isolation.py       # agent không import engine
```

### Lý do tổ chức như vậy

- `sat/` hoàn toàn độc lập (chỉ nhận danh sách mệnh đề số nguyên), nên test riêng và tái sử dụng dễ.
- Thêm extension chỉ cần sửa 3 chỗ: `clues/extensions.py` (kèm `evaluate`), `encoding/clue_encoders.py`, `clues/parser.py`. GUI, agent, DPLL không cần chỉnh sửa.
- Mỗi folder là một tầng với trách nhiệm duy nhất, và phụ thuộc chỉ đi theo một chiều.

---

## 4. Hợp đồng giao tiếp giữa các module

```python
# clues/base.py
class Clue:
    id: str
    def cells(self) -> tuple[Coord, ...]: ...                    # cho GUI highlight
    def evaluate(self, assign: dict[Coord, bool]) -> bool: ...   # semantic evaluator

# encoding/encoder.py
class Encoder:
    def __init__(self, varmap: VarMap): ...
    def encode(self, clues: list[Clue]) -> CNF: ...              # + .stats (primary/aux/clauses)

# sat/dpll.py
class DPLLSolver:
    def solve(self, cnf: CNF, assumptions: list[int] = ()) -> SatResult
    # SatResult: sat: bool, model: dict[int, bool] | None, stats: SolverStats

# reasoning/entailment.py
def classify(cnf_kb: CNF, var: int, solver) -> Classification    # + số SAT call

# engine/game_engine.py
class GameEngine:
    def public_state(self) -> PublicState
    def submit_verdict(self, cell, status) -> VerdictResult      # ACCEPTED | NOT_PROVABLE | CONTRADICTED
    def reveal(self, cell) -> Clue                               # chỉ gọi sau khi verdict được chấp nhận

# agent/logic_agent.py
class LogicAgent:
    def next_forced(self, pk: PublicKnowledge) -> tuple[Coord, Status] | None
    def run(self, engine) -> Trace                               # Auto Solve
```

### Mẹo tối ưu số SAT call (nên ghi vào báo cáo)

Giải `KB` một lần để có model `M`. Với mỗi ô `i`, chỉ cần kiểm tra `KB ∧ (C_i = ¬M[i])`:

- SAT → ô `i` là UNKNOWN.
- UNSAT → ô `i` bị ép theo `M[i]`.

Cách này chỉ tốn 1 truy vấn mỗi ô thay vì 2, và mỗi counter-model tìm được có thể loại ngay các ô UNKNOWN khác. Kết quả vẫn đúng theo định nghĩa trong đề.

---

## 5. Chiến lược kiểm thử

1. **Encoder ≡ Evaluator** (quan trọng nhất): với mỗi clue và mọi phép gán trên vùng liên quan, `CNF thỏa ⟺ evaluate() = True`. Với biến phụ thì kiểm tra tồn tại một phép gán biến phụ thỏa CNF.
2. **DPLL vs brute force** trên CNF ngẫu nhiên nhỏ (≤ 12 biến).
3. Ví dụ KB trong đề `(A ∨ B) ∧ (¬A ∨ B)` làm unit test cho entailment: B là CRIMINAL, A là UNKNOWN.
4. Mỗi puzzle trong `puzzles/` phải qua **uniqueness check** trước khi dùng cho thí nghiệm.
5. `test_isolation.py` kiểm tra `agent/` không import `engine/`.
6. Test trường hợp `INCONSISTENT` (KB tự mâu thuẫn).

---

## 6. Lựa chọn extension (≥ 2)

Ảnh minh họa trong đề cho thấy game thật dùng các clue như "Tom là 1 trong 2 neighbor criminal của Priya" (compound), "2 innocent hàng xóm của Mara nằm ở cột B" (đếm có điều kiện), "2 innocent bên phải Abel liền nhau" (connectivity).

| Extension | Độ khó | Cách encode |
|---|---|---|
| **Parity** (số Criminal chẵn/lẻ) | Dễ | Cấm các tổ hợp có parity sai (trực tiếp, vùng ≤ 8 ô) |
| **Compound** (AND/OR/NOT của clue con) | Dễ–Vừa | Tseitin hoặc biến phụ cho từng clue con |
| **CompareCount** (vùng R1 nhiều hơn R2) | Vừa | Bộ đếm sequential/totalizer, dùng biến phụ |
| Region nâng cao (giao, hàng xóm chung, giữa 2 ô) | Dễ | Chỉ là cách sinh vùng, tái sử dụng encoder đếm |

**Đề xuất:** Parity + Compound + CompareCount. Compound và CompareCount cho báo cáo nhiều nội dung hay (biến phụ).

**Lưu ý:** encode trực tiếp CompareCount với hai vùng 8 ô sẽ bùng nổ (2^16 tổ hợp), nên dùng bộ đếm.

---

## 7. Kế hoạch 3 tuần (giả định nhóm 3–4 người)

### 7.1. Phân công gợi ý

| Vai trò | Phụ trách | Bàn giao chính |
|---|---|---|
| **A: SAT core** | `sat/`, `reasoning/`, test DPLL | DPLL, entailment, uniqueness |
| **B: Logic modeling** | `clues/`, `encoding/`, extension | 6 clue + extensions, encoder, test encoder ≡ evaluator |
| **C: Engine + Agent** | `engine/`, `agent/`, `experiments/` | Game loop, trace, hint, runner |
| **D: GUI + Content** | `gui/`, `puzzles/`, video | Giao diện, bộ puzzle, video demo |

Cả nhóm cùng viết báo cáo, mỗi người viết phần mình làm. **Ghi % đóng góp ngay từ tuần 1 và cập nhật hằng tuần**, vì phần này quyết định điểm cá nhân (ví dụ: điểm nhóm 9.0 × 90% = 8.1).

### 7.2. Tiến độ

**Tuần 1: Nền tảng** (làm song song, thống nhất hợp đồng ở mục 4 ngay ngày đầu)

- Chốt **định dạng JSON** của puzzle/clue trước tiên vì mọi người phụ thuộc vào nó.
- A: `cnf.py`, `dpll.py`, `stats.py`.
- B: `domain/`, `clues/core.py`, `varmap`, `cardinality`, `clue_encoders` cho 6 clue.
- D: tự tạo 3–4 puzzle 3×3 và xác nhận nghiệm duy nhất bằng brute force.
- **Mốc:** encoder + DPLL giải được puzzle 3×3 đầy đủ clue, test encoder ≡ evaluator xanh.

**Tuần 2: Suy diễn và Game**

- A: `entailment`, `uniqueness`.
- C: `engine`, `public_state`, `logic_agent`, `trace`.
- B: extension (≥ 2).
- D: GUI cơ bản (lưới, flip, gọi verdict).
- **Mốc:** Auto Solve chạy được trên 3×3 và 4×4 bằng CLI; GUI chơi tay được; có `NOT_PROVABLE` và `CONTRADICTED`.

**Tuần 3: Hoàn thiện**

- D: highlight clue, Hint, Load/Restart/Auto Solve.
- C: `experiments` (3×3, 4×4, 5×5, ghi cả failure/timeout).
- Cả nhóm: viết báo cáo, quay video, kiểm tra README và `requirements.txt` chạy sạch trên máy mới.
- **Mốc:** dư 2–3 ngày đệm; kiểm tra link Google Drive bằng cửa sổ ẩn danh; nén nộp bài đúng tên `StudentID1_StudentID2_...`; không nộp link YouTube.

---

## 8. Dàn ý báo cáo (30 điểm)

1. **Phân công và % hoàn thành** (kèm ví dụ cách tính điểm cá nhân).
2. **Mô hình hóa:** biến `C_i`, ngữ nghĩa clue, KB, reveal protocol.
3. **Dẫn xuất CNF:**
   - Một clue nhị phân, ví dụ `C_i ⊕ C_j = (C_i ∨ C_j) ∧ (¬C_i ∨ ¬C_j)`.
   - Một clue đếm, ví dụ `EXACTLY(2, R)` với |R| = 4: liệt kê mệnh đề AT_LEAST + AT_MOST.
4. **Thuật toán:** DPLL, phân loại entailment (kèm tối ưu 1 query/ô), uniqueness check, vòng lặp suy diễn (pseudo-code).
5. **Thí nghiệm:** bảng đủ 6 chỉ số, quan sát, failure case, hạn chế (ví dụ bùng nổ clause khi encode trực tiếp vùng lớn).
6. **Tài liệu tham khảo và Phụ lục:** cách dùng AI/LLM và các prompt.
7. Link video demo Google Drive (đặt trong Report.pdf).

### Sáu chỉ số cần ghi cho mỗi puzzle

| # | Chỉ số |
|---|---|
| 1 | Số biến chính / biến phụ |
| 2 | Số clause CNF |
| 3 | Số SAT call |
| 4 | Decisions, propagations, backtracks |
| 5 | Số bước suy diễn hoặc reveal waves |
| 6 | Runtime |

---

## 9. Quyết định cần chốt sớm

1. **GUI:** đề xuất web (Flask + HTML/CSS/JS), vì hiệu ứng lật thẻ và highlight bằng CSS dễ làm, engine trả JSON qua API. Tkinter vẫn đạt yêu cầu nhưng lật thẻ khó hơn.
2. **Một bước = một verdict hay một "wave"?** Đề xuất: mỗi bước chọn ô forced đầu tiên theo row-major, đồng thời ghi lại "wave" (tập tất cả ô forced tại thời điểm đó) để báo cáo số reveal waves.
3. **Ánh xạ biến:** `var_id = row_major_index + 1`, cố định và có tài liệu rõ. Đề nói nhân vật được sắp theo tên alphabet; trong ảnh minh họa thứ tự này trùng với thứ tự cột-rồi-hàng của lưới (Abel A1, Bea B1, Clara C1, Derek D1, Eliza A2...), nên nên xác nhận lại với giảng viên nếu có chỗ chưa rõ.
4. **Định dạng JSON:** chốt schema puzzle/clue ngay ngày đầu.
5. **Cardinality encoding:** dùng encode trực tiếp cho vùng nhỏ (≤ 8 ô), sequential counter/totalizer cho CompareCount và vùng lớn.

---

## 10. Checklist trước khi nộp

- [ ] GUI có đủ: lưới, tọa độ, tên + nghề, thẻ úp/ngửa, status, Load/Restart/Hint/Auto Solve.
- [ ] Phân biệt rõ `NOT_PROVABLE` và `CONTRADICTED`; verdict bị từ chối không lộ clue ẩn.
- [ ] Chọn clue → highlight các ô được tham chiếu.
- [ ] Agent không import engine, Hint không đọc lời giải.
- [ ] Mọi clue encode tự động; có evaluator riêng cho 6 clue core.
- [ ] Báo cáo số biến chính, biến phụ, clause cho mỗi puzzle.
- [ ] Có uniqueness check cho toàn bộ clue set.
- [ ] ≥ 2 extension, có test và ví dụ trong báo cáo.
- [ ] Bảng thí nghiệm có cả failure/timeout.
- [ ] Báo cáo có phân công + % đóng góp, tài liệu tham khảo, phụ lục AI.
- [ ] Video 5–10 phút, có phụ đề/thuyết minh, link Google Drive kiểm tra bằng cửa sổ ẩn danh.
- [ ] Nộp đúng cấu trúc: `StudentID1_StudentID2_...` / `Source/` (main.py, README.md, requirements.txt) + `Report.pdf`.
