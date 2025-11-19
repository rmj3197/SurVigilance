"""
Test file to check if the landing page is loaded correctly and all buttons are displayed
"""

from streamlit.testing.v1 import AppTest


def setup_app():
    # Load the app relative to the repo root where tests run
    at = AppTest.from_file("../SurVigilance/ui/_app.py")
    return at


def test_who_vigiaccess_selection():
    at = setup_app()
    at.run()
    at.button[7].click().run()
    assert at.session_state["selected_database"] == "WHO VIGIACCESS"


def test_faers_selection():
    at = setup_app()
    at.run()
    at.button[5].click().run()
    assert at.session_state["selected_database"] == "USA FAERS"


def test_vaers_selection():
    at = setup_app()
    at.run()
    at.button[6].click().run()
    assert at.session_state["selected_database"] == "USA VAERS"


def test_lareb_selection():
    at = setup_app()
    at.run()
    at.button[3].click().run()
    assert at.session_state["selected_database"] == "NL LAREB"


def test_nz_medsafe_selection():
    at = setup_app()
    at.run()
    at.button[4].click().run()
    assert at.session_state["selected_database"] == "NZ MEDSAFE"


def test_dma_selection():
    at = setup_app()
    at.run()
    at.button[2].click().run()
    assert at.session_state["selected_database"] == "DK DMA"


def test_daen_selection():
    at = setup_app()
    at.run()
    # Click the AU DAEN database button and verify selection
    at.button[1].click().run()
    assert at.session_state["selected_database"] == "AU DAEN"
