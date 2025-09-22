# test_ui.py
from unittest.mock import patch
from SurVigilance.ui import UI


def test_ui_runs_streamlit():
    with patch("streamlit.web.cli.main") as mock_main:
        ui = UI()
        ui.run()
        mock_main.assert_called_once()
