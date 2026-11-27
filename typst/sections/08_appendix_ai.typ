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

- “Đối chiếu toàn bộ source với đề Project 2; chỉ ra yêu cầu đã đạt và phần còn thiếu.”
- “Kiểm tra encoder CNF có tương đương semantic evaluator trên mọi assignment nhỏ hay không.”
- “Rà soát DPLL assumptions, propagation, backtracking và timeout.”
- “Kiểm tra agent có đọc solution hoặc clue ẩn hay không bằng static và dynamic isolation test.”
- “Chạy benchmark toàn bộ puzzle, giữ lại failure/timeout và xuất các chỉ số cho report.”
