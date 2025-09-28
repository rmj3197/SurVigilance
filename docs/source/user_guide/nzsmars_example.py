import os

from SurVigilance.ui.scrapers import scrape_medsafe_sb


def main():
    out_dir = "nzsmars_out"
    os.makedirs(out_dir, exist_ok=True)

    term = "atorvastatin"
    search_type = "medicine"  # or "vaccine"

    df = scrape_medsafe_sb(
        searching_for=search_type,
        drug_vaccine=term,
        output_dir=out_dir,
        headless=True,
    )
    print(df.head())


if __name__ == "__main__":
    main()
