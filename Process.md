# Quy trình Phát triển & Bộ Quy tắc Bắt buộc (Team Rules) – Griductive Solver

> **Tài liệu này là hiến pháp kỹ thuật của dự án Griductive Solver.**
> Mọi thành viên trong nhóm và các công cụ hỗ trợ lập trình (AI Coding Assistants) **BẮT BUỘC** phải tuân thủ 100% các quy định dưới đây. Mọi Pull Request vi phạm quy tắc sẽ bị từ chối merge.

---

## 1. Phân công Trách nhiệm & Phạm vi Module

Tuyệt đối không ai tự ý sửa đổi mã nguồn nằm ngoài module được giao nếu chưa trao đổi với người phụ trách và Team Leader.

| Thành viên | Vai trò | Phạm vi phụ trách chính (Modules) |
|:---|:---|:---|
| **Trần Văn Nguyên** | **Team Leader / Integrator** | • Thiết lập repo, định nghĩa cấu trúc thư mục, chuẩn code.<br>• Viết mã nối (glue code), `main.py`, quản lý `requirements.txt`.<br>• Review, Approve & Merge toàn bộ Pull Request.<br>• Chịu trách nhiệm viết Final Report (30 điểm). |
| **Gia Hưng** | **Frontend (GUI) Developer** | • Thiết kế giao diện (Tkinter/PyQt), vẽ lưới, render nhân vật.<br>• Quản lý tương tác người dùng, hiển thị lỗi (NOT_PROVABLE...).<br>• Code Game Engine (lưu trữ đáp án ẩn) độc lập với Agent. |
| **Nhật Tân** | **Logic & CNF Engineer** | • Viết module ánh xạ biến Boolean.<br>• Lập trình thuật toán dịch 4 loại gợi ý.<br>• Viết API đếm số lượng biến và clauses. |
| **Nhật Minh** | **DPLL Solver Engineer** | • Code thuật toán DPLL thuần (Unit propagation, Conflict detection...).<br>• Xử lý logic đệ quy, Backtracking.<br>• Gắn bộ đếm hiệu năng (Decisions, Propagations, Runtime). |
| **Ngọc Quang** | **Agent Developer & Tester** | • Code Deductive Agent kết nối với DPLL để suy luận từng bước.<br>• Chạy thực nghiệm thu thập số liệu trên lưới 3x3, 4x4, 5x5.<br>• Chịu trách nhiệm quay và dựng Video Demo. <br>• Xây dựng thuật toán dịch 2 gợi ý còn lại + 2 gợi ý mở rộng cho thuật toán CNF|

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
2. **Quyền Merge**: Tác giả PR **không được tự bấm Merge**. Chỉ Trưởng nhóm (Nguyên) mới có quyền Approve và Merge vào `develop`.
3. **Không commit rác**: Đưa các thư mục/file sau vào `.gitignore`: `__pycache__/`, `.venv/`, `env/`, `.pytest_cache/`, `*.pyc`.

---

## 3. Quy tắc Kiến trúc & Coding Standards

### 3.1. Cấu trúc thư mục
Toàn bộ code phải nằm trong các module rõ ràng, không viết tất cả vào 1 file.
```text
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

### 3.2. Tiêu chuẩn viết Code Python (PEP 8)
1. **Type Hinting**: Bắt buộc dùng Type Hints cho tham số và giá trị trả về của mọi hàm (VD: `def solve(clauses: list[list[int]]) -> bool:`).
2. **Docstrings**: Mọi class và hàm quan trọng phải có chú thích docstring mô tả đầu vào/đầu ra.
3. **Decoupling**: Các module giao tiếp bằng tham số truyền vào hàm, **tuyệt đối không** dùng biến toàn cục (global variables) để truyền dữ liệu giữa GUI và Solver.

---

## 4. Năm Quy tắc Nghiệp vụ Bất khả xâm phạm (Game Rules)

1. **Rule 1 (Phân tách Dữ liệu)**: Logic Agent **tuyệt đối không được phép** truy cập vào danh sách thẻ đang úp hoặc thuộc tính ẩn của Game Engine. Nó chỉ được nhận thông tin từ các thẻ đã lật ngửa.
2. **Rule 2 (Không Đoán Mò)**: Agent chỉ đưa ra kết luận (CRIMINAL/INNOCENT) khi cả hai trường hợp đều được thử bằng DPLL và có 1 trường hợp trả về UNSAT.
3. **Rule 3 (Định dạng CNF)**: Module CNF phải tự động gen ra clauses, tuyệt đối không hard-code (viết sẵn) mảng CNF cho từng bài test cụ thể.
4. **Rule 4 (Bắt lỗi Logic)**: Khi người chơi chơi tay, hệ thống phải phân biệt rõ ràng hai trạng thái từ chối: `NOT_PROVABLE` (chưa đủ dữ kiện) và `CONTRADICTED` (ngược với logic hiện tại).
5. **Rule 5 (Tính độc lập của DPLL)**: DPLL Solver phải được viết thuần túy, nhận đầu vào là mảng 2 chiều các số nguyên (đại diện cho CNF). Không nhúng code của giao diện hay file đọc ghi trực tiếp vào bên trong hàm DPLL.

---

## 5. Định nghĩa Hoàn thành (Definition of Done - DoD)

Một task phân công chỉ được coi là **Hoàn thành** khi thỏa mãn:
- [ ] Code chạy không văng lỗi (crash) trên môi trường ảo (virtual environment) chuẩn.
- [ ] Hàm/Class đã được gắn Type Hints và Docstrings đầy đủ.
- [ ] Không chứa file rác hay thư mục môi trường trong Git.
- [ ] Đã tạo PR lên GitHub và được Trưởng nhóm review, test tích hợp thành công.
- [ ] Báo cáo lại số liệu/thuật toán (nếu có) vào file nháp chung để Trưởng nhóm tổng hợp Final Report.