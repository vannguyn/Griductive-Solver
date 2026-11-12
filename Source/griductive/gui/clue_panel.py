"""Clue panel widget displaying revealed clues and friendly descriptions.

Tác dụng:
    Hiển thị danh sách các manh mối đã được lật mở:
    - Tự động sinh mô tả tự nhiên, thân thiện từ các trường dữ liệu của Clue
      (không dùng trường text tĩnh lưu trong domain theo quy định).
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
from griductive.domain.grid import Coord


def format_clue_description(clue: Clue) -> str:
    """Tự động sinh chuỗi mô tả thân thiện cho clue."""
    if isinstance(clue, FactClue):
        return f"[{clue.owner}] {clue.target_cell} là {clue.target_status.value}."
    elif isinstance(clue, SameClue):
        return f"[{clue.owner}] {clue.cell_a} và {clue.cell_b} có CÙNG trạng thái."
    elif isinstance(clue, DifferentClue):
        return f"[{clue.owner}] {clue.cell_a} và {clue.cell_b} KHÁC trạng thái nhau."
    elif isinstance(clue, ExactlyClue):
        return f"[{clue.owner}] Có ĐÚNG {clue.k} Criminal trong vùng ({len(clue.region_cells)} ô)."
    elif isinstance(clue, AtLeastClue):
        return f"[{clue.owner}] Có ÍT NHẤT {clue.k} Criminal trong vùng."
    elif isinstance(clue, AtMostClue):
        return f"[{clue.owner}] Có NHIỀU NHẤT {clue.k} Criminal trong vùng."
    return f"[{clue.owner}] Manh mối loại {clue.clue_type}."


class CluePanel(QWidget):
    """Bảng hiển thị danh sách các manh mối đã phát hiện."""

    clue_selected = pyqtSignal(tuple)  # tuple[Coord, ...]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.title_label = QLabel("<b>DANH SÁCH MANH MỐI ĐÃ MỞ</b>", self)
        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.list_widget)

        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self._current_clues: list[Clue] = []

    def set_clues(self, clues: tuple[Clue, ...]) -> None:
        """Cập nhật danh sách clue hiển thị."""
        self.list_widget.clear()
        self._current_clues = list(clues)
        for clue in clues:
            item_text = format_clue_description(clue)
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Xử lý khi người dùng click vào một clue trong danh sách."""
        idx = self.list_widget.row(item)
        if 0 <= idx < len(self._current_clues):
            target_cells = self._current_clues[idx].cells()
            self.clue_selected.emit(target_cells)
