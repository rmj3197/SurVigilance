import os

from SurVigilance.ui.scrapers import scrape_lareb_sb


def main():
    out_dir = "lareb_out"
    os.makedirs(out_dir, exist_ok=True)

    med = "atorvastatin"

    df = scrape_lareb_sb(medicine=med, output_dir=out_dir, headless=True)
    print(df.head())


if __name__ == "__main__":
    main()
