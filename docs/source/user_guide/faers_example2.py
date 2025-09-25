import os

from SurVigilance.ui.scrapers import download_file


def main():
    # Please note the year and quarters in this url should be changed corresponding to data to be downloaded.
    # Also for data prior to Q4 2012, please use url : https://fis.fda.gov/content/Exports/aers_ascii_YYYYQQ.zip
    url = "https://fis.fda.gov/content/Exports/faers_ascii_2025q1.zip"
    out_dir = "faers_out"
    os.makedirs(out_dir, exist_ok=True)

    path = download_file(url=url, download_dir=out_dir)

    # Show size of downloaded file
    size_bytes = os.path.getsize(path)
    size_mb = size_bytes / (1024**2)
    print(f"Downloaded file size: {size_bytes} bytes ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
