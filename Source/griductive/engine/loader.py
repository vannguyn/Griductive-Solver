"""Fast puzzle loader and runtime integrity validator.

Tác dụng:
    Đọc và phân tích cú pháp file JSON của Puzzle:
    - Kiểm tra schema JSON: id, size (3, 4, 5), characters, initially_revealed, solution, clues.
    - Bảo đảm đúng N*N ô nhân vật và ánh xạ 1-1 owner cho mỗi clue.
    - Kiểm tra nhanh tính tương thích của solution: clue.evaluate(solution) == True cho toàn bộ clue.
    - KHÔNG chạy SAT uniqueness check ở đây (để tránh lag/treo giao diện GUI khi mở file).
    - Ném InvalidPuzzleError nếu file sai định dạng.

Input:
    Đường dẫn file (path: str | Path) hoặc dictionary dữ liệu thô.

Output:
    Đối tượng Puzzle hợp lệ.
    Được gọi bởi GameSession.load_puzzle().

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

import json
from pathlib import Path
from griductive.clues.parser import parse_clues
from griductive.domain.errors import InvalidPuzzleError
from griductive.domain.grid import all_coords, validate_coord
from griductive.engine.puzzle import Character, Puzzle


def load_puzzle_from_dict(data: dict) -> Puzzle:
    """Nạp và kiểm tra tính hợp lệ của puzzle từ dictionary."""
    if not isinstance(data, dict):
        raise InvalidPuzzleError("Dữ liệu puzzle phải là dictionary JSON.")

    puzzle_id = str(data.get("id", "unknown"))
    size = data.get("size")
    if size not in (3, 4, 5):
        raise InvalidPuzzleError(f"Kích thước lưới không hợp lệ (chỉ hỗ trợ 3, 4, 5): {size}")

    coords_in_grid = set(all_coords(size))

    # 1. Characters
    raw_chars = data.get("characters", [])
    if len(raw_chars) != size * size:
        raise InvalidPuzzleError(f"Cần đúng {size*size} nhân vật, tìm thấy: {len(raw_chars)}")
    characters: dict[str, Character] = {}
    for rc in raw_chars:
        cell = rc.get("cell")
        if not cell or not validate_coord(cell, size):
            raise InvalidPuzzleError(f"Tọa độ nhân vật không hợp lệ: {cell}")
        characters[cell] = Character(cell=cell, name=rc.get("name", "Unknown"), job=rc.get("job", "Unknown"))

    # 2. Initially revealed
    initially_revealed = tuple(data.get("initially_revealed", ()))
    for c in initially_revealed:
        if not validate_coord(c, size):
            raise InvalidPuzzleError(f"Tọa độ initially_revealed không hợp lệ: {c}")

    # 3. Solution
    solution_raw = data.get("solution", {})
    if len(solution_raw) != size * size:
        raise InvalidPuzzleError(f"Solution phải chứa đủ {size*size} ô.")
    solution: dict[str, bool] = {}
    for c in coords_in_grid:
        if c not in solution_raw:
            raise InvalidPuzzleError(f"Thiếu giá trị solution cho ô: {c}")
        val = solution_raw[c]
        if not isinstance(val, bool):
            raise InvalidPuzzleError(f"Giá trị solution của ô {c} phải là bool: {val}")
        solution[c] = val

    # 4. Clues
    raw_clues = data.get("clues", [])
    if len(raw_clues) != size * size:
        raise InvalidPuzzleError(f"Cần đúng {size*size} clue (mỗi ô 1 clue), tìm thấy: {len(raw_clues)}")
    parsed_clues = parse_clues(raw_clues, size)
    clues_map: dict[str, Any] = {}
    for clue in parsed_clues:
        if clue.owner in clues_map:
            raise InvalidPuzzleError(f"Ô {clue.owner} có nhiều hơn 1 clue sở hữu!")
        clues_map[clue.owner] = clue

        # Kiểm tra nhanh: clue phải đúng với solution ẩn
        if not clue.evaluate(solution):
            raise InvalidPuzzleError(f"Clue {clue.id} (owner={clue.owner}) mâu thuẫn với solution ẩn!")

    return Puzzle(
        id=puzzle_id,
        size=size,
        characters=characters,
        solution=solution,
        initially_revealed=initially_revealed,
        clues=clues_map,
    )


def load_puzzle_file(path: str | Path) -> Puzzle:
    """Đọc file JSON từ đĩa và nạp thành đối tượng Puzzle."""
    p = Path(path)
    if not p.exists():
        raise InvalidPuzzleError(f"Không tìm thấy file puzzle: {p}")
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise InvalidPuzzleError(f"File JSON không hợp lệ: {e}")

    return load_puzzle_from_dict(data)
