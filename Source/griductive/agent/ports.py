"""Ports and protocols for data isolation between Agent and Game.

Tác dụng:
    Định nghĩa cổng giao tiếp trừu tượng (PublicGame Protocol) giữa Logic Agent và Game.
    Bảo đảm Rule 1: Logic Agent chỉ nhìn thấy thế giới qua PublicState và thao tác qua submit_verdict.
    Không bao giờ import hay truy cập thuộc tính ẩn của GameEngine.

Input:
    Không có (định nghĩa Protocol).

Output:
    PublicGame Protocol.
    Được GameEngine thực thi ngầm định (structural subtyping) và LogicAgent sử dụng.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

from typing import Protocol
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState, VerdictOutcome
from griductive.domain.types import Status


class PublicGame(Protocol):
    """Giao diện công khai tối thiểu của Game dành riêng cho Agent."""

    def public_state(self) -> PublicState:
        """Lấy toàn bộ trạng thái công khai hiện tại của bàn chơi."""
        ...

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Nộp kết luận về một ô và nhận kết quả phản hồi từ Engine."""
        ...
