"""
Test if the streamlit UI for AU DAEN is working
"""

from streamlit.testing.v1 import AppTest


def test_daen_selection():
    at = AppTest.from_file("../SurVigilance/ui/pages/search_page_daen.py")
    at.run()
    at.button[0].click().run(timeout=3000)
    assert at.success[0].value == "Data Fetching Complete!"
