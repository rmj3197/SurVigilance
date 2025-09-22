"""
Test if the streamlit UI for FAERS is working
"""

from streamlit.testing.v1 import AppTest
import time


def test_faers_listing():
    at = AppTest.from_file("../SurVigilance/ui/pages/search_page_faers.py")
    at.run()

    at.button[0].click().run(timeout=200)
    assert at.success[0].value == "Data Fetching Complete!"

    container = at.main 
    checkbox = container.checkbox[0]
    checkbox.check().run()
    assert checkbox.value

    download_button = next(b for b in at.button if "Download" in b.label)
    download_button.click().run(timeout = 600)

