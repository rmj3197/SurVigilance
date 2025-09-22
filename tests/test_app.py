"""
Test file to check if the landing page is loaded correctly and all buttons are displayed
"""

from streamlit.testing.v1 import AppTest


def setup_app():
    at = AppTest.from_file("../SurVigilance/ui/_app.py")
    return at


def test_who_vigiaccess_selection():
    at = setup_app()
    at.run()
    at.button[1].click().run()
    assert at.session_state["selected_database"] == "VIGIACCESS"


def test_faers_selection():
    at = setup_app()
    at.run()
    at.button[2].click().run()
    assert at.session_state["selected_database"] == "FAERS"


def test_vaers_selection():
    at = setup_app()
    at.run()
    at.button[3].click().run()
    assert at.session_state["selected_database"] == "VAERS"


def test_lareb_selection():
    at = setup_app()
    at.run()
    at.button[4].click().run()
    assert at.session_state["selected_database"] == "LAREB"
