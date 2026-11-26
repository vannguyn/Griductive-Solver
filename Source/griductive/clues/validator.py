from griductive.clues.base import Clue
from griductive.clues.core import AtLeastClue, AtMostClue, ExactlyClue
from griductive.clues.extensions import CompoundClue, ParityClue
from griductive.domain.errors import InvalidClueError
from griductive.domain.grid import validate_coord
from griductive.domain.types import Status


COUNT_TYPES = ("EXACTLY", "AT_LEAST", "AT_MOST")
CLUE_TYPES = ("FACT", "SAME", "DIFFERENT", *COUNT_TYPES, "PARITY", "COMPOUND")


def validate_clue_dict(data: dict, size: int) -> None:
    if not isinstance(data, dict):
        raise InvalidClueError(f"Dữ liệu clue phải là dict, nhận được: {type(data)}")

    for field in ("id", "owner", "type"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            raise InvalidClueError(f"Clue {data.get('id')!r}: {field!r} phải là chuỗi không rỗng")

    owner = data["owner"]
    if not validate_coord(owner, size):
        raise InvalidClueError(f"Clue {data['id']!r}: owner {owner!r} nằm ngoài lưới {size}x{size}")

    clue_type = data["type"].upper()
    if clue_type not in CLUE_TYPES:
        raise InvalidClueError(f"Clue {data['id']!r}: type chưa được hỗ trợ: {clue_type}")

    try:
        if clue_type == "FACT":
            _validate_choice(data, "status", "CRIMINAL", tuple(status.value for status in Status))
            _validate_cell(data.get("target_cell", owner), "target_cell", size)
        elif clue_type in ("SAME", "DIFFERENT"):
            _validate_cell(data.get("cell_a"), "cell_a", size)
            _validate_cell(data.get("cell_b"), "cell_b", size)
        elif clue_type in COUNT_TYPES:
            k = data.get("k")
            if type(k) is not int or k < 0:
                raise InvalidClueError(f"k phải là số nguyên không âm: {k!r}")
        elif clue_type == "PARITY":
            _validate_choice(data, "parity", "EVEN", ("EVEN", "ODD"))
        elif clue_type == "COMPOUND":
            op = _validate_choice(data, "op", "AND", ("AND", "OR", "NOT"))
            children = data.get("sub_clues")
            if not isinstance(children, list):
                raise InvalidClueError("sub_clues phải là danh sách")
            _validate_arity(op, len(children))
    except InvalidClueError as exc:
        raise InvalidClueError(f"Clue {data['id']!r}: {exc}") from exc


def _validate_choice(data: dict, field: str, default: str, choices: tuple[str, ...]) -> str:
    value = data.get(field, default)
    if not isinstance(value, str) or value.upper() not in choices:
        raise InvalidClueError(f"{field} không hợp lệ: {value!r}")
    return value.upper()


def _validate_cell(value: object, field: str, size: int) -> None:
    if not isinstance(value, str) or not validate_coord(value, size):
        raise InvalidClueError(f"{field} {value!r} nằm ngoài lưới {size}x{size} hoặc sai định dạng")


def _validate_arity(op: str, count: int) -> None:
    if op == "NOT" and count != 1:
        raise InvalidClueError("NOT cần đúng một phần tử trong sub_clues")
    if op in ("AND", "OR") and count == 0:
        raise InvalidClueError(f"{op} cần ít nhất một phần tử trong sub_clues")


def validate_clue_object(clue: Clue, size: int) -> None:
    if not validate_coord(clue.owner, size):
        raise InvalidClueError(f"Owner {clue.owner} của clue {clue.id} nằm ngoài lưới {size}x{size}")
    for cell in clue.cells():
        if not validate_coord(cell, size):
            raise InvalidClueError(f"Ô tham chiếu {cell} của clue {clue.id} nằm ngoài lưới {size}x{size}")
    if isinstance(clue, (AtLeastClue, AtMostClue, ExactlyClue)):
        if type(clue.k) is not int or not 0 <= clue.k <= len(clue.region_cells):
            raise InvalidClueError(f"Clue {clue.id!r}: k={clue.k!r} vượt phạm vi kích thước vùng")
    elif isinstance(clue, ParityClue) and clue.parity not in ("EVEN", "ODD"):
        raise InvalidClueError(f"Clue {clue.id!r}: parity không hợp lệ: {clue.parity!r}")
    elif isinstance(clue, CompoundClue):
        if clue.op not in ("AND", "OR", "NOT"):
            raise InvalidClueError(f"Clue {clue.id!r}: op không hợp lệ: {clue.op!r}")
        _validate_arity(clue.op, len(clue.sub_clues))
        for child in clue.sub_clues:
            validate_clue_object(child, size)
