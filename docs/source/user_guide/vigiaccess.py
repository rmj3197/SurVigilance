"""
Even though SurVigilance is a GUI application to download data from various safety databases,
we have also kept the possibility for a user to interact in a programmatic manner to download the data.
This vignette demonstrates how to access the different databases programmatically and download the required data."
"""

import os

from SurVigilance.ui.scrapers import scrape_vigiaccess_sb


def main():
    out_dir = "vigi_out"
    os.makedirs(out_dir, exist_ok=True)

    med = "aspirin"

    df = scrape_vigiaccess_sb(medicine=med, output_dir=out_dir, headless=True)
    print(df.head())


if __name__ == "__main__":
    main()
