import os

from SurVigilance.ui.scrapers import scrape_daen_sb


def main():
    out_dir = "daen_out"
    os.makedirs(out_dir, exist_ok=True)

    med = "aspirin"

    result_path = scrape_daen_sb(medicine=med, output_dir=out_dir, headless=True)
    print(f"Saved export to: {result_path}")


if __name__ == "__main__":
    main()
