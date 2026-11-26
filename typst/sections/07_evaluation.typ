#import "../components.typ": styled_table

#pagebreak()

= Mức độ hoàn thành

#styled_table(
  (1.45fr, 2.25fr, 1.0fr, 1.0fr),
  ([Thành viên], [Phạm vi], [% hoàn thành], [Ghi chú]),
  (
    ([Trần Văn Nguyên], [`domain/`, `main.py`, tích hợp, report], [100%], [Leader]),
    ([Nguyễn Gia Hưng], [`engine/`, `app/`, PyQt6 GUI], [100%], [Game/GUI]),
    ([Võ Nhật Minh], [`sat/`, `reasoning/`, semantic evaluator], [100%], [SAT/logic]),
    ([Lương Nhật Tân], [`encoding/`, parser, validator], [100%], [CNF]),
    ([Nguyễn Ngọc Quang], [`agent/`, `experiments/`, puzzles, tests], [100%], [Agent/benchmark]),
  ),
  caption: [Phân công và phần trăm đóng góp],
)
