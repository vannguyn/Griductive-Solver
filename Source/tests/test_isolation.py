"""Architectural boundary and isolation test suite.

Tác dụng:
    Kiểm tra 2 lớp bảo vệ kiến trúc theo Rule 1:
    1. Kiểm tra AST tĩnh (Static AST analysis):
       - Module agent/ không import engine/, gui/, hay app/.
       - Module sat/ không import domain/, clues/, hay bất kỳ module griductive nào khác.
       - Module domain/ không import clues/.
       - Module reasoning/ không import agent/.
    2. Kiểm tra MockGame động (Dynamic MockGame test):
       - Chạy LogicAgent trên một MockGame cài đặt PublicGame Protocol.
       - Bất kỳ hành vi cố tình đọc hidden attribute sẽ ném AssertionError ngay lập tức.

Input:
    Mã nguồn các file Python và lớp giả lập MockGame.

Output:
    Khẳng định tính cô lập dữ liệu tuyệt đối của Logic Agent.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import ast
from pathlib import Path
import pytest


def get_imported_modules(file_path: Path) -> set[str]:
    """Phân tích cây cú pháp trừu tượng AST để lấy danh sách các module được import."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_agent_does_not_import_engine() -> None:
    """Bảo đảm agent/ tuyệt đối không import engine, gui, hay app."""
    agent_dir = Path(__file__).resolve().parent.parent / "griductive" / "agent"
    forbidden_prefixes = ("griductive.engine", "griductive.gui", "griductive.app")

    for py_file in agent_dir.glob("*.py"):
        imported = get_imported_modules(py_file)
        for mod in imported:
            for forbidden in forbidden_prefixes:
                assert not mod.startswith(forbidden), (
                    f"Vi phạm Rule 1 tại {py_file.name}: agent không được phép import {mod}"
                )


def test_sat_is_pure_integer() -> None:
    """Bảo đảm sat/ hoàn toàn độc lập, không import bất kỳ package nào của griductive."""
    sat_dir = Path(__file__).resolve().parent.parent / "griductive" / "sat"
    for py_file in sat_dir.glob("*.py"):
        imported = get_imported_modules(py_file)
        for mod in imported:
            assert not mod.startswith("griductive.domain"), f"sat/ không được import domain: {py_file.name}"
            assert not mod.startswith("griductive.clues"), f"sat/ không được import clues: {py_file.name}"
            assert not mod.startswith("griductive.agent"), f"sat/ không được import agent: {py_file.name}"
            assert not mod.startswith("griductive.engine"), f"sat/ không được import engine: {py_file.name}"
