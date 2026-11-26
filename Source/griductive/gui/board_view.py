"""Board view widget rendering the N x N grid and cozy character cards.

Tác dụng:
    Hiển thị giao diện trực quan của lưới bàn cờ N x N:
    - Bố cục lưới thẻ nhân vật căn giữa sang trọng, tự co giãn mượt mà.
    - Sử dụng CharacterCardWidget với avatar chân dung minh họa riêng biệt.
    - Hiệu ứng lật thẻ (3D flip) và rung lắc (shake) phản hồi trực quan.
    - Hỗ trợ spotlight manh mối: Chủ thể (Subject), Mục tiêu (Target) và Làm mờ (Dimmed).
    - Mở hộp thoại thẩm vấn VerdictDialog khi click vào thẻ chưa mở.

Input:
    PublicState từ GameSession.

Output:
    Tín hiệu Qt:
    - cell_submitted(coord, Status): khi người chơi đưa ra phán quyết
    - cell_inspected(coord): khi người chơi click vào thẻ đã giải để xem manh mối.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from griductive.domain.grid import Coord, parse_coord
from griductive.domain.public_state import PublicCell, PublicState
from griductive.domain.types import Status
from griductive.gui.card_widget import CharacterCardWidget
from griductive.gui.verdict_dialog import VerdictDialog


class BoardView(QWidget):
    """Widget hiển thị lưới bàn cờ và hệ thống thẻ nhân vật Grid Detective."""

    cell_submitted = pyqtSignal(str, object)  # (coord, Status)
    cell_inspected = pyqtSignal(str)          # coord (khi click vào ô đã lật)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._root_layout.setContentsMargins(16, 16, 16, 16)

        self._container = QWidget(self)
        self.grid_layout = QGridLayout(self._container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._root_layout.addWidget(self._container)

        self._card_widgets: dict[Coord, CharacterCardWidget] = {}
        self._header_widgets: list[QLabel] = []
        self._cells: dict[Coord, PublicCell] = {}
        self._size = 0
        self._puzzle_id: str | None = None
        self._input_enabled = True

    # ------------------------------------------------------------------ API
    def update_board(self, state: PublicState) -> None:
        """Cập nhật toàn bộ giao diện lưới theo PublicState mới."""
        # Khi đổi puzzle cùng kích thước (ví dụ tutorial 3x3 -> case 3x3),
        # không được tái sử dụng các thẻ cũ. Nếu tái sử dụng, một ô vừa được
        # lật trong puzzle mới có thể bị coi là đang flip từ puzzle trước và
        # bị giữ ở trạng thái co ngang.
        if (
            state.puzzle_id != self._puzzle_id
            or state.size != self._size
            or not self._card_widgets
        ):
            self._rebuild(state)
            return

        for cell in state.cells:
            widget = self._card_widgets.get(cell.coord)
            if widget is not None:
                widget.set_cell_data(cell, animate_flip_if_new=True)
            self._cells[cell.coord] = cell

    def highlight_cells(self, coords: tuple[Coord, ...]) -> None:
        """Highlight viền màu nổi bật cho các ô có trong coords."""
        self.spotlight_clue(subject=None, targets=coords)

    def clear_highlights(self) -> None:
        """Xóa toàn bộ hiệu ứng highlight và khôi phục độ sáng bình thường."""
        for widget in self._card_widgets.values():
            widget.set_spotlight(role=None, dimmed=False)

    def mark_hint(self, coord: Coord | None) -> None:
        """Đánh dấu ô được gợi ý bằng viền nổi bật đặc biệt."""
        for c, widget in self._card_widgets.items():
            if c == coord:
                widget.set_spotlight(role="hint", dimmed=False)
            elif widget.highlight_role == "hint":
                widget.set_spotlight(role=None, dimmed=False)

    def shake_cell(self, coord: Coord) -> None:
        """Kích hoạt hiệu ứng rung lắc cảnh báo cho một thẻ cụ thể."""
        widget = self._card_widgets.get(coord)
        if widget is not None:
            widget.shake()

    def spotlight_clue(self, subject: Coord | None, targets: tuple[Coord, ...]) -> None:
        """Tô sáng ngữ cảnh manh mối: Chủ thể (vàng), Mục tiêu (xanh), các ô khác làm mờ."""
        targets_set = set(targets)
        has_spotlight = (subject is not None) or bool(targets_set)

        for coord, widget in self._card_widgets.items():
            if coord == subject:
                widget.set_spotlight(role="subject", dimmed=False)
            elif coord in targets_set:
                widget.set_spotlight(role="target", dimmed=False)
            else:
                widget.set_spotlight(role=None, dimmed=has_spotlight)

    def set_input_enabled(self, enabled: bool) -> None:
        """Cho phép hoặc chặn người chơi click ô (chặn khi Auto Solve đang chạy)."""
        self._input_enabled = enabled

    # ------------------------------------------------------------ internals
    def _rebuild(self, state: PublicState) -> None:
        """Dựng lại toàn bộ lưới thẻ nhân vật khi đổi ván chơi hoặc kích thước."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                if isinstance(widget, CharacterCardWidget):
                    widget.stop_animations()
                widget.hide()
                widget.deleteLater()

        self._card_widgets.clear()
        self._header_widgets.clear()
        self._cells.clear()
        self._size = state.size
        self._puzzle_id = state.puzzle_id

        # Tiêu đề Cột (A, B, C...)
        for c in range(state.size):
            col_letter = chr(ord("A") + c)
            lbl = QLabel(f"COL {col_letter}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #64748B; font-family: 'Segoe UI'; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
            self.grid_layout.addWidget(lbl, 0, c + 1)
            self._header_widgets.append(lbl)

        # Tiêu đề Hàng (1, 2, 3...)
        for r in range(state.size):
            row_num = str(r + 1)
            lbl = QLabel(f"ROW {row_num}", self)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #64748B; font-family: 'Segoe UI'; font-size: 11px; font-weight: bold; letter-spacing: 1px; padding-right: 6px;")
            self.grid_layout.addWidget(lbl, r + 1, 0)
            self._header_widgets.append(lbl)

        # Tạo từng thẻ nhân vật
        for cell in state.cells:
            col, row = parse_coord(cell.coord)
            card = CharacterCardWidget(cell.coord, self)
            card.set_cell_data(cell, animate_flip_if_new=False)
            card.card_clicked.connect(self._on_card_clicked)
            self._card_widgets[cell.coord] = card
            self._cells[cell.coord] = cell
            self.grid_layout.addWidget(card, row + 1, col + 1)

    def _on_card_clicked(self, coord: Coord) -> None:
        """Xử lý sự kiện khi người chơi click vào thẻ."""
        if not self._input_enabled:
            return

        cell = self._cells.get(coord)
        if cell is None:
            return

        # Nếu thẻ đã lật: kích hoạt xem manh mối (spotlight clue)
        if cell.revealed:
            self.cell_inspected.emit(coord)
            return

        # Nếu thẻ chưa lật: mở hộp thoại thẩm vấn thẩm mỹ
        dlg = VerdictDialog(coord=coord, name=cell.name, job=cell.job, parent=self)
        if dlg.exec() == VerdictDialog.DialogCode.Accepted and dlg.selected_status is not None:
            self.cell_submitted.emit(coord, dlg.selected_status)
