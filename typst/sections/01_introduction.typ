#import "../components.typ": callout_note, callout_tip, callout_warning

#pagebreak(weak: true)

= Giới thiệu và mục tiêu

== Bối cảnh bài toán

Griductive là một trò chơi suy diễn trên lưới. Mỗi ô chứa một nhân vật có trạng thái ẩn là `CRIMINAL` hoặc `INNOCENT`, đồng thời sở hữu manh mối có nội dung đúng. Người chơi chỉ được lật một thẻ khi trạng thái của nhân vật đã được suy ra từ các manh mối đã có trước đó. Vì vậy, ta không thể đoán nghiệm, mà là kiểm tra hệ quả logic của Knowledge Base tăng dần.

Link video: https://drive.google.com/file/d/1J64Ka3cbOS2ott92SYkqXLO_36-otup3/view?usp=sharing
== Mục tiêu

Mục tiêu của nhóm là xây dựng pipeline hoàn chỉnh:

#figure(
  block(width: 100%, inset: 10pt, fill: rgb("#F0F5FA"), stroke: 0.8pt + rgb("#005CA9"), radius: 3pt)[
    #align(center)[
      JSON puzzle → Clue objects → CNF → DPLL → Entailment → Game/Agent
    ]
  ],
  caption: [Pipeline xử lý chính của hệ thống],
)

Hệ thống phải đồng thời bảo đảm ba tính chất. Thứ nhất, mọi clue đang hoạt động được chuyển sang CNF tự động, không hard-code công thức cho từng puzzle. Thứ hai, verdict chỉ được chấp nhận khi được chứng minh bởi `KB_t`. Thứ ba, tác tử chỉ nhận `PublicState`, không được nhìn solution hoặc clue chưa lật.

== Phạm vi và quyết định triển khai

Nhóm dùng desktop GUI bằng PyQt6. Các puzzle mẫu được đóng gói trong `Source/puzzles/` và chọn bằng preset selector trong GUI. 

Hai extension kèm theo được chọn là `PARITY` và `COMPOUND`. Ngoài ra, nhóm nối thêm `COMPARE_COUNT` qua parser, validator, semantic evaluator và encoder để mở rộng ngôn ngữ clue.


