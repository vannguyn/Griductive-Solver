"""Puzzle generation and verification tool for Griductive Solver.

Tạo và kiểm định các bộ puzzle 3x3, 4x4, 5x5 bảo đảm:
1. Schema JSON chuẩn xác.
2. Clue evaluate(solution) == True với 100% clue.
3. Nghiệm DUY NHẤT (UNIQUE qua SAT blocking clause).
4. Giải được 100% qua LogicAgent mà không cần đoán mò (SOLVED).
"""

import json
from pathlib import Path
from griductive.domain.grid import all_coords
from griductive.experiments.validate_puzzle import validate_puzzle_file

NAMES = [
    ("A1", "Abel", "Detective"), ("B1", "Bea", "Analyst"), ("C1", "Cora", "Journalist"),
    ("D1", "Derek", "Guard"), ("E1", "Eva", "Officer"),
    ("A2", "Dara", "Engineer"), ("B2", "Eli", "Doctor"), ("C2", "Faye", "Teacher"),
    ("D2", "Grant", "Clerk"), ("E2", "Hannah", "Guard"),
    ("A3", "Gus", "Designer"), ("B3", "Hana", "Lawyer"), ("C3", "Iris", "Pilot"),
    ("D3", "Jonas", "Farmer"), ("E3", "Karl", "Painter"),
    ("A4", "Mara", "Astronaut"), ("B4", "Noah", "Clerk"), ("C4", "Owen", "Clerk"),
    ("D4", "Priya", "Farmer"), ("E4", "Quinn", "Scientist"),
    ("A5", "Roy", "Guard"), ("B5", "Sophia", "Painter"), ("C5", "Tom", "Farmer"),
    ("D5", "Uma", "Chef"), ("E5", "Vince", "Tailor"),
]


def make_characters(size: int) -> list[dict]:
    coords = set(all_coords(size))
    chars = []
    for cell, name, job in NAMES:
        if cell in coords:
            chars.append({"cell": cell, "name": name, "job": job})
    return chars


# =========================================================================
# 3x3 PUZZLE DEFINITIONS
# =========================================================================

def create_3x3_p01() -> dict:
    """3x3 Puzzle 1: Deductive chain with FACT, SAME, DIFFERENT, EXACTLY."""
    sol = {
        "A1": True, "B1": False, "C1": False,
        "A2": False, "B2": True, "C2": True,
        "A3": True, "B3": True, "C3": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "EXACTLY", "hint": "Row 1 exactly 1 criminal", "region": {"kind": "row", "index": 1}, "k": 1},
        {"id": "c_b1", "owner": "B1", "type": "FACT", "hint": "B2 is criminal", "target_cell": "B2", "status": "CRIMINAL"},
        {"id": "c_c1", "owner": "C1", "type": "DIFFERENT", "hint": "C1 diff C2", "cell_a": "C1", "cell_b": "C2"},
        {"id": "c_a2", "owner": "A2", "type": "DIFFERENT", "hint": "A2 diff B3", "cell_a": "A2", "cell_b": "B3"},
        {"id": "c_b2", "owner": "B2", "type": "FACT", "hint": "A2 is innocent", "target_cell": "A2", "status": "INNOCENT"},
        {"id": "c_c2", "owner": "C2", "type": "SAME", "hint": "C2 same C3", "cell_a": "C2", "cell_b": "C3"},
        {"id": "c_a3", "owner": "A3", "type": "FACT", "hint": "C3 is criminal", "target_cell": "C3", "status": "CRIMINAL"},
        {"id": "c_b3", "owner": "B3", "type": "FACT", "hint": "A3 is criminal", "target_cell": "A3", "status": "CRIMINAL"},
        {"id": "c_c3", "owner": "C3", "type": "AT_MOST", "hint": "Row 3 at most 3 criminals", "region": {"kind": "row", "index": 3}, "k": 3},
    ]
    return {
        "id": "puzzle-3x3-01",
        "size": 3,
        "initially_revealed": ["A1"],
        "characters": make_characters(3),
        "solution": sol,
        "clues": clues,
    }


def create_3x3_p02() -> dict:
    """3x3 Puzzle 2: Featuring AT_LEAST, PARITY, DIFFERENT in topological order."""
    sol = {
        "A1": False, "B1": True, "C1": True,
        "A2": True, "B2": False, "C2": True,
        "A3": False, "B3": False, "C3": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "FACT", "hint": "B1 is criminal", "target_cell": "B1", "status": "CRIMINAL"},
        {"id": "c_b1", "owner": "B1", "type": "SAME", "hint": "B1 same C1", "cell_a": "B1", "cell_b": "C1"},
        {"id": "c_c1", "owner": "C1", "type": "SAME", "hint": "C1 same C2", "cell_a": "C1", "cell_b": "C2"},
        {"id": "c_c2", "owner": "C2", "type": "DIFFERENT", "hint": "C2 diff B2", "cell_a": "C2", "cell_b": "B2"},
        {"id": "c_b2", "owner": "B2", "type": "DIFFERENT", "hint": "B2 diff A2", "cell_a": "B2", "cell_b": "A2"},
        {"id": "c_a2", "owner": "A2", "type": "PARITY", "hint": "Col 1 odd criminal count", "parity": "ODD", "region": {"kind": "column", "index": 1}},
        {"id": "c_a3", "owner": "A3", "type": "FACT", "hint": "B3 is innocent", "target_cell": "B3", "status": "INNOCENT"},
        {"id": "c_b3", "owner": "B3", "type": "DIFFERENT", "hint": "B3 diff C3", "cell_a": "B3", "cell_b": "C3"},
        {"id": "c_c3", "owner": "C3", "type": "AT_MOST", "hint": "Row 3 at most 1 criminal", "region": {"kind": "row", "index": 3}, "k": 1},
    ]
    return {
        "id": "puzzle-3x3-02",
        "size": 3,
        "initially_revealed": ["A1"],
        "characters": make_characters(3),
        "solution": sol,
        "clues": clues,
    }


def create_3x3_p03() -> dict:
    """3x3 Puzzle 3: Featuring AT_MOST, EXACTLY, SAME, DIFFERENT."""
    sol = {
        "A1": True, "B1": True, "C1": False,
        "A2": True, "B2": False, "C2": False,
        "A3": False, "B3": True, "C3": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "SAME", "hint": "A1 same B1", "cell_a": "A1", "cell_b": "B1"},
        {"id": "c_b1", "owner": "B1", "type": "DIFFERENT", "hint": "B1 diff C1", "cell_a": "B1", "cell_b": "C1"},
        {"id": "c_c1", "owner": "C1", "type": "SAME", "hint": "C1 same B2", "cell_a": "C1", "cell_b": "B2"},
        {"id": "c_b2", "owner": "B2", "type": "DIFFERENT", "hint": "B2 diff A2", "cell_a": "B2", "cell_b": "A2"},
        {"id": "c_a2", "owner": "A2", "type": "DIFFERENT", "hint": "A2 diff A3", "cell_a": "A2", "cell_b": "A3"},
        {"id": "c_a3", "owner": "A3", "type": "SAME", "hint": "A3 same C2", "cell_a": "A3", "cell_b": "C2"},
        {"id": "c_c2", "owner": "C2", "type": "DIFFERENT", "hint": "C2 diff B3", "cell_a": "C2", "cell_b": "B3"},
        {"id": "c_b3", "owner": "B3", "type": "SAME", "hint": "B3 same C3", "cell_a": "B3", "cell_b": "C3"},
        {"id": "c_c3", "owner": "C3", "type": "EXACTLY", "hint": "Row 3 exactly 2 criminals", "region": {"kind": "row", "index": 3}, "k": 2},
    ]
    return {
        "id": "puzzle-3x3-03",
        "size": 3,
        "initially_revealed": ["A1"],
        "characters": make_characters(3),
        "solution": sol,
        "clues": clues,
    }


# =========================================================================
# 4x4 PUZZLE DEFINITIONS
# =========================================================================

def create_4x4_p01() -> dict:
    """4x4 Puzzle 1: 16 cells, cascading FACT and cardinality."""
    sol = {
        "A1": True, "B1": False, "C1": True, "D1": False,
        "A2": False, "B2": True, "C2": False, "D2": True,
        "A3": True, "B3": True, "C3": False, "D3": False,
        "A4": False, "B4": False, "C4": True, "D4": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "FACT", "hint": "B1 is innocent", "target_cell": "B1", "status": "INNOCENT"},
        {"id": "c_b1", "owner": "B1", "type": "FACT", "hint": "C1 is criminal", "target_cell": "C1", "status": "CRIMINAL"},
        {"id": "c_c1", "owner": "C1", "type": "FACT", "hint": "D1 is innocent", "target_cell": "D1", "status": "INNOCENT"},
        {"id": "c_d1", "owner": "D1", "type": "FACT", "hint": "A2 is innocent", "target_cell": "A2", "status": "INNOCENT"},

        {"id": "c_a2", "owner": "A2", "type": "FACT", "hint": "B2 is criminal", "target_cell": "B2", "status": "CRIMINAL"},
        {"id": "c_b2", "owner": "B2", "type": "FACT", "hint": "C2 is innocent", "target_cell": "C2", "status": "INNOCENT"},
        {"id": "c_c2", "owner": "C2", "type": "FACT", "hint": "D2 is criminal", "target_cell": "D2", "status": "CRIMINAL"},
        {"id": "c_d2", "owner": "D2", "type": "FACT", "hint": "A3 is criminal", "target_cell": "A3", "status": "CRIMINAL"},

        {"id": "c_a3", "owner": "A3", "type": "FACT", "hint": "B3 is criminal", "target_cell": "B3", "status": "CRIMINAL"},
        {"id": "c_b3", "owner": "B3", "type": "FACT", "hint": "C3 is innocent", "target_cell": "C3", "status": "INNOCENT"},
        {"id": "c_c3", "owner": "C3", "type": "FACT", "hint": "D3 is innocent", "target_cell": "D3", "status": "INNOCENT"},
        {"id": "c_d3", "owner": "D3", "type": "FACT", "hint": "A4 is innocent", "target_cell": "A4", "status": "INNOCENT"},

        {"id": "c_a4", "owner": "A4", "type": "FACT", "hint": "B4 is innocent", "target_cell": "B4", "status": "INNOCENT"},
        {"id": "c_b4", "owner": "B4", "type": "FACT", "hint": "C4 is criminal", "target_cell": "C4", "status": "CRIMINAL"},
        {"id": "c_c4", "owner": "C4", "type": "FACT", "hint": "D4 is criminal", "target_cell": "D4", "status": "CRIMINAL"},
        {"id": "c_d4", "owner": "D4", "type": "EXACTLY", "hint": "Row 4 exactly 2 criminals", "region": {"kind": "row", "index": 4}, "k": 2},
    ]
    return {
        "id": "puzzle-4x4-01",
        "size": 4,
        "initially_revealed": ["A1"],
        "characters": make_characters(4),
        "solution": sol,
        "clues": clues,
    }


def create_4x4_p02() -> dict:
    """4x4 Puzzle 2: Rich relations with SAME, DIFFERENT, PARITY."""
    sol = {
        "A1": False, "B1": True, "C1": True, "D1": False,
        "A2": True, "B2": False, "C2": True, "D2": False,
        "A3": False, "B3": True, "C3": False, "D3": True,
        "A4": True, "B4": False, "C4": True, "D4": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "DIFFERENT", "hint": "A1 diff B1", "cell_a": "A1", "cell_b": "B1"},
        {"id": "c_b1", "owner": "B1", "type": "SAME", "hint": "B1 same C1", "cell_a": "B1", "cell_b": "C1"},
        {"id": "c_c1", "owner": "C1", "type": "DIFFERENT", "hint": "C1 diff D1", "cell_a": "C1", "cell_b": "D1"},
        {"id": "c_d1", "owner": "D1", "type": "DIFFERENT", "hint": "D1 diff A2", "cell_a": "D1", "cell_b": "A2"},

        {"id": "c_a2", "owner": "A2", "type": "DIFFERENT", "hint": "A2 diff B2", "cell_a": "A2", "cell_b": "B2"},
        {"id": "c_b2", "owner": "B2", "type": "DIFFERENT", "hint": "B2 diff C2", "cell_a": "B2", "cell_b": "C2"},
        {"id": "c_c2", "owner": "C2", "type": "DIFFERENT", "hint": "C2 diff D2", "cell_a": "C2", "cell_b": "D2"},
        {"id": "c_d2", "owner": "D2", "type": "SAME", "hint": "D2 same A3", "cell_a": "D2", "cell_b": "A3"},

        {"id": "c_a3", "owner": "A3", "type": "DIFFERENT", "hint": "A3 diff B3", "cell_a": "A3", "cell_b": "B3"},
        {"id": "c_b3", "owner": "B3", "type": "DIFFERENT", "hint": "B3 diff C3", "cell_a": "B3", "cell_b": "C3"},
        {"id": "c_c3", "owner": "C3", "type": "DIFFERENT", "hint": "C3 diff D3", "cell_a": "C3", "cell_b": "D3"},
        {"id": "c_d3", "owner": "D3", "type": "SAME", "hint": "D3 same A4", "cell_a": "D3", "cell_b": "A4"},

        {"id": "c_a4", "owner": "A4", "type": "DIFFERENT", "hint": "A4 diff B4", "cell_a": "A4", "cell_b": "B4"},
        {"id": "c_b4", "owner": "B4", "type": "DIFFERENT", "hint": "B4 diff C4", "cell_a": "B4", "cell_b": "C4"},
        {"id": "c_c4", "owner": "C4", "type": "SAME", "hint": "C4 same D4", "cell_a": "C4", "cell_b": "D4"},
        {"id": "c_d4", "owner": "D4", "type": "PARITY", "hint": "Col 4 has even criminals", "parity": "EVEN", "region": {"kind": "column", "index": 4}},
    ]
    return {
        "id": "puzzle-4x4-02",
        "size": 4,
        "initially_revealed": ["A1"],
        "characters": make_characters(4),
        "solution": sol,
        "clues": clues,
    }


def create_4x4_p03() -> dict:
    """4x4 Puzzle 3: Featuring Cardinality counting (EXACTLY) on column."""
    sol = {
        "A1": True, "B1": True, "C1": False, "D1": False,
        "A2": False, "B2": True, "C2": True, "D2": False,
        "A3": True, "B3": False, "C3": True, "D3": True,
        "A4": False, "B4": False, "C4": False, "D4": True,
    }
    clues = [
        {"id": "c_a1", "owner": "A1", "type": "FACT", "hint": "B1 is criminal", "target_cell": "B1", "status": "CRIMINAL"},
        {"id": "c_b1", "owner": "B1", "type": "FACT", "hint": "C1 is innocent", "target_cell": "C1", "status": "INNOCENT"},
        {"id": "c_c1", "owner": "C1", "type": "SAME", "hint": "C1 same D1", "cell_a": "C1", "cell_b": "D1"},
        {"id": "c_d1", "owner": "D1", "type": "SAME", "hint": "D1 same A2", "cell_a": "D1", "cell_b": "A2"},

        {"id": "c_a2", "owner": "A2", "type": "DIFFERENT", "hint": "A2 diff B2", "cell_a": "A2", "cell_b": "B2"},
        {"id": "c_b2", "owner": "B2", "type": "SAME", "hint": "B2 same C2", "cell_a": "B2", "cell_b": "C2"},
        {"id": "c_c2", "owner": "C2", "type": "DIFFERENT", "hint": "C2 diff D2", "cell_a": "C2", "cell_b": "D2"},
        {"id": "c_d2", "owner": "D2", "type": "DIFFERENT", "hint": "D2 diff A3", "cell_a": "D2", "cell_b": "A3"},

        {"id": "c_a3", "owner": "A3", "type": "DIFFERENT", "hint": "A3 diff B3", "cell_a": "A3", "cell_b": "B3"},
        {"id": "c_b3", "owner": "B3", "type": "DIFFERENT", "hint": "B3 diff C3", "cell_a": "B3", "cell_b": "C3"},
        {"id": "c_c3", "owner": "C3", "type": "SAME", "hint": "C3 same D3", "cell_a": "C3", "cell_b": "D3"},
        {"id": "c_d3", "owner": "D3", "type": "DIFFERENT", "hint": "D3 diff A4", "cell_a": "D3", "cell_b": "A4"},

        {"id": "c_a4", "owner": "A4", "type": "SAME", "hint": "A4 same B4", "cell_a": "A4", "cell_b": "B4"},
        {"id": "c_b4", "owner": "B4", "type": "SAME", "hint": "B4 same C4", "cell_a": "B4", "cell_b": "C4"},
        {"id": "c_c4", "owner": "C4", "type": "DIFFERENT", "hint": "C4 diff D4", "cell_a": "C4", "cell_b": "D4"},
        {"id": "c_d4", "owner": "D4", "type": "EXACTLY", "hint": "Col 4 exactly 2 criminals", "region": {"kind": "column", "index": 4}, "k": 2},
    ]
    return {
        "id": "puzzle-4x4-03",
        "size": 4,
        "initially_revealed": ["A1"],
        "characters": make_characters(4),
        "solution": sol,
        "clues": clues,
    }


# =========================================================================
# 5x5 PUZZLE DEFINITION (Stress Case)
# =========================================================================

def create_5x5_p01() -> dict:
    """5x5 Puzzle 1: 25 cells stress case with progressive cascade across all cells."""
    coords = all_coords(5)
    sol = {}
    for c in coords:
        col_idx = ord(c[0]) - ord('A')
        row_idx = int(c[1]) - 1
        sol[c] = ((col_idx + row_idx) % 2 == 0)

    # Clues form a complete domino chain from A1 through all 25 cells
    clues = []
    for i in range(len(coords) - 1):
        c_curr = coords[i]
        c_next = coords[i + 1]
        if sol[c_curr] == sol[c_next]:
            clues.append({
                "id": f"c_{c_curr.lower()}",
                "owner": c_curr,
                "type": "SAME",
                "hint": f"{c_curr} same status as {c_next}",
                "cell_a": c_curr,
                "cell_b": c_next,
            })
        else:
            clues.append({
                "id": f"c_{c_curr.lower()}",
                "owner": c_curr,
                "type": "DIFFERENT",
                "hint": f"{c_curr} diff status from {c_next}",
                "cell_a": c_curr,
                "cell_b": c_next,
            })

    # Clue for the last cell E5: Row 5 cardinality
    clues.append({
        "id": "c_e5",
        "owner": "E5",
        "type": "EXACTLY",
        "hint": "Row 5 has exactly 3 criminals",
        "region": {"kind": "row", "index": 5},
        "k": 3,
    })

    return {
        "id": "puzzle-5x5-01",
        "size": 5,
        "initially_revealed": ["A1"],
        "characters": make_characters(5),
        "solution": sol,
        "clues": clues,
    }


def generate_all() -> None:
    puzzles_to_generate = [
        ("Source/puzzles/3x3/puzzle_01.json", create_3x3_p01()),
        ("Source/puzzles/3x3/puzzle_02.json", create_3x3_p02()),
        ("Source/puzzles/3x3/puzzle_03.json", create_3x3_p03()),
        ("Source/puzzles/4x4/puzzle_01.json", create_4x4_p01()),
        ("Source/puzzles/4x4/puzzle_02.json", create_4x4_p02()),
        ("Source/puzzles/4x4/puzzle_03.json", create_4x4_p03()),
        ("Source/puzzles/5x5/puzzle_01.json", create_5x5_p01()),
    ]

    for rel_path, p_data in puzzles_to_generate:
        p = Path(rel_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(p_data, f, indent=2, ensure_ascii=False)
        print(f"Generated {rel_path}")

        # Kiểm định ngay sau khi sinh
        valid, msg = validate_puzzle_file(p)
        print(f"  -> Validation: {'PASS' if valid else 'FAIL'}: {msg}")
        assert valid, f"Puzzle sinh ra không đạt chuẩn: {msg}"

    print("\nALL PUZZLES GENERATED AND VERIFIED 100% VALID!")


if __name__ == "__main__":
    generate_all()
