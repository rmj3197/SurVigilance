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


def check_site_connectivity(
    url=None,
    timeout=5,
):
    """
    Checks if a given URL or list of URLs is reachable by making a HEAD request.

    Parameters
    -----------
    url: str or list, optional
        The URL or list of URLs to check for connectivity. If None, SITES_TO_CHECK will be used.
        SITES_TO_CHECK = ["https://daen.tga.gov.au/medicines-search/", "https://laegemiddelstyrelsen.dk/en/sideeffects/side-effects-of-medicines/interactive-adverse-drug-reaction-overviews/",
        "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html", "https://www.lareb.nl/en", "https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp",
        "https://vaers.hhs.gov/data/datasets.html", "https://www.vigiaccess.org/",]

    timeout: int, optional
        The maximum time (in seconds) to wait for a connection. Defaults to 5 seconds.

    Returns
    --------
    tuple or list: If `url` is a string, returns a tuple containing:
        - bool: True if the site is reachable, False otherwise.
        - str: A message indicating the connectivity status.

    If `urls` is a list, returns a list of these tuples.

    Example
    --------
    >>> SITES_TO_CHECK = ["https://daen.tga.gov.au/medicines-search/", "https://laegemiddelstyrelsen.dk/en/sideeffects/side-effects-of-medicines/interactive-adverse-drug-reaction-overviews/",
        "https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html", "https://www.lareb.nl/en", "https://www.medsafe.govt.nz/Projects/B1/ADRSearch.asp",
        "https://vaers.hhs.gov/data/datasets.html", "https://www.vigiaccess.org/",]
    >>> result, message = check_site_connectivity(url=SITES_TO_CHECK)
    >>> print(result)
    """

    if url is None:
        url = SITES_TO_CHECK

    is_single_url = isinstance(url, str)
    if is_single_url:
        urls = [url]
    else:
        urls = url

    results = []
    for url in urls:
        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme == "https":
                connection = httplib.HTTPSConnection(parsed_url.netloc, timeout=timeout)
            else:
                connection = httplib.HTTPConnection(parsed_url.netloc, timeout=timeout)

            connection.request("HEAD", parsed_url.path or "/")
            connection.getresponse()
            results.append(
                (
                    True,
                    f"{url} is reachable.",
                )
            )
        except Exception as e:  # pragma: no cover
            results.append((False, f"{url} is not reachable. Error: {e}."))
        finally:
            if "connection" in locals() and connection:
                connection.close()

    if is_single_url:
        return results[0]
    return results


def check_all_scraper_sites(st_object=None):
    """
    Checks connectivity for all external websites required by the scrapers.

    Parameters
    -----------
    st_object: Streamlit Object
        Streamlit object in which the connectivity status for the
        various databases are shown.

    Returns
    ---------
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

    results = check_site_connectivity()

    for reachable, message in results:
        all_messages.append(message)
        if st_object:
            st_object.markdown(message)
        else:
            print(message)
        if not reachable:
            all_ok = False

    return all_ok, all_messages
