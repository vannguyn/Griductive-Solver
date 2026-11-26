#import "../components.typ": algorithm_box, styled_table

#pagebreak(weak: true)

= Bộ giải SAT DPLL và kiểm chứng suy diễn

*Võ Nhật Minh (24120202)*

== Phạm vi đóng góp

Phần việc được giao bao gồm tầng `sat/`, tầng `reasoning/` và các lớp
ngữ nghĩa trong `clues/`. Các thay đổi trên nhánh `feature/dpll-solver`
tập trung vào `griductive/sat/dpll.py` và ba bộ kiểm thử trong
`Source/tests/`. `test_dpll.py` kiểm chứng bộ giải, `test_uniqueness.py`
kiểm tra nghiệm trên các biến chính và `test_encoder_vs_eval.py` đối
chiếu hàm ngữ nghĩa `evaluate()` với CNF do encoder của nhóm sinh ra.

== Mô hình hóa và ngữ nghĩa manh mối

Bộ giải SAT nhận các ràng buộc của Griductive dưới dạng công thức chuẩn hội
(CNF). Mỗi ô $i$ có một biến chính $C_i$, với `True` ứng với `CRIMINAL` và
`False` ứng với `INNOCENT`. Mệnh đề là tuyển các literal. Trong mã nguồn,
literal dương `i` biểu diễn $C_i$ và literal âm `-i` biểu diễn $¬ C_i$.
Các biến phụ phục vụ mã hóa được cấp số sau các biến chính.

Tri thức ban đầu $upright("KB")_0$ được dựng từ các ô có trong
`initially_revealed`. Tại bước $t$, $upright("KB")_t$ là hội của CNF
cho các manh mối đã lật và các mệnh đề đơn vị biểu diễn trạng thái
đã biết. Một phán quyết được chấp nhận sẽ lật ô tương ứng. Trạng thái
mới và manh mối vừa lật được dùng để dựng $upright("KB")_(t+1)$.

=== Giao diện chung của manh mối

`clues/base.py` công khai lại lớp trừu tượng `Clue` từ
`griductive.domain.clue`. Mỗi đối tượng có `id: str`, `owner: Coord`
và `clue_type: str`. `owner` xác định ô sở hữu manh mối. `cells()`
trả về các ô được nhắc đến trong nội dung. Ví dụ, manh mối
của A1 có thể khẳng định B1 là `INNOCENT`. Khi đó `owner` là A1 và
`cells()` trả `("B1",)`.

```python
def cells(self) -> tuple[Coord, ...]:
    ...

def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
    ...
```

`cells()` cung cấp tọa độ tham chiếu cho giao diện và các bước xử lý
manh mối. `evaluate()` nhận ánh xạ từ tọa độ sang giá trị Boolean và
trả `True` khi phép gán thỏa nội dung manh mối. Trình nạp puzzle dùng
hàm này để xác thực đáp án khai báo. Bộ kiểm thử dùng cùng giao diện
để đối chiếu với CNF do encoder sinh ra. Parser, bộ kiểm tra dữ liệu
và phần chuyển sang CNF thuộc phạm vi của Nhật Tân.

=== Sáu lớp manh mối cơ bản

Các lớp trong `core.py` nhận `id` và `owner` rồi truyền mã loại cố định
cho lớp `Clue`. Bảng dưới đây liệt kê tham số riêng của từng lớp và
điều kiện để `evaluate()` trả `True`.

#styled_table(
  (1.15fr, 1.65fr, 2.2fr),
  ([Lớp], [Tham số riêng], [Điều kiện thỏa]),
  (
    [`FactClue`], [`target_cell`, `target_status`], [Giá trị của ô đích bằng giá trị Boolean ứng với trạng thái yêu cầu.],
    [`SameClue`], [`cell_a`, `cell_b`], [Hai giá trị bằng nhau.],
    [`DifferentClue`], [`cell_a`, `cell_b`], [Hai giá trị khác nhau.],
    [`ExactlyClue`], [`k`, `region_spec`, `region_cells`], [Số ô `CRIMINAL` trong vùng bằng $k$.],
    [`AtLeastClue`], [`k`, `region_spec`, `region_cells`], [Số ô `CRIMINAL` trong vùng lớn hơn hoặc bằng $k$.],
    [`AtMostClue`], [`k`, `region_spec`, `region_cells`], [Số ô `CRIMINAL` trong vùng nhỏ hơn hoặc bằng $k$.],
  ),
  align: (left + horizon, left + horizon, left + horizon),
  inset: 5pt,
  caption: [Khai báo và điều kiện thỏa của các lớp manh mối cơ bản],
)

`target_cell`, `cell_a` và `cell_b` có kiểu `Coord`. `target_status`
có kiểu `Status`. Với các lớp đếm, `k` là `int`,
`region_spec: RegionSpec` mô tả vùng và
`region_cells: tuple[Coord, ...]` chứa các ô cụ thể trong vùng.
`cells()` trả các ô đó theo thứ tự đã có. Phép đếm trong `evaluate()`
duyệt `region_cells` và chỉ tăng khi `assign.get(cell, False) is True`.

=== Manh mối mở rộng

`ParityClue` nhận `parity: str`, `region_spec` và `region_cells`.
Lớp đổi `parity` sang chữ hoa. `evaluate()` đếm số ô `CRIMINAL`
trong vùng, sau đó kiểm tra phần dư bằng 0 với `EVEN` hoặc bằng 1
với `ODD`. `cells()` trả `region_cells`.

`CompoundClue` nhận `op: str` và `sub_clues: tuple[Clue, ...]`.
Lớp đổi `op` sang chữ hoa. Các manh mối con dùng chung một phép gán.
`AND` gọi `all()` trên các kết quả con, `OR` gọi `any()` và `NOT`
phủ định kết quả của một manh mối con. `NOT` trả `False` nếu số manh
mối con khác 1. Vì một phần tử trong `sub_clues` có thể là
`CompoundClue`, cấu trúc này biểu diễn được biểu thức lồng như
$(¬ A) ∨ B$. Phương thức `cells()` duyệt các manh mối con và dùng
một `set` để loại tọa độ lặp, giữ thứ tự xuất hiện đầu tiên trong
tuple kết quả.

`CompareCountClue` là lớp ngữ nghĩa tùy chọn nhận `op` và hai tuple
tọa độ `region_left_cells`, `region_right_cells`. `evaluate()` tính
số ô `CRIMINAL` riêng cho mỗi vùng rồi so sánh theo `GREATER`, `LESS`
hoặc `EQUAL`. Hai mở rộng được dùng trong bộ kiểm thử đối chiếu của
nhánh này là `PARITY` và `COMPOUND`.

== Dẫn xuất CNF từ ngữ nghĩa manh mối

=== Ràng buộc nhị phân `DIFFERENT`

`DifferentClue.evaluate()` trả `True` khi hai ô có giá trị khác nhau.
Với các biến $C_i$ và $C_j$, mệnh đề $(C_i ∨ C_j)$ loại phép gán cả
hai bằng `False`. Mệnh đề $(¬ C_i ∨ ¬ C_j)$ loại phép gán cả hai
bằng `True`. Hội hai mệnh đề giữ đúng hai trường hợp có trạng thái
khác nhau.

$ (C_i ∨ C_j) ∧ (¬ C_i ∨ ¬ C_j) $

Khi hai ô có ID 1 và 2, `encode_different()` trả `[[1, 2], [-1, -2]]`.
Các phép gán `(True, False)` và `(False, True)` thỏa đồng thời hai
mệnh đề, phù hợp với kết quả của hàm ngữ nghĩa.

=== Ràng buộc đếm `EXACTLY(2)` trên bốn ô

Gọi $R$ là vùng gồm bốn ô có ID từ 1 đến 4. Điều kiện có đúng hai
`CRIMINAL` là hội của `AT_MOST(2)` và `AT_LEAST(2)`. Để có tối đa
hai ô `CRIMINAL`, mỗi nhóm ba ô cần ít nhất một ô `INNOCENT`. Vì
vậy, mỗi bộ ba sinh một mệnh đề có cả ba literal âm. Để có tối thiểu
hai ô `CRIMINAL`, mỗi nhóm ba ô cần ít nhất một ô `CRIMINAL`. Mỗi
bộ ba sinh thêm một mệnh đề có cả ba literal dương.

#styled_table(
  (1fr, 1fr),
  ([Mệnh đề của `AT_MOST(2)`], [Mệnh đề của `AT_LEAST(2)`]),
  (
    [`[-1, -2, -3]`], [`[1, 2, 3]`],
    [`[-1, -2, -4]`], [`[1, 2, 4]`],
    [`[-1, -3, -4]`], [`[1, 3, 4]`],
    [`[-2, -3, -4]`], [`[2, 3, 4]`],
  ),
  caption: [Tám mệnh đề trực tiếp của `EXACTLY(2)` với bốn biến chính],
)

Với $0 < k < n$, bộ mã hóa ước lượng `AT_MOST(k)` bằng số tổ hợp
chọn $k+1$ từ $n$ ô và `AT_LEAST(k)` bằng số tổ hợp chọn $n-k+1$
ô. `EXACTLY(k)` lấy tổng hai số. Ví dụ trên sinh 8 mệnh đề, nằm
trong ngưỡng mặc định `direct_threshold=64`. Nếu ước lượng vượt
ngưỡng, `encode_cardinality()` chuyển sang nhánh Sequential Counter,
được thiết kế để dùng biến phụ cho bộ đếm. Trên phiên bản dùng
cho báo cáo, nhánh đó vẫn trả `NotImplementedError`.

== Khai báo và giao diện của `sat/`

=== Biểu diễn CNF và kết quả giải

`cnf.py` khai báo `Literal` là số nguyên và `Clause` là danh sách literal.
Theo quy ước của tầng SAT, ID biến nằm trong `1..num_vars` và literal
mang dấu của biến đó. `num_vars` tính cả biến được khai báo nhưng không
xuất hiện trong mệnh đề. `clauses` là danh sách các mệnh đề phải đồng
thời đúng.

```python
Literal: TypeAlias = int
Clause: TypeAlias = list[Literal]

@dataclass
class CNF:
    num_vars: int
    clauses: list[Clause] = field(default_factory=list)
```

Ví dụ, `CNF(3, [[1, -2], [3]])` biểu diễn $(C_1 ∨ ¬ C_2) ∧ C_3$.
`field(default_factory=list)` tạo một danh sách riêng cho mỗi CNF.
`add_clause(clause)` nối một mệnh đề vào danh sách hiện tại.
`copy()` tạo cả danh sách mệnh đề mới lẫn bản sao của từng mệnh đề,
cho phép `check_uniqueness()` thêm mệnh đề chặn trên bản sao CNF.

`SatResult` là dataclass khai báo với `frozen=True`. Trường `status`
có kiểu `SatStatus` và nhận một trong ba giá trị `SAT`, `UNSAT`,
`TIMEOUT`. `model: dict[int, bool] | None` chứa ánh xạ đầy đủ khi
DPLL trả `SAT`, kể cả các biến đã khai báo nhưng còn tự do. Hai trạng
thái kia trả `model = None`. `stats: SolverStats | None` cho phép một
solver tuân theo giao diện trả kết quả mà chưa cung cấp số đo.

=== Giao diện solver và thống kê

Trong `stats.py`, `SolverStats` là dataclass với ba bộ đếm kiểu `int`
gồm `decisions`, `propagations`, `backtracks`, và `runtime_ms` kiểu
`float`. Các trường mặc định bằng 0, mỗi đối tượng ghi số liệu của
một lượt SAT.

`solver.py` định nghĩa `SatSolver` theo `Protocol`. Các hàm suy diễn
nhận một đối tượng có phương thức `solve()` theo chữ ký dưới đây.
`DPLLSolver` cung cấp phần thực thi. Test uniqueness cũng dùng giao
diện này để mô phỏng kết quả của từng lượt truy vấn.

```python
class SatSolver(Protocol):
    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        ...
```

`CountingSolver(inner_solver)` giữ cùng giao diện `solve()`. Mỗi lời
gọi tăng `calls`, chuyển CNF, giả định và thời hạn cho solver bên trong,
rồi cộng thống kê của kết quả vào các trường `total_*`. `last_stats`
lưu thống kê lượt gần nhất. Nếu kết quả có `stats = None`, lớp bọc đo
thời gian bằng đồng hồ của chính nó để cập nhật `last_stats` và tổng
thời gian. Phương thức trả lại `SatResult` nhận được từ solver bên
trong. `reset_counts()` đưa các tổng về 0 và `last_stats` về `None`.
`sat/__init__.py` công khai các kiểu CNF, kết quả, thống kê, giao diện
và hai lớp solver để các tầng khác có thể import từ `griductive.sat`.

== Cài đặt bộ giải DPLL

`DPLLSolver.solve(cnf, assumptions, deadline)` nhận một công thức CNF,
danh sách literal phải đúng trong lượt giải và thời điểm hết hạn theo
`time.perf_counter()`. Kết quả gồm trạng thái, mô hình nếu có và thống kê
lượt giải. Phương pháp tìm kiếm dựa trên thủ tục DPLL.#footnote[
  M. Davis, G. Logemann và D. Loveland, “A machine program for
  theorem-proving,” _Communications of the ACM_, tập 5, số 7,
  tr. 394–397, 1962. #link("https://doi.org/10.1145/368273.368557")[DOI].
]

#algorithm_box(
  [DPLL với lan truyền đơn vị và quay lui],
  input: [CNF, các literal giả định và thời điểm hết hạn tùy chọn],
  output: [`SAT` kèm mô hình đầy đủ, `UNSAT` hoặc `TIMEOUT`, kèm thống kê],
  steps: (
    [Gán các literal giả định. Trả `UNSAT` nếu cùng một biến bị ép nhận cả hai giá trị.],
    [Quét các mệnh đề. Khi một mệnh đề chưa đúng và chỉ còn một literal phân biệt chưa gán, gán literal đó thành đúng. Lặp đến khi không còn phép gán mới hoặc phát hiện mâu thuẫn.],
    [Khi mọi mệnh đề đã đúng, điền `False` cho các biến còn tự do trong `1..num_vars` và trả `SAT`.],
    [Nếu chưa có mâu thuẫn và còn mệnh đề chưa thỏa, chọn biến chưa gán đầu tiên theo thứ tự quét. Lưu điểm khôi phục vào ngăn xếp rồi thử `True`.],
    [Khi có mâu thuẫn, lấy nhánh gần nhất còn lựa chọn, hoàn tác các phép gán kể từ điểm khôi phục rồi thử `False`. Trả `UNSAT` nếu đã hết lựa chọn.],
    [Nếu hết thời gian ở bất kỳ bước nào, trả `TIMEOUT` kèm thống kê đã ghi nhận.],
  ),
)

=== Trạng thái và lan truyền đơn vị

Mỗi lần gọi `solve()` tạo một từ điển `assignment` và các bộ đếm riêng.
`search()` đọc từng giả định theo `abs(literal)` và `literal > 0` để xác
định biến và giá trị cần gán. Giả định lặp cùng dấu giữ nguyên giá trị.
Giả định trái dấu trên cùng biến làm lượt giải kết thúc với `UNSAT`.

`propagate()` đọc từng literal trực tiếp từ `cnf.clauses`. Một literal
có biến đã gán được xem là đúng khi `assignment[abs(literal)]` bằng
`(literal > 0)`. Nếu gặp literal đúng, vòng lặp trong dùng `break` và
chuyển sang mệnh đề kế tiếp. Khối `else` của vòng `for` chỉ chạy khi đã
quét hết mệnh đề mà chưa thấy literal đúng. Khi đó, hàm xử lý như sau.

- Nếu `unassigned_literal` vẫn là `None`, mọi literal đều sai hoặc mệnh
  đề rỗng. Hàm báo mâu thuẫn bằng `(False, None)`.
- Nếu chỉ có một literal phân biệt chưa gán, hàm gán giá trị làm literal
  đó đúng, tăng `propagations` và đặt `changed = True`. Ví dụ, `[1, 1]`
  vẫn là mệnh đề đơn vị vì cả hai vị trí chứa cùng literal.
- Nếu còn từ hai literal phân biệt trở lên, hàm ghi nhận biến chưa gán
  đầu tiên của mệnh đề chưa giải quyết đầu tiên để có thể phân nhánh.

Khi `changed` là `True`, hàm quét lại từ đầu vì phép gán mới có thể biến
một mệnh đề đã quét thành mệnh đề đơn vị. Khi không còn phép gán mới,
`propagate()` trả `(True, branch_variable)`. Nếu `branch_variable` là
`None`, mọi mệnh đề đã có ít nhất một literal đúng. `search()` tạo mô
hình đầy đủ bằng cách đọc từng biến từ 1 đến `cnf.num_vars` và điền
`False` cho các biến còn tự do. Các mệnh đề đã thỏa vẫn giữ literal đúng
sau phép điền này.

=== Phân nhánh, quay lui và thời hạn

Theo §4.3 của đề, DPLL phân nhánh và quay lui theo cấu trúc đệ quy. Bản
Python biểu diễn các nhánh chưa thử bằng ngăn xếp `alternatives` và duyệt
theo chiều sâu. Trước khi thử `True`, `search()` lưu biến phân nhánh và
số phép gán hiện có. Nếu nhánh đó mâu thuẫn, hàm lấy điểm lưu gần nhất,
gọi `dict.popitem()` cho đến khi `assignment` trở về kích thước đã lưu,
rồi gán biến vừa lấy thành `False`. Vì từ điển giữ thứ tự chèn, bước này
hoàn tác cả phép gán thử lẫn các phép lan truyền phát sinh sau nó. Các
giả định và phép gán đã có trước điểm lưu được giữ lại. Nếu mâu thuẫn
xuất hiện khi ngăn xếp rỗng, bộ giải kết luận `UNSAT`.

```python
elif alternatives:
    branch_variable, checkpoint = alternatives.pop()
    while len(assignment) > checkpoint:
        check_deadline()
        assignment.popitem()
    assignment[branch_variable] = False
    backtracks += 1
```

Lan truyền đơn vị chỉ thêm các giá trị mà mọi nghiệm của nhánh hiện tại
đều phải thỏa. Quay lui cho phép xét nhánh còn lại sau khi một nhánh mâu
thuẫn. Với cùng thứ tự mệnh đề và literal, bộ giải luôn chọn biến theo
cùng thứ tự. Trong trường hợp xấu, số nhánh có thể tăng theo hàm mũ của
số biến. Mỗi lượt lan truyền quét danh sách mệnh đề nên chi phí còn phụ
thuộc kích thước CNF.

`check_deadline()` so sánh đồng hồ với thời điểm hết hạn khi đọc giả
định, quét literal, hoàn tác và hoàn tất mô hình. Khi quá hạn, ngoại lệ
nội bộ `_DeadlineExceeded` đưa bộ giải đến nhánh `TIMEOUT` với
`model = None` và các chỉ số đã thu thập. `decisions` đếm số giá trị
phân nhánh đã thử, `propagations` đếm số phép gán từ mệnh đề đơn vị,
`backtracks` đếm số lần khôi phục để thử nhánh `False`, và `runtime_ms`
là thời gian từ lúc vào `solve()` tới lúc lập kết quả.

== Cơ sở tri thức và suy diễn trong `reasoning/`

=== Tri thức công khai và chuyển đổi sang CNF

`knowledge.py` dùng `PublicKnowledge` để lưu phần dữ liệu cần cho suy
diễn tại một thời điểm của ván chơi. `puzzle_id` và `size` nhận diện
bàn chơi. `revealed_clues` lưu các manh mối đã mở và `proved_verdicts`
ánh xạ tọa độ sang trạng thái đã biết.

```python
@dataclass(frozen=True)
class PublicKnowledge:
    puzzle_id: str
    size: int
    revealed_clues: tuple[Clue, ...]
    proved_verdicts: dict[Coord, Status]
```

`PublicKnowledge.from_public_state(state)` đọc các ô từ `PublicState`.
Hàm tạo một từ điển mới, chỉ đưa vào các ô có `revealed = True` và
`status` khác `None`, sau đó lấy `revealed_clues` từ cùng trạng thái.
Đây là dữ liệu tác tử và chức năng gợi ý dùng để dựng cơ sở tri thức
công khai trong lúc chơi.

```python
def build_kb_cnf(
    kb: PublicKnowledge,
    varmap: VarMap | None = None,
    direct_threshold: int = 64,
) -> tuple[CNF, VarMap, EncodingStats]:
    ...
```

`kb_builder.py` tạo `VarMap(kb.size)` khi hàm chưa nhận một ánh xạ.
Hàm truyền `varmap` và `direct_threshold` cho `Encoder`, rồi gọi
`encode(kb.revealed_clues)`. Với mỗi phán quyết đã biết, hàm tra
`varmap.coord_to_var(coord)` và thêm mệnh đề đơn vị `[i]` nếu ô là
`CRIMINAL` hoặc `[-i]` nếu ô là `INNOCENT`. Kết quả gồm CNF của cả
manh mối lẫn verdict, ánh xạ dùng để chọn biến cho truy vấn sau và
`EncodingStats`. Số biến chính và phụ lấy từ encoder. Số mệnh đề
được đếm lại sau khi thêm verdict.

Trong trạng thái ban đầu của `json_example.json`, A1 đã mở với trạng
thái `CRIMINAL`. Manh mối đang mở quy định hàng A1, B1 và C1 có đúng
một `CRIMINAL`. Ba ô lần lượt có ID biến 1, 2 và 3. Encoder sinh
`[[-1, -2], [-1, -3], [-2, -3], [1, 2, 3]]` cho manh mối, sau đó
`build_kb_cnf()` thêm `[1]` cho verdict của A1. CNF công khai có 9 biến
chính, 0 biến phụ và 5 mệnh đề. Từ đó suy ra B1 và C1 là `INNOCENT`.

=== Phân loại trạng thái bằng hai truy vấn SAT

Trong `entailment.py`, `check_kb_consistent(cnf_kb, solver, deadline)`
gọi solver với `assumptions=()` và trả `SatStatus`. Tác tử gọi hàm này
ở đầu mỗi lượt suy diễn. `classify(cnf_kb, var_id, solver, deadline)`
thử giả định `-var_id` rồi `var_id` trên cùng CNF, chuyển cùng
`deadline` vào từng truy vấn.

Mỗi truy vấn được lưu trong `SatQuery`, gồm `var_id: int`,
`assumed_literal: int` và `status: SatStatus`. Hàm trả
`ClassifyOutcome(classification, queries)`, với nhãn có kiểu
`Classification` và `queries: tuple[SatQuery, ...]`. Tác tử dùng
chuỗi truy vấn này để lưu căn cứ SAT vào trace. Nếu truy vấn đầu hết
hạn, tuple chỉ chứa truy vấn đã thực hiện.

- Nếu chỉ truy vấn với `-i` là `UNSAT`, ô $i$ bắt buộc là `CRIMINAL`.
- Nếu chỉ truy vấn với `i` là `UNSAT`, ô $i$ bắt buộc là `INNOCENT`.
- Nếu cả hai truy vấn là `SAT`, kết quả là `UNKNOWN`. Nếu cả hai là `UNSAT`,
  kết quả là `INCONSISTENT`.
- Nếu một truy vấn hết hạn, kết quả là `TIMEOUT`.

Ví dụ, với $(C_A ∨ C_B) ∧ (¬ C_A ∨ C_B)$, giả định $¬ C_B$ buộc $C_A$ và
$¬ C_A$ đồng thời đúng. Do đó ô B là `CRIMINAL`. Cả hai giá trị của $C_A$
đều có mô hình thỏa khi $C_B$ đúng, nên ô A là `UNKNOWN`.

Với CNF công khai của puzzle mẫu, truy vấn B1 nhận `SAT` cho `[-2]`
và `UNSAT` cho `[2]`. Trace của kết luận `INNOCENT` vì thế chứa cả hai
kết quả. Ô A2 nhận `SAT` cho cả `[-4]` và `[4]`, nên tại thời điểm đó
dữ kiện công khai chỉ cho phép kết luận `UNKNOWN`.

=== Kiểm tra nghiệm duy nhất trên các biến chính

`uniqueness.py` cung cấp hàm
`check_uniqueness(cnf, num_primary_vars, solver, deadline)` cho trình
kiểm tra puzzle offline. Đầu vào của trình kiểm tra này là CNF của
toàn bộ tập manh mối. `UniquenessOutput` chứa `result` kiểu
`UniquenessResult`, `first_model: dict[int, bool] | None` và
`stats: SolverStats | None`. Trường `stats` lấy từ truy vấn quyết định
kết quả, tức là truy vấn cuối cùng đã chạy.

Khi lượt đầu tìm được mô hình, hàm thêm vào bản sao CNF một mệnh đề
chặn gồm các literal đảo dấu của những biến chính trong mô hình đó.
Lượt thứ hai trả `UNSAT` thì nghiệm chính là `UNIQUE`. Nếu trả `SAT`,
có ít nhất hai nghiệm chính và kết quả là `MULTIPLE`. `UNSAT` ở lượt
đầu biểu thị công thức vô nghiệm. Hai lượt dùng chung `deadline`.
Khi lượt hai trả `TIMEOUT`, kết quả giữ mô hình tìm được từ lượt đầu.

Hàm duyệt các biến từ `1` đến `num_primary_vars`. Biến $i$ nhận `True`
trong mô hình đầu tạo literal `-i` và biến nhận `False` tạo literal `i`.
Để thỏa mệnh đề chặn, mô hình kế tiếp phải làm đúng ít nhất một literal
trong mệnh đề, tức là phải đổi giá trị của ít nhất một ô.

=== Vòng lặp suy diễn của tác tử

`LogicAgent.iter_steps()` đọc `PublicState` qua giao diện `PublicGame`
ở đầu mỗi lượt (*wave*). Tác tử dựng CNF công khai và kiểm tra tính
nhất quán. Nếu CNF vô nghiệm, lượt giải dừng ở `INCONSISTENT`. Nếu
hết hạn, lượt giải dừng ở `TIMEOUT`. Với CNF thỏa được, tác tử duyệt
theo thứ tự hàng rồi cột để tìm ô chưa mở đầu tiên có trạng thái bị
ép. Nếu duyệt hết mà mọi ô đều `UNKNOWN`, kết quả là `STUCK`.

Một ô bị ép dẫn đến một bước (*step*) gọi `submit_verdict()`. Trace
ghi số lượt, số bước, danh sách clue đang mở, kết quả hai truy vấn,
kết quả nộp verdict và ID clue vừa lật. Khi verdict được chấp nhận,
lượt sau lấy `PublicState` mới để dựng lại CNF. Khi mọi ô đã mở, kết
quả là `SOLVED`. `CountingSolver` tích lũy số gọi của tác tử, gồm
kiểm tra tính nhất quán và các truy vấn phân loại đã thực hiện.

== Thiết kế kiểm thử

=== Kiểm thử bộ giải DPLL

Bộ `test_dpll.py` kết hợp các CNF có kết quả tính được bằng tay, vét cạn
độc lập và mô phỏng đồng hồ. Mỗi phương pháp kiểm chứng một nhóm hành vi
cụ thể của `solve()`.

*Ca cơ sở và trạng thái giữa các lượt giải.* Với `[[1, 2], [-1, 2]]`, bộ
giải phải trả `SAT` và gán biến 2 bằng `True`. Hai mệnh đề `[[1], [-1]]`
mâu thuẫn nên phải trả `UNSAT`. Khi thêm giả định `[-1, -2]` vào `[[1, 2]]`,
cả hai literal đều sai và kết quả cũng là `UNSAT`. Ca kiểm thử biên so
sánh CNF rỗng `[]` cho `SAT` với mô hình `{}` và CNF chứa mệnh đề rỗng
`[[]]` cho `UNSAT`. Ca tái sử dụng solver gọi lần lượt với `[1, -1]` và
`[-1, 2, 2]` trên cùng đối tượng. Lượt sau phải trả mô hình
`{1: False, 2: True}` với 0 phép lan truyền, qua đó kiểm tra tính cục bộ
của phép gán và bộ đếm.

*Lan truyền qua nhiều lượt quét.* CNF `[[-2, 3], [-1, 2], [1, 1]]` được
khai báo với 4 biến. Lượt quét đầu gặp `[1, 1]` ở cuối và gán biến 1
bằng `True`. Lượt kế tiếp dùng `[-1, 2]` để gán biến 2, rồi lượt tiếp
theo dùng `[-2, 3]` để gán biến 3. Test yêu cầu mô hình có đủ bốn biến
với biến 4 bằng `False`, 3 lần lan truyền và 0 quyết định. Đây là ca
kiểm tra đồng thời việc xử lý literal lặp, quét lại và hoàn tất mô hình.

*Quay lui sau mâu thuẫn.* Với `[[-1, 2], [-1, -2], [1, 3]]`, nhánh gán
biến 1 bằng `True` làm `[-1, 2]` ép biến 2 bằng `True`, khiến `[-1, -2]`
sai. Khi quay lui, bộ giải xóa cả hai phép gán phát sinh trong nhánh này.
Nhánh gán biến 1 bằng `False` làm `[1, 3]` ép biến 3 bằng `True`. Test
yêu cầu mô hình `{1: False, 2: False, 3: True}`, 2 quyết định, 2 lần lan
truyền và 1 lần quay lui. Việc đối chiếu với bản sao CNF xác nhận lượt
giải giữ nguyên công thức đầu vào.

*Đối chiếu với vét cạn.* Test dùng `Random(7)` để chọn 30 CNF cho mỗi
số biến từ 1 đến 6, tổng cộng 180 CNF. Mỗi CNF có từ 0 đến 12 mệnh đề,
mỗi mệnh đề có từ 1 đến 4 literal, và mỗi lượt giải có từ 0 đến 2 giả
định. Nhánh vét cạn chuyển giả định thành mệnh đề đơn vị, rồi duyệt
`product((False, True), repeat=num_vars)`. Hàm `_satisfies()` dùng
`all()` trên các mệnh đề và `any()` trên literal trong từng mệnh đề để
xác định có mô hình hay không. Khi DPLL trả `SAT`, test còn kiểm tra mô
hình có đủ khóa từ 1 đến `num_vars` và thỏa từng mệnh đề cùng giả định.
Với `UNSAT`, test kiểm tra `model is None`.

*Kiểm thử thời hạn.* Ca thứ nhất dùng một deadline trong quá khứ ngay
cả với CNF rỗng. Ca thứ hai thay đồng hồ của module DPLL bằng một bộ đếm
tăng dần với `monkeypatch`, rồi giải CNF có 100 mệnh đề đơn vị với
`deadline = 20.0`. Kết quả kỳ vọng là `TIMEOUT`, `model is None` và
`0 < propagations < 100`. Điều kiện cuối xác nhận bộ giải đã thực hiện
công việc và dừng giữa quá trình lan truyền, đồng thời còn giữ thống kê.

=== Kiểm thử tính duy nhất

`test_uniqueness.py` dùng DPLL thật cho năm ca và dùng một solver mô phỏng
cho ca hết hạn ở truy vấn thứ hai. Ba ca cơ sở dùng `[[1], [-2]]` để
kiểm tra `UNIQUE` và mô hình đầu, `[[1, 2]]` để kiểm tra `MULTIPLE`,
và `[[1], [-1]]` để kiểm tra `UNSAT` ngay ở lượt đầu.

Ca biến phụ dùng `[[1], [-2], [3, 4], [-3, -4]]` với hai biến chính.
Trước tiên, test gọi DPLL với `[3]` và `[-3]` để xác nhận tồn tại cả hai
cách gán biến phụ. Hai cách gán đều có biến 1 bằng `True` và biến 2 bằng
`False`. Mệnh đề chặn `[-1, 2]` làm truy vấn thứ hai vô nghiệm, nên
kết quả phải là `UNIQUE`. Test cũng so sánh CNF với bản sao tạo trước
khi kiểm tra.

Để kiểm tra `TIMEOUT` ở lượt đầu, test đưa một deadline đã qua cho
DPLL thật và kiểm tra `first_model` là `None`. Để kiểm tra lượt thứ
hai, test dùng `create_autospec(SatSolver, instance=True)` và đặt
`side_effect` lần lượt là kết quả `SAT` thực tế và một kết quả
`TIMEOUT` có thống kê định sẵn. `call_args_list` xác nhận cả hai truy
vấn nhận `assumptions=()` và cùng `deadline=42.0`. Truy vấn thứ hai
phải nhận `[[1], [-2], [-1, 2]]`. Mệnh đề chặn gồm hai biến chính.
Test kiểm tra kết quả cuối giữ mô hình đầu tiên và thống kê của lượt
hết hạn.

=== Kiểm thử chéo encoder và hàm ngữ nghĩa

`test_encoder_vs_eval.py` dựng đối tượng clue trực tiếp để kiểm tra
cùng một manh mối theo hai cách. Kết quả kỳ vọng đến từ
`evaluate()` trên phép gán cụ thể. Kết quả đối chiếu đến từ truy vấn
SAT trên CNF do encoder tạo.

Với mỗi clue, `_assert_encoder_matches_evaluator()` tạo một `VarMap`
cho lưới 3 × 3 và mã hóa clue một lần. Hàm duyệt $2^9 = 512$ phép gán
của toàn bộ biến chính. Mỗi ô mang `True` sinh literal giả định dương,
ô mang `False` sinh literal âm. DPLL tìm phép gán cho những biến phụ
còn tự do. Test yêu cầu `SAT` khi `evaluate()` trả `True` và `UNSAT`
khi trả `False`. Nếu lệch, thông báo kiểm thử nêu rõ clue và toàn bộ
phép gán gây lệch. Chẳng hạn, với `EXACTLY(1)` trên hàng A1, B1, C1,
phép gán `(True, False, False)` phải cho `SAT`, còn
`(True, True, False)` phải cho `UNSAT`, với các ô khác được cố định
theo từng phép thử.

Mã hóa trực tiếp được kiểm tra với cả hai trạng thái của `FACT`,
`SAME`, `DIFFERENT`, ba clue đếm trên hàng đầu và `PARITY` theo cả
chẵn lẫn lẻ. Ba ca Sequential Counter dùng lại `EXACTLY(1)`,
`AT_LEAST(2)` và `AT_MOST(1)`, truyền `direct_threshold=0` để yêu cầu
encoder chuyển sang nhánh mã hóa này theo ngưỡng hiện tại.

Ngữ nghĩa `COMPOUND` được kiểm tra riêng bằng bảng chân trị. Đặt $A$ là
phán đoán A1 là `CRIMINAL` và $B$ là phán đoán tương ứng cho B1. Test
so sánh cả bốn kết quả của `evaluate()` với từng cột kỳ vọng dưới đây.
Ba biểu thức này cũng được đưa vào bộ đối chiếu CNF.

#styled_table(
  (1fr, 1fr, 1.3fr, 1.5fr, 1.3fr),
  ([$A$], [$B$], [$A ∧ B$], [$(¬ A) ∨ B$], [$¬ A$]),
  (
    [`False`], [`False`], [`False`], [`True`], [`True`],
    [`False`], [`True`], [`False`], [`True`], [`True`],
    [`True`], [`False`], [`False`], [`False`], [`False`],
    [`True`], [`True`], [`True`], [`True`], [`False`],
  ),
  caption: [Kết quả kỳ vọng khi kiểm tra ngữ nghĩa của `COMPOUND`],
)

== Kết quả kiểm thử, thực nghiệm và giới hạn

=== Kết quả kiểm thử tự động

Kết quả được ghi trên nhánh `feature/dpll-solver` tại phiên bản `4208ff0`,
chạy bằng Python 3.12 và pytest từ thư mục `Source/`.

#styled_table(
  (1.25fr, 0.5fr, 0.7fr, 2.7fr),
  ([Bộ kiểm thử], [Đạt], [`xfail`], [Nội dung kiểm chứng]),
  (
    [DPLL], [10], [0], [Lan truyền, quay lui, giả định, timeout và đối chiếu 180 CNF có từ 1 đến 6 biến với vét cạn.],
    [Uniqueness], [6], [0], [Bốn trạng thái kết quả, chặn đúng biến chính và giữ nguyên CNF đầu vào.],
    [Encoder và evaluator], [12], [6], [Sáu loại clue cơ bản, `PARITY` và bảng chân trị của `COMPOUND`.],
  ),
  align: (left + horizon, center + horizon, center + horizon, left + horizon),
  caption: [Kết quả của ba bộ kiểm thử trong phần việc của Võ Nhật Minh],
)

Ba ca `COMPOUND` chạy trực tiếp trên `evaluate()` đã qua bảng chân trị.
Sáu ca `xfail` gồm ba ca chờ Sequential Counter và ba ca chờ encoder
`COMPOUND`. Mỗi nhóm dùng `xfail(raises=NotImplementedError)`. Khi chạy
lại với `--runxfail`, cả sáu ca dừng tại `NotImplementedError` từ hai
hàm mã hóa tương ứng. Những lượt này chưa có CNF để đối chiếu trên 512
phép gán.

=== Thực nghiệm trên puzzle mẫu

Chạy `run_benchmark_on_puzzle()` năm lần trên `json_example.json`
ở Windows 11, Python 3.12.1 và `PYTHONHASHSEED=0`. Mỗi lần chạy có
thời hạn suy diễn 30 giây. Các bộ đếm và trạng thái giống nhau qua
năm lần. Các số thời gian là trung vị theo từng phép đo. Thời gian
tổng được tính từ tổng thời gian mã hóa và suy diễn của từng lần.

#styled_table(
  (1.55fr, 2.95fr),
  ([Chỉ số], [Kết quả trên `json-example-3x3`]),
  (
    [Biến chính và biến phụ], [9 biến chính, 0 biến phụ],
    [Mệnh đề CNF], [15 mệnh đề của toàn bộ tập manh mối],
    [Truy vấn SAT], [26 lượt do `CountingSolver` của tác tử ghi nhận],
    [Chỉ số DPLL], [0 quyết định, 123 lần lan truyền, 0 lần quay lui],
    [Bước và lượt suy diễn], [8 bước, 8 lượt],
    [Thời gian trung vị], [Mã hóa 0,036 ms, suy diễn 1,730 ms, tổng 1,850 ms],
    [Kết quả auto-solve], [`SOLVED` trong cả năm lần],
    [Kiểm tra tính duy nhất offline], [`MULTIPLE`, vét cạn tìm được 3 nghiệm],
  ),
  align: (left + horizon, left + horizon),
  inset: 5pt,
  caption: [Sáu nhóm chỉ số và kết quả kiểm tra puzzle mẫu 3 × 3],
)

Tác tử suy ra đủ 8 ô còn lại từ trạng thái ban đầu đã mở A1. Trong
lần đo này, lan truyền đơn vị và phát hiện mâu thuẫn giải quyết các
truy vấn mà không cần phân nhánh. Phạm vi của 26 lượt gọi là solver
của tác tử. `GameEngine` có solver riêng để xác nhận verdict khi tác
tử nộp phán quyết.

Trình kiểm tra offline trả lỗi tính duy nhất `MULTIPLE` vì xét CNF
của toàn bộ tập manh mối. Đối chiếu vét cạn qua `evaluate()` xác nhận
có 3 cách gán thỏa tập manh mối đó. Trong luồng chơi, tri thức ban
đầu còn có phán quyết A1 là `CRIMINAL`. Hai phép kiểm chứng dùng
đầu vào khác nhau, nên bảng ghi cả `SOLVED` lẫn `MULTIPLE`.

=== Giới hạn kiểm chứng

Kho puzzle của phiên bản này có một JSON mẫu kích thước 3 × 3. Các
số đo trên hỗ trợ kiểm chứng luồng chạy trên mẫu này. Đánh giá theo
§4.5 của đề cần thêm các puzzle 3 × 3 và 4 × 4 đã qua kiểm tra đầu
vào. Với vùng đếm lớn, số mệnh đề của mã hóa trực tiếp có thể tăng
nhanh theo số tổ hợp. Khả năng dùng biến phụ và chi phí của Sequential
Counter cần được đo lại sau khi encoder hoàn thiện. Các ca timeout
trong bộ kiểm thử xác nhận hành vi trả kết quả và bảo toàn thống kê.

== Kết luận

Bộ giải DPLL đã thỏa các ca kiểm chứng về mô hình đầy đủ, mâu thuẫn,
quay lui và xử lý thời hạn. Hai truy vấn SAT theo hai dấu của biến cho phép
tác tử xác định khi nào một trạng thái thực sự được suy ra. Phép chặn chỉ
trên biến chính cho phép kiểm tra tính duy nhất của nghiệm trên bàn cờ.
Bước kiểm chứng còn lại là chạy sáu ca tích hợp sau khi encoder hoàn thiện
Sequential Counter và `COMPOUND`. Kết quả trên puzzle 3 × 3 là dữ liệu
kiểm chứng luồng chạy của phiên bản hiện tại.

#heading(level: 2, outlined: false)[Nguồn và ghi nhận hỗ trợ AI]

Quy ước về tri thức công khai, điều kiện suy diễn, kiểm tra nghiệm và
các nhóm số đo dựa trên đề *CSC14003 – Project 2: Griductive Solver*,
§3.4 và §4.3–4.6. Thủ tục DPLL được dẫn nguồn tại mục cài đặt.

Codex được dùng để rà soát bộ kiểm thử, đối chiếu cơ chế mã hóa với
evaluator và soạn phần Typst. Các yêu cầu tiêu biểu gồm “kiểm lại file
test encoder” và “bổ sung thêm viết thêm báo cáo logic và khai báo
của các folder tôi được phân công”. Thông tin đưa vào báo cáo được
đối chiếu với mã nguồn, kết quả `pytest` và lượt chạy mẫu tại phiên
bản đã ghi ở phần kết quả.
