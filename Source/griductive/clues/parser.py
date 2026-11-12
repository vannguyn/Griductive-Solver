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
from griductive.clues.validator import validate_clue_dict
from griductive.domain.errors import InvalidClueError
from griductive.domain.regions import RegionKind, RegionSpec, resolve_region
from griductive.domain.types import Status


def parse_region_spec(data: dict) -> RegionSpec:
    """Chuyển đổi dictionary vùng thành đối tượng RegionSpec."""
    kind_str = data.get("kind", "").lower()
    try:
        kind = RegionKind(kind_str)
    except ValueError:
        raise InvalidClueError(f"Loại vùng không hợp lệ: {kind_str}")

    return RegionSpec(
        kind=kind,
        index=data.get("index"),
        center=data.get("center"),
        cells=tuple(data.get("cells", ())),
    )


def parse_clue(raw: dict[str, Any], size: int) -> Clue:
    """Phân tích 1 clue từ dict thô và khởi tạo đối tượng Clue tương ứng."""
    validate_clue_dict(raw, size)

    clue_id = str(raw["id"])
    owner = str(raw["owner"])
    clue_type = str(raw["type"]).upper()

    if clue_type == "FACT":
        target = str(raw.get("target_cell", owner))
        status_str = str(raw.get("status", "CRIMINAL")).upper()
        return FactClue(clue_id, owner, target_cell=target, target_status=Status(status_str))

    elif clue_type == "SAME":
        return SameClue(clue_id, owner, cell_a=str(raw["cell_a"]), cell_b=str(raw["cell_b"]))

    elif clue_type == "DIFFERENT":
        return DifferentClue(clue_id, owner, cell_a=str(raw["cell_a"]), cell_b=str(raw["cell_b"]))

    elif clue_type in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        k = int(raw["k"])
        region_dict = raw.get("region", {})
        spec = parse_region_spec(region_dict)
        cells = resolve_region(spec, size)
        if clue_type == "EXACTLY":
            return ExactlyClue(clue_id, owner, k=k, region_spec=spec, region_cells=cells)
        elif clue_type == "AT_LEAST":
            return AtLeastClue(clue_id, owner, k=k, region_spec=spec, region_cells=cells)
        else:
            return AtMostClue(clue_id, owner, k=k, region_spec=spec, region_cells=cells)

    elif clue_type == "PARITY":
        parity = str(raw.get("parity", "EVEN")).upper()
        region_dict = raw.get("region", {})
        spec = parse_region_spec(region_dict)
        cells = resolve_region(spec, size)
        return ParityClue(clue_id, owner, parity=parity, region_spec=spec, region_cells=cells)

    elif clue_type == "COMPOUND":
        op = str(raw.get("op", "AND")).upper()
        sub_list = raw.get("sub_clues", [])
        sub_clues = tuple(parse_clue(s, size) for s in sub_list)
        return CompoundClue(clue_id, owner, op=op, sub_clues=sub_clues)

    else:
        raise InvalidClueError(f"Loại clue chưa được hỗ trợ: {clue_type}")


def parse_clues(raw_list: list[dict[str, Any]], size: int) -> tuple[Clue, ...]:
    """Phân tích danh sách các dictionary thành tuple các đối tượng Clue."""
    return tuple(parse_clue(c, size) for c in raw_list)
