#import "../components.typ": algorithm_box, styled_table, callout_note

== Bộ giải SAT DPLL và suy diễn logic

Phần này tập trung vào con đường từ một tập clue công khai đến kết luận
logic mà tác tử có thể sử dụng trong trò chơi. Các khái niệm về ô, vùng,
clue và `PublicState` đã được trình bày ở mục 2; ở đây chỉ nhắc lại những
điểm cần thiết để giải thích cách cài đặt.

=== Từ ngữ nghĩa clue đến CNF

Mỗi ô trên bàn cờ tương ứng với một biến chính $C_i$. Literal dương `i`
biểu diễn `C_i = True`, còn literal âm `-i` biểu diễn `C_i = False`.
Encoder nhận các đối tượng clue, sinh ra một `CNF` và không cần biết puzzle
cụ thể nào đang được chơi.

==== Clue nhị phân

Với `DIFFERENT(C_i, C_j)`, hai trạng thái bằng nhau phải bị loại. Vì vậy
encoder sinh hai mệnh đề:

$ (C_i ∨ C_j) ∧ (¬C_i ∨ ¬C_j) $

Mệnh đề thứ nhất loại trường hợp cả hai ô đều `INNOCENT`, mệnh đề thứ hai
loại trường hợp cả hai đều `CRIMINAL`. Hai cách gán còn lại chính là XOR.
Với `SAME`, encoder dùng hai mệnh đề ngược lại. Cách viết này giúp
`evaluate()` và CNF encoder có cùng một ngữ nghĩa nhưng vẫn kiểm tra được
độc lập trong bộ test.

==== Clue đếm và biến phụ

Với `EXACTLY(2)` trên bốn literal, encoder ghép `AT_MOST(2)` và
`AT_LEAST(2)`. Vế thứ nhất sinh các clause phủ định mọi nhóm ba literal;
vế thứ hai sinh các clause dương trên cùng các nhóm. Tổng cộng có tám
clause trực tiếp.

Chẳng hạn, với `EXACTLY(1)` trên ba biến $C_1, C_2, C_3$, vế `AT_LEAST(1)` sinh một mệnh đề dương và vế `AT_MOST(1)` sinh ba mệnh đề nhị phân loại trừ từng cặp:

$ (C_1 ∨ C_2 ∨ C_3) ∧ (¬C_1 ∨ ¬C_2) ∧ (¬C_1 ∨ ¬C_3) ∧ (¬C_2 ∨ ¬C_3) $

#styled_table(
  (1.45fr, 3.1fr),
  ([Thành phần], [Cách mã hóa]),
  (
    ([`AT_MOST(k)`], [Với mỗi nhóm `k + 1` literal, sinh một clause phủ định.]),
    ([`AT_LEAST(k)`], [Áp dụng cùng quy tắc cho các literal phủ định.]),
    ([`EXACTLY(k)`], [Kết hợp hai vế `AT_MOST(k)` và `AT_LEAST(k)`.]),
    ([Sequential Counter], [Được chọn khi số clause trực tiếp vượt `direct_threshold`; các biến đếm được tính là auxiliary variables.]),
  ),
  align: (left + horizon, left + horizon),
  caption: [Các lựa chọn mã hóa cho clue đếm],
)

Hai extension bắt buộc của nhóm là `PARITY` và `COMPOUND`. `PARITY` dùng
chuỗi XOR để theo dõi tính chẵn/lẻ của vùng; `COMPOUND` dùng literal đại
diện theo Tseitin cho các phép `AND`, `OR` và `NOT`. Ngoài ra,
`COMPARE_COUNT` được bổ sung để so sánh số Criminal của hai vùng. Với
`GREATER` và `LESS`, encoder dùng các điều kiện nghiêm ngặt thay vì nhầm
lẫn với quan hệ `>=` hoặc `<=`.

=== Giao diện SAT và thống kê

Tầng `sat/` chỉ làm việc với số nguyên literal và danh sách clause. Nhờ
đó, DPLL không phụ thuộc vào domain, engine hay GUI. Các kiểu chính gồm:

```python
class CNF:
    num_vars: int
    clauses: list[list[int]]

class SatSolver(Protocol):
    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        ...
```

`SatResult` phân biệt ba trạng thái `SAT`, `UNSAT` và `TIMEOUT`. Khi kết
quả là `SAT`, model luôn có đủ các biến từ `1` đến `num_vars`; những biến
chưa bị ràng buộc được điền `False`. `SolverStats` ghi lại decisions,
propagations, backtracks và runtime của từng lượt giải.

`CountingSolver` bọc một solver bất kỳ nhưng giữ nguyên giao diện trên.
Nó cộng dồn số lần gọi và các bộ đếm DPLL để phần agent và phần benchmark
có thể dùng cùng một nguồn số liệu.

=== Cài đặt DPLL

Bộ giải được triển khai theo thủ tục DPLL truyền thống của Davis,
Logemann và Loveland (1960).
Mỗi lượt gọi tạo một assignment mới, áp dụng assumptions trước, sau đó
luân phiên giữa lan truyền đơn vị và phân nhánh.

#algorithm_box(
  [DPLL với lan truyền đơn vị và quay lui],
  input: [CNF, assumptions tùy chọn và deadline],
  output: [`SAT` kèm model, `UNSAT` hoặc `TIMEOUT` cùng thống kê],
  steps: (
    [Gán các assumptions. Nếu cùng một biến bị ép theo hai hướng, trả `UNSAT`.],
    [Quét các clause. Nếu một clause chỉ còn một literal chưa gán, gán literal đó để clause đúng.],
    [Lặp lại bước lan truyền cho đến khi không còn phép gán mới hoặc phát hiện mâu thuẫn.],
    [Nếu mọi clause đã đúng, hoàn tất model cho các biến còn tự do và trả `SAT`.],
    [Nếu chưa giải được, chọn biến chưa gán đầu tiên, thử một nhánh rồi quay lui khi nhánh đó mâu thuẫn.],
    [Kiểm tra deadline trong lúc quét, hoàn tác assignment và tạo model; quá hạn thì trả `TIMEOUT`.],
  ),
)

Trong `propagate()`, một clause được xem là đã thỏa nếu có ít nhất một
literal đúng. Nếu toàn bộ literal đều sai, solver phát hiện mâu thuẫn.
Nếu chỉ còn một literal chưa gán, solver gán literal đó và quét lại từ
đầu, vì phép gán mới có thể tạo ra unit clause ở nơi khác.

Khi cần phân nhánh, solver lưu biến và kích thước assignment hiện tại vào
stack `alternatives`. Nếu thử nhánh `True` mà gặp mâu thuẫn, các phép gán
phát sinh sau checkpoint được hoàn tác bằng `popitem()`, rồi solver thử
nhánh `False`. Cách làm này giữ nguyên các assumptions và các phép lan
truyền đã có trước điểm phân nhánh.

```python
elif alternatives:
    branch_variable, checkpoint = alternatives.pop()
    while len(assignment) > checkpoint:
        check_deadline()
        assignment.popitem()
    assignment[branch_variable] = False
    backtracks += 1
```

Deadline được kiểm tra cả khi đọc assumptions, quét literal và hoàn tác
assignment. Vì vậy timeout không làm mất các thống kê đã ghi nhận và cũng
không trả về một model chưa hoàn chỉnh.

=== Entailment và vòng lặp suy diễn

Ở mỗi wave, `PublicKnowledge` được chuyển thành CNF từ các clue đã lật và
các verdict đã được chứng minh. Trước khi xét từng ô, agent kiểm tra
`SAT(KB_t)` để phát hiện một public KB mâu thuẫn.

Với biến $C_i$, agent thực hiện hai truy vấn độc lập:

```text
SAT(KB_t ∧ ¬C_i)
SAT(KB_t ∧ C_i)
```

#styled_table(
  (1.8fr, 2.7fr),
  ([Kết quả hai truy vấn], [Kết luận]),
  (
    ([`UNSAT` với `¬C_i`], [Ô `i` bắt buộc là `CRIMINAL`.]),
    ([`UNSAT` với `C_i`], [Ô `i` bắt buộc là `INNOCENT`.]),
    ([Cả hai đều `SAT`], [Chưa đủ thông tin; kết luận là `UNKNOWN`.]),
    ([Cả hai đều `UNSAT`], [Public KB mâu thuẫn; kết luận là `INCONSISTENT`.]),
    ([Một truy vấn `TIMEOUT`], [Dừng wave và trả `TIMEOUT`.]),
  ),
  align: (left + horizon, left + horizon),
  caption: [Phân loại entailment bằng hai truy vấn SAT],
)

Các truy vấn được lưu trong `TraceStep`, cùng với wave, step, clue đang
hoạt động và verdict cuối cùng. Agent chỉ nộp verdict khi đã có kết luận
`CRIMINAL` hoặc `INNOCENT`; nếu verdict được engine chấp nhận, clue mới
được thêm vào public state và wave tiếp theo được dựng lại từ đầu.

==== Kiểm tra nghiệm duy nhất

`check_uniqueness()` được dùng offline trên CNF của toàn bộ puzzle. Solver
lấy model đầu tiên, sau đó thêm một blocking clause chỉ trên các biến
chính. Nếu CNF mới `UNSAT`, nghiệm là `UNIQUE`; nếu còn model thứ hai,
nghiệm là `MULTIPLE`. Các biến phụ không xuất hiện trong blocking clause,
vì chúng chỉ là chi tiết của cách mã hóa chứ không phải trạng thái của ô.

==== Dòng suy diễn của agent

`LogicAgent.iter_steps()` duyệt ô chưa lật theo thứ tự row-major. Mỗi bước
chỉ lật một ô được chứng minh, nhờ đó trace phản ánh đúng tiến trình chơi.
Nếu không còn ô nào bị ép, agent trả `STUCK`; nếu public KB mâu thuẫn hoặc
hết thời gian, agent trả `INCONSISTENT` hoặc `TIMEOUT`. Khi mọi ô đã được
mở, trạng thái cuối cùng là `SOLVED`.

=== Kiểm thử và kết quả hiện tại

Các test DPLL kiểm tra assumptions, unit propagation, model đầy đủ,
backtracking, timeout và việc không làm thay đổi CNF đầu vào. Test
uniqueness kiểm tra cả `UNIQUE`, `MULTIPLE`, `UNSAT` và timeout ở truy vấn
thứ hai. Test encoder đối chiếu `evaluate()` với CNF trên các phép gán
nhỏ, bao gồm cả `PARITY`, `COMPOUND` và các ca Sequential Counter.

#styled_table(
  (1.7fr, 1.1fr, 2.45fr),
  ([Nhóm kiểm thử], [Kết quả], [Ý nghĩa]),
  (
    ([Toàn bộ test suite], [`149 passed`], [Các tầng domain, SAT, encoder, agent, engine và experiments cùng hoạt động.]),
    ([Các ca có marker `xfail`], [`6 xpassed`], [Sequential Counter và `COMPOUND` hiện đã chạy thành công.]),
    ([Benchmark puzzle], [`14/17 SOLVED`], [14 puzzle chuẩn `UNIQUE` và `SOLVED`; 3 ca biên tái hiện đủ `STUCK`, `INCONSISTENT`, `TIMEOUT`.]),
  ),
  align: (left + horizon, center + horizon, left + horizon),
  caption: [Tóm tắt kiểm thử và thực nghiệm liên quan đến DPLL],
)

Kết quả chi tiết theo từng puzzle, gồm số biến chính, biến phụ, clause,
SAT calls, các bộ đếm DPLL, số bước và thời gian chạy, được trình bày ở
mục 6.2. Cách tách này giúp phần DPLL giải thích thuật toán và cách đo,
còn phần thực nghiệm giữ toàn bộ bảng benchmark ở một nơi duy nhất.

=== Kết luận

Thiết kế hiện tại giữ được ranh giới rõ giữa solver và các tầng nghiệp vụ:
DPLL chỉ biết CNF, còn reasoning chịu trách nhiệm dựng public KB và đặt
câu hỏi entailment. Nhờ blocking clause trên biến chính, hệ thống cũng
kiểm tra được tính duy nhất mà không phụ thuộc vào số lượng biến phụ.
Toàn bộ pipeline đã được kiểm chứng bằng test suite và benchmark 17
puzzle; các kết quả này là cơ sở cho phần đánh giá ở mục 6. Phần khai
báo tài liệu tham khảo và việc sử dụng AI được trình bày riêng ở cuối
báo cáo để tránh lặp lại trong chương kỹ thuật.
