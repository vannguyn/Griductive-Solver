#import "../components.typ": styled_table

#pagebreak()

= Thực nghiệm và đánh giá

== Thiết lập

Benchmark dùng toàn bộ 17 file JSON trong `Source/puzzles/`, gồm 14 puzzle chuẩn ở các kích thước `3x3`, `4x4`, `5x5` và 3 ca kiểm thử biên (`puzzle-3x3-04`, `puzzle-4x4-04`, `puzzle-5x5-02`). Mỗi case được loader kiểm tra, encode toàn bộ clue, rồi chạy `GameEngine + LogicAgent + DPLLSolver` với ngưỡng timeout mặc định 30 giây (riêng `puzzle-5x5-02` đặt ngưỡng 10 ms để kiểm chứng cơ chế ngắt `TIMEOUT`). Các số liệu được xuất sang `Source/results/metrics.csv`, `metrics.tex` và `runtime_by_grid.svg`.

== Kết quả

#styled_table(
  (1.6fr, 0.3fr, 0.96fr, 0.5fr, 0.9fr, 1.45fr, 1fr),
  ([Puzzle], [N], [P/A/C], [SAT], [D/P/B], [Outcome], [Check]),
  (
    ([`griductive-3x3-01`], [3], [9/0/16], [28], [0/139/0], [SOLVED], [UNIQUE]),
    ([`griductive-3x3-02`], [3], [9/0/22], [26], [0/146/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-01`], [3], [9/0/14], [28], [0/138/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-02`], [3], [9/0/19], [30], [0/131/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-03`], [3], [9/0/20], [28], [0/136/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-04`], [3], [9/0/10], [47], [5/295/0], [STUCK], [MULTIPLE]),
    ([`knotwise-tutorial-3x3`], [3], [9/54/132], [54], [18/409/0], [SOLVED], [UNIQUE]),
    ([`griductive-4x4-01`], [4], [16/168/403], [45], [0/459/0], [SOLVED], [UNIQUE]),
    ([`griductive-4x4-02`], [4], [16/0/31], [69], [0/607/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-01`], [4], [16/0/23], [45], [0/360/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-02`], [4], [16/0/38], [45], [0/375/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-03`], [4], [16/0/36], [45], [0/360/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-04`], [4], [16/44/144], [1], [0/33/0], [INCONSISTENT], [UNSAT]),
    ([`griductive-5x5-01`], [5], [25/400/934], [72], [0/1212/0], [SOLVED], [UNIQUE]),
    ([`puzzle-5x5-01`], [5], [25/0/63], [72], [0/924/0], [SOLVED], [UNIQUE]),
    ([`puzzle-5x5-02`], [5], [25/0/320], [6], [21/110/0], [TIMEOUT], [MULTIPLE]),
    ([`json-example-3x3`], [3], [9/0/15], [26], [0/125/0], [SOLVED], [UNIQUE]),
  ),
  caption: [Bảng thông số CNF, SAT và kết quả trên 17 puzzle],
  inset: 3pt,
)

Trong cột `P/A/C`, ba số lần lượt là primary variables, auxiliary variables và clauses. Cột `D/P/B` là decisions, propagations và backtracks. Kết quả cho thấy toàn bộ 14 puzzle chuẩn đều đạt `SOLVED` và `UNIQUE`, trong khi 3 ca kiểm thử biên tái hiện đầy đủ các trạng thái dừng an toàn của tác tử: `puzzle-3x3-04` dừng ở `STUCK` sau 6 bước khi hai ô `B1, C1` đa nghiệm (`MULTIPLE`); `puzzle-4x4-04` phát hiện `INCONSISTENT` ngay tại lần gọi SAT đầu tiên (`0` bước); và `puzzle-5x5-02` dừng ở `TIMEOUT` sau 6 truy vấn SAT và 21 lần phân nhánh.

#styled_table(
  (2.15fr, 0.75fr, 0.75fr, 0.95fr, 0.95fr, 0.95fr),
  ([Puzzle], [Steps], [Waves], [Encode ms], [Solve ms], [Total ms]),
  (
    ([`griductive-3x3-01`], [8], [8], [0.06], [1.73], [1.78]),
    ([`griductive-3x3-02`], [8], [8], [0.03], [1.95], [1.98]),
    ([`puzzle-3x3-01`], [8], [8], [0.04], [1.68], [1.72]),
    ([`puzzle-3x3-02`], [8], [8], [0.05], [1.63], [1.69]),
    ([`puzzle-3x3-03`], [8], [8], [0.04], [2.51], [2.56]),
    ([`puzzle-3x3-04`], [6], [6], [0.09], [2.53], [2.61]),
    ([`knotwise-tutorial-3x3`], [8], [8], [0.16], [6.41], [6.58]),
    ([`griductive-4x4-01`], [15], [15], [0.16], [5.45], [5.62]),
    ([`griductive-4x4-02`], [15], [15], [0.05], [7.20], [7.25]),
    ([`puzzle-4x4-01`], [15], [15], [0.05], [4.70], [4.75]),
    ([`puzzle-4x4-02`], [15], [15], [0.10], [4.25], [4.35]),
    ([`puzzle-4x4-03`], [15], [15], [0.07], [5.58], [5.65]),
    ([`puzzle-4x4-04`], [0], [0], [0.16], [0.48], [0.65]),
    ([`griductive-5x5-01`], [24], [24], [0.42], [17.59], [18.01]),
    ([`puzzle-5x5-01`], [24], [24], [0.11], [10.91], [11.02]),
    ([`puzzle-5x5-02`], [0], [0], [0.35], [10.10], [10.45]),
    ([`json-example-3x3`], [8], [8], [0.04], [1.73], [1.78]),
  ),
  caption: [Bảng phân rã bước suy luận và thời gian chạy],
  inset: 3pt,
)

#figure(
  image("../../Source/results/runtime_by_grid.svg", width: 100%),
  caption: [Thời gian chạy theo từng puzzle trong bộ benchmark],
)

== Nhận xét

- Direct encoding đủ nhỏ và thường có zero auxiliary variables.
- Các case `griductive-*` có compound/cardinality lớn nên sinh nhiều biến phụ; `griductive-5x5-01` là stress case với 400 auxiliary variables và 934 clauses.
- DPLL giải phần lớn các puzzle chuẩn thuần bằng unit propagation (`0` decisions); riêng `knotwise-tutorial-3x3` cần `18` decisions (không backtrack) để chứng minh entailment, còn hai ca biên `puzzle-3x3-04` và `puzzle-5x5-02` phát sinh lần lượt `5` và `21` decisions khi tìm kiếm trên không gian chưa bị ép.
- Runtime tăng theo kích thước lưới và số biến phụ, nhưng các puzzle `5x5` giải được đều hoàn thành trong khoảng `11.02--18.01 ms` trên môi trường đo.

== Giới hạn

- Bộ giải DPLL hiện cài đặt theo thuật toán kinh điển (chọn biến chưa gán đầu tiên, chưa tích hợp heuristic VSIDS hay conflict-driven clause learning), nên tốc độ suy giảm rõ rệt khi gặp mạng ràng buộc `PARITY` mật độ cao thiếu dữ kiện ban đầu (`puzzle-5x5-02`).
- Khi nạp file JSON sai cấu trúc schema ngoài tập benchmark chuẩn, `runner.py` hiện ghi thông báo lỗi ra console thay vì xuất một dòng bản ghi lỗi vào file CSV.
