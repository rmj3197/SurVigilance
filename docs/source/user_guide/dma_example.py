import os

from SurVigilance.ui.scrapers import scrape_dma_sb


def main():
    out_dir = "dma_out"
    os.makedirs(out_dir, exist_ok=True)

    med = "paracetamol"

    df = scrape_dma_sb(medicine=med, output_dir=out_dir, headless=True)
    print(df.head())


if __name__ == "__main__":
    main()
