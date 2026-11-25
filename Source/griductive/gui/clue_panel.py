"""Clue panel widget displaying revealed clues and friendly descriptions.

Tác dụng:
    Hiển thị danh sách các manh mối đã được lật mở:
    - Tự động sinh mô tả tự nhiên, thân thiện từ các trường dữ liệu của Clue
      (không dùng trường text tĩnh lưu trong domain theo quy định).
    - Hỗ trợ đủ 6 clue lõi + PARITY, COMPOUND, COMPARE_COUNT.
    - Sắp xếp clue theo thứ tự row-major của ô sở hữu để thứ tự luôn ổn định.
    - Khi người dùng click chọn 1 clue: phát tín hiệu clue_selected(cells)
      để BoardView highlight các ô cờ liên quan.

Input:
    Tuple các đối tượng Clue đã được mở từ PublicState.revealed_clues.

Output:
    Tín hiệu pyqtSignal(tuple) gửi danh sách ô cần highlight cho BoardView.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
from griductive.clues.base import Clue
from griductive.clues.core import AtLeastClue, AtMostClue, DifferentClue, ExactlyClue, FactClue, SameClue
from griductive.clues.extensions import CompareCountClue, CompoundClue, ParityClue
from griductive.domain.grid import Coord, parse_coord

_OP_WORDS = {"AND": "VÀ", "OR": "HOẶC"}
_COMPARE_WORDS = {"GREATER": "NHIỀU HƠN", "LESS": "ÍT HƠN", "EQUAL": "BẰNG"}


def _region_text(cells: tuple[Coord, ...]) -> str:
    """Mô tả ngắn gọn một vùng ô, ví dụ: 'vùng gồm A1, B1, C1'."""
    return "vùng gồm " + ", ".join(cells)


def _describe_body(clue: Clue) -> str:
    """Mô tả nội dung clue (không kèm tiền tố chủ sở hữu)."""
    if isinstance(clue, FactClue):
        return f"{clue.target_cell} là {clue.target_status.value}."
    if isinstance(clue, SameClue):
        return f"{clue.cell_a} và {clue.cell_b} có CÙNG trạng thái."
    if isinstance(clue, DifferentClue):
        return f"{clue.cell_a} và {clue.cell_b} KHÁC trạng thái nhau."
    if isinstance(clue, ExactlyClue):
        return f"Có ĐÚNG {clue.k} Criminal trong {_region_text(clue.region_cells)}."
    if isinstance(clue, AtLeastClue):
        return f"Có ÍT NHẤT {clue.k} Criminal trong {_region_text(clue.region_cells)}."
    if isinstance(clue, AtMostClue):
        return f"Có NHIỀU NHẤT {clue.k} Criminal trong {_region_text(clue.region_cells)}."
    if isinstance(clue, ParityClue):
        word = "CHẴN" if clue.parity == "EVEN" else "LẺ"
        return f"Số Criminal trong {_region_text(clue.region_cells)} là số {word}."
    if isinstance(clue, CompoundClue):
        subs = [_describe_body(sub).rstrip(".") for sub in clue.sub_clues]
        if clue.op == "NOT" and subs:
            return f"KHÔNG phải: ({subs[0]})."
        joiner = f" {_OP_WORDS.get(clue.op, clue.op)} "
        return joiner.join(f"({s})" for s in subs) + "."
    if isinstance(clue, CompareCountClue):
        word = _COMPARE_WORDS.get(clue.op, clue.op)
        return (
            f"Số Criminal trong {_region_text(clue.region_left_cells)} {word} "
            f"số Criminal trong {_region_text(clue.region_right_cells)}."
        )
    return f"Manh mối loại {clue.clue_type}."


def format_clue_description(clue: Clue) -> str:
    """Tự động sinh chuỗi mô tả thân thiện cho clue (kèm ô sở hữu)."""
    return f"[{clue.owner}] {_describe_body(clue)}"


def _row_major_key(clue: Clue) -> tuple[int, int]:
    col, row = parse_coord(clue.owner)
    return row, col


class CluePanel(QWidget):
    """Bảng hiển thị danh sách các manh mối đã phát hiện."""

    clue_selected = pyqtSignal(tuple)  # tuple[Coord, ...]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel("<b>DANH SÁCH MANH MỐI ĐÃ MỞ</b>", self)
        self.hint_label = QLabel("Chọn một manh mối để tô sáng các ô liên quan.", self)
        self.hint_label.setWordWrap(True)
        self.list_widget = QListWidget(self)
        self.list_widget.setWordWrap(True)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.hint_label)
        self.layout.addWidget(self.list_widget)

        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self._current_clues: list[Clue] = []

    def set_clues(self, clues: tuple[Clue, ...]) -> None:
        """Cập nhật danh sách clue hiển thị (sắp xếp theo ô sở hữu, row-major)."""
        self.list_widget.clear()
        self._current_clues = sorted(clues, key=_row_major_key)
        for clue in self._current_clues:
            self.list_widget.addItem(QListWidgetItem(format_clue_description(clue)))

    def clues(self) -> tuple[Clue, ...]:
        """Các clue đang hiển thị, theo đúng thứ tự trong danh sách."""
        return tuple(self._current_clues)

    def find_clues(self, clue_ids: tuple[str, ...]) -> tuple[Clue, ...]:
        """Tìm các clue đang hiển thị theo id (dùng cho Hint)."""
        wanted = set(clue_ids)
        return tuple(c for c in self._current_clues if c.id in wanted)

    def select_owner(self, owner: Coord | None) -> None:
        """Chọn (tô nền) clue của ô `owner`, ví dụ clue vừa được lật; không phát tín hiệu."""
        self.list_widget.clearSelection()
        if owner is None:
            return
        for idx, clue in enumerate(self._current_clues):
            if clue.owner == owner:
                self.list_widget.setCurrentRow(idx)
                self.list_widget.scrollToItem(self.list_widget.item(idx))
                return

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Xử lý khi người dùng click vào một clue trong danh sách."""
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self._current_clues):
            target_cells = self._current_clues[idx].cells()
            self.clue_selected.emit(target_cells)
