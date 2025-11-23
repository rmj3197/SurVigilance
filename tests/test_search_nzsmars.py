"""
Test if the streamlit UI for NZ MEDSAFE is working
"""

from streamlit.testing.v1 import AppTest


def test_nzsmars_selection():
    at = AppTest.from_file("../SurVigilance/ui/pages/search_page_nzsmars.py")
    at.run()
    at.button[0].click().run(timeout=3000)
    assert at.success[0].value == "Data Fetching Complete!"
