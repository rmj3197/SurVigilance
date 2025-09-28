"""
Test if the streamlit UI for DK DMA is working
"""

from streamlit.testing.v1 import AppTest


def test_dma_selection():
    at = AppTest.from_file("../SurVigilance/ui/pages/search_page_dma.py")
    at.run()
    at.button[0].click().run(timeout=300)
    assert at.success[0].value == "Data Fetching Complete!"
