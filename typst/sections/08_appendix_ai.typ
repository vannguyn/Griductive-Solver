#import "../components.typ": styled_table

#pagebreak()

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
