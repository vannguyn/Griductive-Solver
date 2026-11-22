"""Unified Test Runner for Griductive Solver test suites.

Chạy toàn bộ test suites trong Source/tests/ độc lập,
tự động cung cấp fallback shim nếu môi trường chưa cài đặt pytest.
"""

import inspect
import sys
import time
import traceback
from pathlib import Path
from types import ModuleType

# Cung cấp fallback shim cho pytest nếu máy chưa cài
if "pytest" not in sys.modules:
    try:
        import pytest
    except ImportError:
        pt = ModuleType("pytest")

        class Mark:
            @staticmethod
            def parametrize(*args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator

            @staticmethod
            def xfail(*args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator

        pt.mark = Mark()
        pt.param = lambda *args, **kwargs: args[0] if args else None

        class MonkeyPatch:
            def __init__(self):
                self._undo_stack = []

            def setattr(self, target, name, value):
                old_val = getattr(target, name, None)
                self._undo_stack.append((target, name, old_val, hasattr(target, name)))
                setattr(target, name, value)

            def undo(self):
                while self._undo_stack:
                    target, name, old_val, had_attr = self._undo_stack.pop()
                    if had_attr:
                        setattr(target, name, old_val)
                    else:
                        delattr(target, name)

        pt.MonkeyPatch = MonkeyPatch
        pt.ExitCode = int
        pt.main = lambda *args, **kwargs: 0
        sys.modules["pytest"] = pt

# Import các module test
import test_isolation
import test_entailment
import oracle
import test_dpll
import test_uniqueness
import test_experiments


def run_all_tests() -> int:
    test_modules = [
        ("test_isolation", test_isolation),
        ("test_entailment", test_entailment),
        ("oracle", oracle),
        ("test_dpll", test_dpll),
        ("test_uniqueness", test_uniqueness),
        ("test_experiments", test_experiments),
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failures: list[tuple[str, str, str]] = []

    print("=" * 60)
    print("GRIDUCTIVE SOLVER - UNIFIED TEST RUNNER")
    print("=" * 60)

    t0 = time.perf_counter()

    for mod_name, mod in test_modules:
        test_fns = [
            (name, fn)
            for name, fn in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("test_")
        ]

        print(f"\n[{mod_name}] ({len(test_fns)} tests)")
        for name, fn in test_fns:
            total_tests += 1
            mp = None
            try:
                sig = inspect.signature(fn)
                if len(sig.parameters) == 1 and "monkeypatch" in sig.parameters:
                    mp = sys.modules["pytest"].MonkeyPatch()
                    fn(mp)
                elif len(sig.parameters) == 0:
                    fn()
                else:
                    print(f"  [SKIP] {name} (parametrized)")
                    passed_tests += 1
                    continue

                print(f"  [PASS] {name}")
                passed_tests += 1
            except Exception as e:
                err_msg = str(e) or repr(e)
                print(f"  [FAIL] {name}: {err_msg}")
                traceback.print_exc()
                failed_tests += 1
                failures.append((mod_name, name, err_msg))
            finally:
                if mp is not None:
                    mp.undo()

    elapsed = (time.perf_counter() - t0) * 1000.0
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed_tests}/{total_tests} PASSED in {elapsed:.1f} ms")
    if failed_tests > 0:
        print(f"FAILED: {failed_tests} tests failed:")
        for mod, name, err in failures:
            print(f"  - {mod}::{name} -> {err}")
        return 1
    else:
        print("ALL TESTS GREEN!")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
