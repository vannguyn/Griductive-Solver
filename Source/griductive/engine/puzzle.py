"""Puzzle definition and internal hidden solution representation.

Tác dụng:
    Định nghĩa cấu trúc dữ liệu toàn diện của một bài toán Puzzle:
    - Character: Tên, nghề nghiệp, tọa độ của nhân vật.
    - Puzzle: Lưu trữ toàn bộ thông tin bài toán, bao gồm:
        + Kích thước N x N (3, 4, 5)
        + Danh sách toàn bộ characters
        + initially_revealed: Danh sách tọa độ các ô được lật sẵn ban đầu (tạo nên KB_0)
        + clues: Toàn bộ danh sách Clue của mọi ô
        + solution: Đáp án ẩn dict[Coord, bool] (True = Criminal, False = Innocent).
    Lưu ý: Chỉ Engine mới được phép nắm giữ đối tượng Puzzle. PublicState không bao giờ để lộ solution.

Input:
    Dữ liệu đã được kiểm tra từ engine/loader.py.

Output:
    Đối tượng Puzzle.
    Được GameEngine quản lý bên trong.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from dataclasses import dataclass
from griductive.clues.base import Clue
from griductive.domain.grid import Coord


@dataclass(frozen=True)
class Character:
    """Thông tin nhân vật tại một ô trên lưới."""
    cell: Coord
    name: str
    job: str


@dataclass(frozen=True)
class Puzzle:
    """Cấu trúc dữ liệu đầy đủ của một puzzle (chứa cả đáp án ẩn)."""
    id: str
    size: int
    characters: dict[Coord, Character]
    solution: dict[Coord, bool]  # Chỉ engine được giữ
    initially_revealed: tuple[Coord, ...]
    clues: dict[Coord, Clue]  # Ánh xạ owner -> Clue
