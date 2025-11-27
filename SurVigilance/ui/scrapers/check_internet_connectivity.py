# Modified from https://www.geeksforgeeks.org/python/how-to-check-whether-users-internet-is-on-or-off-using-python/
import http.client as httplib
from urllib.parse import urlparse

SITES_TO_CHECK = [
    "https://daen.tga.gov.au/medicines-search/",
    "https://laegemiddelstyrelsen.dk/en/sideeffects/side-effects-of-medicines/interactive-adverse-drug-reaction-overviews/",
    "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html",
    "https://www.lareb.nl/en",
    "https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp",
    "https://vaers.hhs.gov/data/datasets.html",
    "https://www.vigiaccess.org/",
]


def check_site_connectivity(url, timeout=5):
    """Checks if a given URL is reachable by making a HEAD request."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            connection = httplib.HTTPSConnection(parsed_url.netloc, timeout=timeout)
        else:
            connection = httplib.HTTPConnection(parsed_url.netloc, timeout=timeout)

        connection.request("HEAD", parsed_url.path or "/")
        connection.getresponse()
        return (
            True,
            f"{url} is reachable.",
        )
    except Exception as e:
        return False, f"{url} is not reachable. Error: {e}."
    finally:
        if "connection" in locals() and connection:
            connection.close()


def check_all_scraper_sites(st_object=None):
    """
    Checks connectivity for all external websites required by the scrapers.

    Returns
    --------
    tuple: A tuple containing:
        - bool: True if all sites are reachable, False otherwise.
        - list: A list of detailed messages for each site's connectivity.
    """
    all_messages = []
    all_ok = True

    if st_object:
        st_object.write("Checking connectivity to required websites...")
    else:
        print("Checking connectivity to required websites...")

    for site in SITES_TO_CHECK:
        reachable, message = check_site_connectivity(site)
        all_messages.append(message)
        if st_object:
            st_object.markdown(message)
        else:
            print(message)
        if not reachable:
            all_ok = False

    return all_ok, all_messages


if __name__ == "__main__":
    check_all_scraper_sites()
