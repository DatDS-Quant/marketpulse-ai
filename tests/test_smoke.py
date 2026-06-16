"""Smoke tests for the MarketPulse AI project structure."""

from __future__ import annotations

import importlib


def test_project_packages_can_be_imported() -> None:
    """Verify that the planned package structure can be imported.

    Input: none.
    Returns: nothing; pytest treats the test as passing if all imports succeed.
    Why it exists: Module 0 should provide a stable package structure before
    real features are added.
    """

    package_names = [
        "src",
        "src.collectors",
        "src.processing",
        "src.storage",
        "src.intelligence",
        "src.rag",
        "src.agents",
        "src.evals",
        "src.utils",
    ]

    for package_name in package_names:
        imported_package = importlib.import_module(package_name)
        assert imported_package is not None

