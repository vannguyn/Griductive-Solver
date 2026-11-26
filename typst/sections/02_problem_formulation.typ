#import "../components.typ": styled_table

#pagebreak()

= Mô hình hóa bài toán

== Bàn cờ và biến mệnh đề

Với lưới kích thước $N times N$, mỗi ô được định danh bởi cột và hàng, ví dụ `C2`. Biến chính $C_i$ đại diện cho trạng thái Criminal của ô thứ $i$:

$ C_i = cases("True, nếu ô i là CRIMINAL", "False, nếu ô i là INNOCENT") $

Ánh xạ biến là deterministic theo thứ tự row-major. Với lưới $N times N$, ô `A1` nhận biến 1, `B1` nhận biến 2 và `A2` nhận biến $N + 1$. Các biến phụ do encoder sinh ra luôn được cấp sau $N^2$ biến chính và được thống kê riêng.

== Vùng và ngữ nghĩa clue

Các vùng được hỗ trợ gồm hàng, cột, các ô láng giềng theo tám hướng và danh sách tọa độ explicit. Vùng neighbors loại trừ chính ô trung tâm. Parser canonicalize tọa độ và loại phần tử trùng trong vùng explicit.

#styled_table(
  (1.25fr, 2.3fr, 2.25fr),
  ([Loại], [Ý nghĩa], [Điều kiện semantic evaluator]),
  (
    ([`FACT`], [Một ô có trạng thái chỉ định], [$C_i$ hoặc $¬C_i$]),
    ([`SAME`], [Hai ô cùng trạng thái], [$C_i ↔ C_j$]),
    ([`DIFFERENT`], [Hai ô khác trạng thái], [$C_i xor C_j$]),
    ([`EXACTLY`], [Đúng $k$ Criminal trong vùng], [$sum_(i in R) C_i = k$]),
    ([`AT_LEAST`], [Ít nhất $k$ Criminal], [$sum_(i in R) C_i >= k$]),
    ([`AT_MOST`], [Nhiều nhất $k$ Criminal], [$sum_(i in R) C_i <= k$]),
    ([`PARITY`], [Số Criminal chẵn hoặc lẻ], [$sum_(i in R) C_i mod 2$]),
    ([`COMPOUND`], [AND, OR, NOT giữa clue con], [Tính theo giá trị clue con]),
    ([`COMPARE_COUNT`], [So sánh số Criminal hai vùng], [`count(L) >, <, = count(R)`]),
  ),
  caption: [Các template clue và evaluator tương ứng],
)

Mỗi lớp clue cài đặt `cells()` để cung cấp tọa độ cho GUI và `evaluate(assign)` để kiểm chứng độc lập với CNF encoder. Loader dùng evaluator để xác nhận solution khai báo phù hợp với mọi clue.

== Knowledge Base và giao thức lật thẻ

Tại bước $t$, Knowledge Base được định nghĩa:

#raw("KB_t = CNF(revealed clues) AND unit(proved verdicts)")

Hidden status và clue chưa lật không thuộc `KB_t`. Khi người chơi hoặc agent nộp verdict, engine gọi entailment trên `PublicKnowledge`. Nếu verdict được chứng minh, ô được đánh dấu revealed và clue của ô đó được thêm vào trạng thái công khai để tạo `KB_(t+1)`. Nếu verdict chưa được chứng minh hoặc bị phản bác, trạng thái giữ nguyên.

Với biến $C_i$, hệ thống kiểm tra hai truy vấn:

#raw("KB_t |= C_i iff KB_t AND NOT C_i is UNSAT")
thì truy vấn là `UNSAT`.

#raw("KB_t |= NOT C_i iff KB_t AND C_i is UNSAT")
thì truy vấn là `UNSAT`.

Hai truy vấn đều SAT cho kết quả `UNKNOWN`; cả hai UNSAT chỉ xảy ra khi KB không nhất quán.

== Kiểm tra nghiệm duy nhất

`check_uniqueness()` giải CNF đầy đủ một lần để lấy mô hình đầu tiên $M_1$, sau đó thêm blocking clause chỉ trên các biến chính $1..N^2$. Nếu CNF sau blocking clause UNSAT thì nghiệm là `UNIQUE`; nếu SAT thì là `MULTIPLE`; solver timeout được giữ nguyên là `TIMEOUT`.
