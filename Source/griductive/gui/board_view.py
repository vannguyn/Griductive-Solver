"""Board view widget rendering the N x N grid and character cards.

Tác dụng:
    Hiển thị giao diện trực quan của lưới bàn cờ N x N:
    - Vẽ các ô cờ với hiệu ứng lật thẻ (card flip).
    - Hiển thị tên nhân vật, nghề nghiệp, và trạng thái (Úp hoặc Ngửa: CRIMINAL / INNOCENT).
    - Highlight trực quan các ô cờ liên quan khi người dùng click vào một clue ở CluePanel.
    - Bắt sự kiện click chuột của người dùng để nộp verdict.

Input:
    PublicState từ GameSession.

Output:
    Tín hiệu Qt (pyqtSignal) khi người dùng thao tác click ô (cell_clicked).

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState
from griductive.domain.types import Status


class BoardView(QWidget):
    """Widget hiển thị lưới bàn cờ và nhân vật."""

    cell_submitted = pyqtSignal(str, object)  # (coord, Status)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self._cell_widgets: dict[Coord, QPushButton] = {}
        self._highlighted_cells: set[Coord] = set()

    def update_board(self, state: PublicState) -> None:
        """Cập nhật toàn bộ giao diện lưới theo PublicState mới."""
        # Xóa các widget cũ nếu kích thước thay đổi
        # TODO (Gia Hưng): Tạo các CardWidget có animation flip, avatar, và màu sắc
        pass

    def highlight_cells(self, coords: tuple[Coord, ...]) -> None:
        """Highlight viền màu nổi bật cho các ô có trong coords."""
        self._highlighted_cells = set(coords)
        # TODO (Gia Hưng): Áp dụng style QSS viền vàng/xanh cho các ô này
        pass

    def clear_highlights(self) -> None:
        """Xóa toàn bộ hiệu ứng highlight."""
        self._highlighted_cells.clear()
        # TODO (Gia Hưng): Khôi phục style mặc định
        pass
