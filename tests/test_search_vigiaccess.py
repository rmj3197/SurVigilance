"""
Test if the streamlit UI for VigiAccess is working
"""

from streamlit.testing.v1 import AppTest


def test_vigiaccess_selection():
    at = AppTest.from_file("../SurVigilance/ui/pages/search_page_vigiaccess.py")
    at.run()
    at.button[0].click().run(timeout=200)
    assert at.success[0].value == "Data Fetching Complete!"
