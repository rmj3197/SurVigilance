import os

from SurVigilance.ui.scrapers import scrape_daen_sb


def main():
    out_dir = "daen_out"
    os.makedirs(out_dir, exist_ok=True)

    med = "aspirin"

    df = scrape_daen_sb(medicine=med, output_dir=out_dir, headless=True)
    print(f"Data collected: {len(df)} rows, {len(df.columns)} columns")


if __name__ == "__main__":
    main()
