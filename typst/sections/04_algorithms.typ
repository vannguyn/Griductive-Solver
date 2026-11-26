#import "../components.typ": callout_note

#pagebreak()

= Thuật toán và mã hóa CNF

Phần này trình bày chi tiết bộ giải SAT DPLL, giao diện CNF, cơ chế
entailment, kiểm tra nghiệm duy nhất và vòng lặp suy diễn của tác tử.
Nội dung kỹ thuật được tổ chức lại từ tài liệu `Dpll-solver.typ` để nằm
trong đúng mục 4 của báo cáo, đồng thời cập nhật theo source và kết quả
kiểm thử hiện tại.

#callout_note(
  [
    DPLL chỉ nhận `CNF`, literal nguyên và các assumptions; solver không
    phụ thuộc vào domain, engine hoặc GUI. Các tầng reasoning và agent xây
    dựng `KB_t` rồi gọi DPLL thông qua giao diện `SatSolver`.
  ],
  title: [Phạm vi của bộ giải],
)

#include "Dpll-solver.typ"
