from SurVigilance.ui.scrapers.check_internet_connectivity import (
    SITES_TO_CHECK,
    check_all_scraper_sites,
    check_site_connectivity,
)


def test_check_site_connectivity():
    for site in SITES_TO_CHECK:
        reachable, _message = check_site_connectivity(site)
        assert reachable is True, f"{site} is not reachable"


def test_check_all_scraper_sites():
    all_ok, _messages = check_all_scraper_sites()
    assert all_ok is True
    assert len(_messages) == len(SITES_TO_CHECK)
