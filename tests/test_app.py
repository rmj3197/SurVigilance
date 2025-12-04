"""
Test file to check if the landing page is loaded correctly and all buttons are displayed
"""

from streamlit.testing.v1 import AppTest


def setup_app():
    # Load the app relative to the repo root where tests run
    at = AppTest.from_file("../SurVigilance/ui/_app.py", default_timeout=30)
    return at


def test_num_retries_input():
    at = setup_app()
    at.run()
    assert at.number_input(key="num_retries").value == 5


def test_who_vigiaccess_selection():
    at = setup_app()
    at.run()

    at.button(key="vigiaccess").click().run()
    assert at.session_state["selected_database"] == "WHO VIGIACCESS"


def test_faers_selection():
    at = setup_app()
    at.run()
    at.button(key="faers").click().run()
    assert at.session_state["selected_database"] == "USA FAERS"


def test_vaers_selection():
    at = setup_app()
    at.run()
    at.button(key="vaers").click().run()
    assert at.session_state["selected_database"] == "USA VAERS"


def test_lareb_selection():
    at = setup_app()
    at.run()
    at.button(key="lareb").click().run()
    assert at.session_state["selected_database"] == "NL LAREB"


def test_nz_medsafe_selection():
    at = setup_app()
    at.run()
    at.button(key="nzsmars").click().run()
    assert at.session_state["selected_database"] == "NZ MEDSAFE"


def test_dma_selection():
    at = setup_app()
    at.run()
    at.button(key="dma").click().run()
    assert at.session_state["selected_database"] == "DK DMA"


def test_daen_selection():
    at = setup_app()
    at.run()
    at.button(key="daen").click().run()
    assert at.session_state["selected_database"] == "AU DAEN"
