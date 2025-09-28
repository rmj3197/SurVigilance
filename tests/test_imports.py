"""
Basic import checks for the SurVigilance package and its submodules.
"""

import importlib

import pytest

import SurVigilance


def test_version_is_string():
    from SurVigilance import __version__

    assert isinstance(__version__, str)


def test_all_matches_submodules():
    from SurVigilance import __all__, submodules

    assert __all__ == submodules


def test_dir_returns_all():
    from SurVigilance import __all__, __dir__

    assert __dir__() == __all__
    assert dir(SurVigilance) == __all__


def test_getattr_imports_submodule():
    from SurVigilance import __getattr__

    mod = __getattr__("ui")
    assert mod is importlib.import_module("SurVigilance.ui")


def test_getattr_returns_global():
    from SurVigilance import __getattr__, __version__

    assert __getattr__("__version__") == __version__


def test_invalid_attribute_message():
    from SurVigilance import __getattr__

    with pytest.raises(AttributeError) as ei:
        __getattr__("__some__")
    assert str(ei.value) == "Module 'SurVigilance' has no attribute '__some__'"
