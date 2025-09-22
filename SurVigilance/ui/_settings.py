"""
Contains the UI class that runs a Streamlit dashboard.
"""

import runpy
import sys
from importlib import resources

DASHBOARD_MODULE = "SurVigilance.ui"


class UI:
    """
    The UI class runs a Streamlit dashboard.
    Please see - for more information.

    Examples
    ---------
        >>> from SurVigilance.ui import UI
        >>> UI().run()
    """

    def __init__(self) -> None:
        pass

    def run(self) -> None:
        """
        The function runs the Streamlit dashboard using runpy.
        """
        sys.argv = [
            "streamlit",
            "run",
            str(resources.files(DASHBOARD_MODULE).joinpath("_app.py")),
            "--theme.base",
            "light",
            "--theme.secondaryBackgroundColor",
            "#E5E4E2",
            "--theme.textColor",
            "#0e0e0e",
            "--browser.gatherUsageStats",
            "false",
            "--client.showSidebarNavigation",
            "false",
        ]
        try:
            runpy.run_module("streamlit", run_name="__main__")
        except SystemExit as e:  # pragma: no cover
            if e.code == 0:
                pass
            else:
                print(f"Dashboard exited with code {e.code}")
