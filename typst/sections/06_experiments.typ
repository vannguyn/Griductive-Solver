#import "../components.typ": styled_table

#pagebreak()

= Thực nghiệm và đánh giá

== Thiết lập

Benchmark dùng cùng toàn bộ 14 file JSON trong `Source/puzzles/`, gồm 3x3, 4x4, 5x5 và puzzle ví dụ. Mỗi case được loader kiểm tra, encode toàn bộ clue, rồi chạy `GameEngine + LogicAgent + DPLLSolver` với timeout 30 giây. Các số liệu được xuất sang `Source/results/metrics.csv`, `metrics.tex` và `runtime_by_grid.svg`.

== Kết quả

#styled_table(
  (2.15fr, 0.55fr, 1.0fr, 0.7fr, 1.0fr, 0.9fr, 0.85fr),
  ([Puzzle], [N], [P/A/C], [SAT], [D/P/B], [Outcome], [Check]),
  (
    ([`griductive-3x3-01`], [3], [9/0/16], [28], [0/139/0], [SOLVED], [UNIQUE]),
    ([`griductive-3x3-02`], [3], [9/0/22], [26], [0/146/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-01`], [3], [9/0/14], [28], [0/138/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-02`], [3], [9/0/19], [30], [0/131/0], [SOLVED], [UNIQUE]),
    ([`puzzle-3x3-03`], [3], [9/0/20], [28], [0/136/0], [SOLVED], [UNIQUE]),
    ([`knotwise-tutorial-3x3`], [3], [9/54/132], [54], [18/409/0], [SOLVED], [UNIQUE]),
    ([`griductive-4x4-01`], [4], [16/168/403], [45], [0/459/0], [SOLVED], [UNIQUE]),
    ([`griductive-4x4-02`], [4], [16/0/31], [69], [0/607/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-01`], [4], [16/0/23], [45], [0/360/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-02`], [4], [16/0/38], [45], [0/375/0], [SOLVED], [UNIQUE]),
    ([`puzzle-4x4-03`], [4], [16/0/36], [45], [0/360/0], [SOLVED], [UNIQUE]),
    ([`griductive-5x5-01`], [5], [25/400/934], [72], [0/1212/0], [SOLVED], [UNIQUE]),
    ([`puzzle-5x5-01`], [5], [25/0/63], [72], [0/924/0], [SOLVED], [UNIQUE]),
    ([`json-example-3x3`], [3], [9/0/15], [26], [0/125/0], [SOLVED], [UNIQUE]),
  ),
  caption: [Bảng thông số CNF, SAT và kết quả trên 14 puzzle],
  inset: 3pt,
)

Trong cột `P/A/C`, ba số lần lượt là primary variables, auxiliary variables và clauses. Cột `D/P/B` là decisions, propagations và backtracks. Kết quả cho thấy các puzzle hiện tại đều được giải không đoán, không có `STUCK`, `INCONSISTENT` hoặc `TIMEOUT`.

#styled_table(
  (2.15fr, 0.75fr, 0.75fr, 0.95fr, 0.95fr, 0.95fr),
  ([Puzzle], [Steps], [Waves], [Encode ms], [Solve ms], [Total ms]),
  (
    ([`griductive-3x3-01`], [8], [8], [0.07], [2.23], [2.30]),
    ([`griductive-3x3-02`], [8], [8], [0.05], [2.31], [2.37]),
    ([`puzzle-3x3-01`], [8], [8], [0.04], [2.04], [2.08]),
    ([`puzzle-3x3-02`], [8], [8], [0.05], [1.89], [1.94]),
    ([`puzzle-3x3-03`], [8], [8], [0.03], [1.93], [1.96]),
    ([`knotwise-tutorial-3x3`], [8], [8], [0.14], [4.93], [5.06]),
    ([`griductive-4x4-01`], [15], [15], [0.21], [6.11], [6.32]),
    ([`griductive-4x4-02`], [15], [15], [0.04], [5.93], [5.97]),
    ([`puzzle-4x4-01`], [15], [15], [0.04], [3.94], [3.98]),
    ([`puzzle-4x4-02`], [15], [15], [0.06], [4.89], [4.96]),
    ([`puzzle-4x4-03`], [15], [15], [0.05], [4.40], [4.45]),
    ([`griductive-5x5-01`], [24], [24], [0.37], [15.64], [16.01]),
    ([`puzzle-5x5-01`], [24], [24], [0.07], [11.09], [11.16]),
    ([`json-example-3x3`], [8], [8], [0.05], [1.98], [2.03]),
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
- DPLL chủ yếu giải bằng unit propagation; số decisions và backtracks bằng 0 trên toàn bộ benchmark hiện tại.
- Runtime tăng theo kích thước lưới và số biến phụ, nhưng 5x5 vẫn hoàn thành trong khoảng 11--17 ms trên môi trường đo.

== Giới hạn

Bộ puzzle hiện tại đều là ca hợp lệ và no-guess, nên chưa thể hiện failure case thực tế trong bảng benchmark. Test suite vẫn có các nhánh `UNKNOWN`, `INCONSISTENT` và `TIMEOUT`; khi benchmark gặp exception ở bước load, runner hiện ghi lỗi ra console thay vì tạo một dòng metrics riêng. Đây là điểm nên cải thiện nếu dùng cho bộ dữ liệu lỗi hoặc thí nghiệm robustness.
