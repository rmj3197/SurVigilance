"""
Basic import checks for the SurVigilance package and its submodules.
"""

import pytest

import SurVigilance


def test_version_is_string():
    from SurVigilance import __version__

    assert isinstance(__version__, str)


def test_dir_available():
    assert dir(SurVigilance) is not None


def test_submodules_exposed_via_getattr():
    from SurVigilance import submodules

    for name in submodules:
        assert getattr(SurVigilance, name, None) is not None


def test_invalid_attribute_raises_attribute_error():
    with pytest.raises(AttributeError):
        _ = SurVigilance.__some__
