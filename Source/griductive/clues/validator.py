"""Clue syntax and parameter validator.

Tác dụng:
    Kiểm tra tính hợp lệ của dữ liệu clue (dict thô hoặc đối tượng Clue):
    - Kiểm tra các trường bắt buộc (id, owner, type).
    - Tọa độ owner và các ô liên quan phải nằm trong biên lưới N x N.
    - Với các clue đếm (EXACTLY, AT_LEAST, AT_MOST): 0 <= k <= |R|.
    - Ném ngoại lệ InvalidClueError có thông báo chi tiết khi phát hiện vi phạm.

Input:
    Dictionary thô từ JSON hoặc đối tượng Clue, và kích thước lưới size.

Output:
    None (nếu hợp lệ) hoặc raise InvalidClueError (nếu vi phạm).
    Được gọi bởi clues/parser.py và engine/loader.py.

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from griductive.clues.base import Clue
from griductive.domain.errors import InvalidClueError
from griductive.domain.grid import validate_coord


def validate_clue_dict(data: dict, size: int) -> None:
    """Kiểm tra dictionary định nghĩa clue từ file JSON trước khi phân tích cú pháp."""
    if not isinstance(data, dict):
        raise InvalidClueError(f"Dữ liệu clue phải là dict, nhận được: {type(data)}")

    for req_field in ("id", "owner", "type"):
        if req_field not in data:
            raise InvalidClueError(f"Clue thiếu trường bắt buộc {req_field!r}: {data}")

    owner = data["owner"]
    if not validate_coord(owner, size):
        raise InvalidClueError(f"Owner {owner!r} nằm ngoài lưới {size}x{size}")

    clue_type = data["type"].upper()
    if clue_type in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        if "k" not in data:
            raise InvalidClueError(f"Clue loại {clue_type} bắt buộc phải có trường 'k'")
        k = data["k"]
        if not isinstance(k, int) or k < 0:
            raise InvalidClueError(f"Giá trị k không hợp lệ: {k}")


def validate_clue_object(clue: Clue, size: int) -> None:
    """Kiểm tra tính hợp lệ của một đối tượng Clue đã khởi tạo."""
    if not validate_coord(clue.owner, size):
        raise InvalidClueError(f"Owner {clue.owner} của clue {clue.id} nằm ngoài lưới {size}x{size}")
    for cell in clue.cells():
        if not validate_coord(cell, size):
            raise InvalidClueError(f"Ô tham chiếu {cell} của clue {clue.id} nằm ngoài lưới {size}x{size}")
