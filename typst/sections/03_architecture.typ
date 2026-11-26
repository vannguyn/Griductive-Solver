#import "../components.typ": styled_table

#pagebreak()

= Kiến trúc và thiết kế hệ thống

== Phân tầng

Mã nguồn được tổ chức thành các tầng có phụ thuộc một chiều:

#styled_table(
  (1.25fr, 2.0fr, 2.35fr),
  ([Tầng], [Module], [Trách nhiệm]),
  (
    ([Domain], [`domain/`], [Coord, region, types, public state và errors]),
    ([Clues], [`clues/`], [Clue classes, parser, validator và evaluator]),
    ([SAT], [`sat/`], [CNF, DPLL, solver protocol và statistics]),
    ([Encoding], [`encoding/`], [VarMap, cardinality và clue-to-CNF]),
    ([Reasoning], [`reasoning/`], [KB builder, entailment và uniqueness]),
    ([Agent], [`agent/`], [Hint, trace và deduction loop]),
    ([Engine/App], [`engine/`, `app/`], [Puzzle ẩn, session facade và reveal protocol]),
    ([GUI], [`gui/`], [Board, verdict dialog, controls và visual feedback]),
    ([Experiments], [`experiments/`], [Validation, benchmark và exports]),
  ),
  caption: [Các tầng chính của Griductive Solver],
)

== Tách dữ liệu bí mật và dữ liệu công khai

`GameEngine` giữ `Puzzle`, trong đó có solution và toàn bộ clue. `PublicState` chỉ chứa các ô, status đã biết và clue đã mở. `LogicAgent` phụ thuộc vào protocol `PublicGame`, không import `engine`, `gui` hoặc `app`. Static AST checks và dynamic `StrictMockGame` trong `test_isolation.py` kiểm tra ranh giới này.

#figure(
  block(width: 100%, inset: 10pt, fill: rgb("#F6F8FA"), stroke: 0.6pt + rgb("#D0D7DE"), radius: 3pt)[
    #set text(font: "Consolas", size: 10.5pt)
    GUI → GameSession → GameEngine → PublicKnowledge → Encoder → DPLL
    \
    LogicAgent ──────────────── PublicGame protocol ────────────────┘
  ],
  caption: [Luồng dữ liệu không làm lộ solution],
)

== Các luồng sử dụng chính

- Manual play: người dùng click ô úp, chọn verdict trong `VerdictDialog`, engine phân loại và chỉ lật khi `ACCEPTED`.
- Hint: `suggest_hint()` duyệt ô chưa mở theo row-major và trả ô forced đầu tiên.
- Auto Solve: `LogicAgent.iter_steps()` chạy từng wave qua `QTimer`, GUI cập nhật board sau mỗi bước.
- Restart: engine phục hồi đúng `initially_revealed`, không cần GUI đọc solution.
- Preset level: dropdown chọn các JSON được đóng gói trong `Source/puzzles/`; không có upload file ngoài trong GUI hiện tại.

== Thiết kế kiểm lỗi

Solver phân biệt `SAT`, `UNSAT` và `TIMEOUT`. Engine phân biệt `NOT_PROVABLE`, `CONTRADICTED`, `INCONSISTENT` và `ALREADY_REVEALED`. Agent dừng ở `STUCK`, `INCONSISTENT` hoặc `TIMEOUT` thay vì đoán tiếp.
