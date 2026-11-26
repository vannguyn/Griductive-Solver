"""Clue JSON/dict parser and registry.

Tác dụng:
    Chuyển đổi dữ liệu từ điển thô (đọc từ file JSON puzzle) thành các đối tượng Clue cụ thể.
    Sử dụng cơ chế Registry theo trường "type" ("FACT", "SAME", "EXACTLY", "PARITY"...),
    tự động phân giải vùng (resolve_region) và gán các tham số tương ứng.

Input:
    Dictionary thô từ JSON (raw: dict) và kích thước lưới (size: int).

Output:
    Đối tượng Clue cụ thể (FactClue, ExactlyClue, ParityClue...).
    Được gọi bởi engine/loader.py khi tải puzzle.

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from typing import Any
from griductive.clues.base import Clue
from griductive.clues.core import (
    AtLeastClue,
    AtMostClue,
    DifferentClue,
    ExactlyClue,
    FactClue,
    SameClue,
)
from griductive.clues.extensions import CompoundClue, ParityClue
from griductive.clues.validator import COUNT_TYPES, validate_clue_dict, validate_clue_object
from griductive.domain.errors import InvalidClueError
from griductive.domain.grid import Coord, format_coord, parse_coord
from griductive.domain.regions import RegionKind, RegionSpec, resolve_region
from griductive.domain.types import Status


def _canonical_coord(coord: Coord) -> Coord:
    return format_coord(*parse_coord(coord))


def parse_region_spec(data: dict) -> RegionSpec:
    """Chuyển đổi dictionary vùng thành đối tượng RegionSpec."""
    if not isinstance(data, dict):
        raise InvalidClueError("region phải là đối tượng JSON")
    kind_str = data.get("kind")
    if not isinstance(kind_str, str):
        raise InvalidClueError("region.kind phải là chuỗi")
    try:
        kind = RegionKind(kind_str.lower())
    except ValueError as exc:
        raise InvalidClueError(f"region.kind không hợp lệ: {kind_str!r}") from exc

    if kind in (RegionKind.ROW, RegionKind.COLUMN):
        index = data.get("index")
        if type(index) is not int:
            raise InvalidClueError("region.index phải là số nguyên")
        return RegionSpec(kind=kind, index=index)
    if kind == RegionKind.NEIGHBORS:
        center = data.get("center")
        if not isinstance(center, str):
            raise InvalidClueError("region.center phải là tọa độ")
        return RegionSpec(kind=kind, center=center)

    cells = data.get("cells")
    if not isinstance(cells, (list, tuple)) or not all(isinstance(cell, str) for cell in cells):
        raise InvalidClueError("region.cells phải là danh sách tọa độ")
    return RegionSpec(kind=kind, cells=tuple(cells))


def parse_clue(raw: dict[str, Any], size: int) -> Clue:
    """Phân tích 1 clue từ dict thô và khởi tạo đối tượng Clue tương ứng."""
    validate_clue_dict(raw, size)

    clue_id = raw["id"]
    owner = _canonical_coord(raw["owner"])
    clue_type = raw["type"].upper()

    if clue_type == "FACT":
        target = _canonical_coord(raw.get("target_cell", owner))
        status_str = raw.get("status", "CRIMINAL").upper()
        return FactClue(clue_id, owner, target_cell=target, target_status=Status(status_str))

    elif clue_type == "SAME":
        return SameClue(clue_id, owner, _canonical_coord(raw["cell_a"]), _canonical_coord(raw["cell_b"]))

    elif clue_type == "DIFFERENT":
        return DifferentClue(
            clue_id, owner, _canonical_coord(raw["cell_a"]), _canonical_coord(raw["cell_b"])
        )

    elif clue_type in (*COUNT_TYPES, "PARITY"):
        try:
            spec = parse_region_spec(raw.get("region"))
            cells = resolve_region(spec, size)
        except InvalidClueError as exc:
            raise InvalidClueError(f"Clue {clue_id!r}: region: {exc}") from exc
        # Explicit coordinates may use different spellings for the same cell.
        cells = tuple(dict.fromkeys(_canonical_coord(cell) for cell in cells))
        if clue_type == "PARITY":
            return ParityClue(clue_id, owner, raw.get("parity", "EVEN").upper(), spec, cells)
        count_class = {"EXACTLY": ExactlyClue, "AT_LEAST": AtLeastClue, "AT_MOST": AtMostClue}
        clue = count_class[clue_type](clue_id, owner, raw["k"], spec, cells)
        validate_clue_object(clue, size)
        return clue

    elif clue_type == "COMPOUND":
        op = raw.get("op", "AND").upper()
        sub_clues = []
        for index, child in enumerate(raw["sub_clues"]):
            try:
                sub_clues.append(parse_clue(child, size))
            except InvalidClueError as exc:
                raise InvalidClueError(f"Clue {clue_id!r}: sub_clues[{index}]: {exc}") from exc
        return CompoundClue(clue_id, owner, op=op, sub_clues=tuple(sub_clues))

    else:
        raise InvalidClueError(f"Loại clue chưa được hỗ trợ: {clue_type}")


def parse_clues(raw_list: list[dict[str, Any]], size: int) -> tuple[Clue, ...]:
    """Phân tích danh sách các dictionary thành tuple các đối tượng Clue."""
    if not isinstance(raw_list, list):
        raise InvalidClueError("clues phải là danh sách")
    return tuple(parse_clue(c, size) for c in raw_list)
