import os

from SurVigilance.ui.scrapers.scrape_faers import scrape_faers_sb


def main():
    out_dir = "faers_out"
    os.makedirs(out_dir, exist_ok=True)

    df = scrape_faers_sb(output_dir=out_dir, headless=True)
    print(df.head())


if __name__ == "__main__":
    main()
