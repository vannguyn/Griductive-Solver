import pytest

from griductive.clues.parser import parse_clue
from griductive.domain.errors import InvalidClueError


@pytest.mark.parametrize(
    ("fields", "error"),
    [
        ({"type": 7}, "type"),
        ({"type": "FACT", "status": []}, "status"),
        ({"type": "FACT", "target_cell": "D1"}, "target_cell"),
        ({"type": "SAME", "cell_a": "B1"}, "cell_b"),
        ({"type": "EXACTLY", "k": True}, "k"),
        ({"type": "EXACTLY", "k": 4, "region": {"kind": "row", "index": 1}}, "k"),
        ({"type": "AT_MOST", "k": 1, "region": {"kind": "row", "index": True}}, "index"),
        ({"type": "AT_LEAST", "k": 1, "region": {"kind": "neighbors", "center": "D1"}}, "region"),
        ({"type": "PARITY", "parity": "OTHER"}, "parity"),
        ({"type": "COMPOUND", "op": "NOT", "sub_clues": []}, "sub_clues"),
        ({"type": "COMPOUND", "op": "OR", "sub_clues": [None]}, r"sub_clues\[0\]"),
    ],
)
def test_parse_rejects_malformed_clue(fields, error):
    with pytest.raises(InvalidClueError, match=rf"clue-1.*{error}"):
        parse_clue({"id": "clue-1", "owner": "A1", **fields}, 3)


def test_explicit_region_uses_unique_canonical_cells():
    clue = parse_clue(
        {
            "id": "count", "owner": "a1", "type": "exactly", "k": 1,
            "region": {"kind": "explicit", "cells": ["a01", "A1", "B1"]},
        },
        3,
    )
    assert clue.owner == "A1"
    assert clue.cells() == ("A1", "B1")
    assert clue.evaluate({"A1": True, "B1": False})
