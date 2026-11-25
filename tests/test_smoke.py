"""Smoke test: every module of the monolith can be imported."""

import importlib

import pytest

MODULES = ["data_platform", "features", "scouting", "simulation", "api"]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name: str) -> None:
    assert importlib.import_module(name) is not None
