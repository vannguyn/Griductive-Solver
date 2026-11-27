#import "../components.typ": styled_table

#pagebreak()

= Tài liệu tham khảo

+ Davis, M., Logemann, G., & Loveland, D. (1962). *A Machine Program for Theorem-Proving*. Communications of the ACM, 5(7), 394–397.
+ Tseitin, G. S. (1983). *On the Complexity of Derivation in Propositional Calculus*. Automation of Reasoning, Springer, 466–483.
+ Sinz, C. (2005). *Towards an Optimal CNF Encoding of Boolean Cardinality Constraints*. Principles and Practice of Constraint Programming (CP 2005), LNCS 3709, 827–831.
+ Griductive Official Game & Rules: https://griductive.com/
+ Riverbank Computing. *PyQt6 Reference Guide*: https://www.riverbankcomputing.com/static/Docs/PyQt6/

= Sử dụng công cụ AI

Nhóm sử dụng công cụ AI như một trợ lý trao đổi ý tưởng, rà soát logic, gợi ý test và cải thiện cách trình bày. AI không được xem là nguồn sự thật cuối cùng: mọi thay đổi quan trọng đều được chạy test, đối chiếu evaluator/CNF hoặc kiểm tra trực tiếp trên puzzle.

#styled_table(
  (1.25fr, 1.2fr, 3.0fr),
  ([Công cụ], [Nhà cung cấp], [Mục đích]),
  (
    ([Codex], [OpenAI], [Rà soát source, sửa lỗi, viết test và audit yêu cầu]),
    ([ChatGPT], [OpenAI], [Trao đổi khái niệm, diễn đạt report và checklist]),
    ([Claude], [Anthropic], [Giải thích thuật toán và tổ chức module]),
    ([Antigravity], [Google], [Hỗ trợ code và thử nghiệm]),
  ),
  caption: [Công cụ AI được sử dụng trong quá trình phát triển],
)

*Một số prompt tiêu biểu*

- “`/receiving-code-review` đóng vai là người kiểm dịch khởi tạo dự án (senior engineer). Xem xét đề bài `AI - Project 2.pdf` và các tài liệu phân tích của trưởng nhóm `Analysis_Report.md`, `Process.md`, `Workflow.md`. Hãy nhận xét tính đúng đắn của các yếu tố sau: [Review summary: Griductive Solver docs — 1. Retractions (R1–R8: N×N grid, 2-query baseline, desktop PyQt6, ≥2 extensions, lightweight process); 2. Real defects (A–G: `CountingSolver` wrapper, `iter_steps()` + `QTimer`, unified contracts, `app/session.py` layering, evaluator independence, deadline, oracle scope); 3. Keep; 4. Observations on `Audit_Response_TeamLead.md`; 5. Order of work]”
- “Chọn hướng: chỉ dựng hợp đồng và chữ ký tại các biên (≥2 người dùng), thân hàm `raise NotImplementedError`. Chia 2 PR code (A: `domain`, `sat`, `clues/base`; B: chữ ký `encoding`, `reasoning`, `agent`, `engine`, `app`) và 1 PR docs/chore riêng (cập nhật 3 file md, dời `puzzles`/`results`/`tests` vào `Source/`, `requirements`). Sửa theo 4 điểm: `SatSolver` protocol và `CountingSolver` đặt trong `sat/`; `classify(cnf_kb, var_id, solver, deadline)` cùng `build_kb_cnf` ở `kb_builder`; bổ sung `errors`, `regions`, `knowledge`, `encoding`, `GameEngine` vào PR-B; bỏ bước đồng bộ `develop` và `main`. Đưa `app/session.py` vào chính thức, mỏng (`load_puzzle`, `restart`, `submit_verdict`, `hint`, `auto_solve_steps` là generator, trả dataclass), một chủ duy nhất là Hưng. Gỡ `session.py` khỏi cây `engine/` ở cả 3 tài liệu và khỏi hàng Nguyên trong `Process.md`. Chưa động vào thân hàm của module người khác. Bạn hiểu ý tôi chứ?”

- “Đối chiếu toàn bộ source với đề Project 2; chỉ ra yêu cầu đã đạt và phần còn thiếu.”
- “Kiểm tra encoder CNF có tương đương semantic evaluator trên mọi assignment nhỏ hay không.”
- “Rà soát DPLL assumptions, propagation, backtracking và timeout.”
- “Kiểm tra agent có đọc solution hoặc clue ẩn hay không bằng static và dynamic isolation test.”
- “Chạy benchmark toàn bộ puzzle, giữ lại failure/timeout và xuất các chỉ số cho report.”
