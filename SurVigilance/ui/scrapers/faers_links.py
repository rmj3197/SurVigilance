"""
Helpers to build FAERS download URLs.

The FAERS ASCII export URLs usually follow the format -
    https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip

- For older years (roughly 2004 - 2012 Q3), files use the legacy
  "AERS" prefix instead of "FAERS", e.g. - https://fis.fda.gov/content/Exports/aers_ascii_2004q4.zip

Where quarter is 1 to 4 for:
    1 -> January - March
    2 -> April   - June
    3 -> July    - September
    4 -> October - December
"""

QUARTER_LABELS = {
    1: "January - March",
    2: "April - June",
    3: "July - September",
    4: "October - December",
}

QUARTER_MONTHS = {
    1: ["January", "February", "March"],
    2: ["April", "May", "June"],
    3: ["July", "August", "September"],
    4: ["October", "November", "December"],
}


def faers_ascii_url(year: int, quarter: int) -> str:  # pragma: no cover
    """Return the FAERS ASCII zip URL for a given year and quarter (1 to 4)."""
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1, 2, 3, or 4")  # pragma: no cover

    if year >= 2013:
        return f"https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip"
    elif year == 2012 and quarter == 4:
        return f"https://fis.fda.gov/content/Exports/faers_ascii_{year}q{quarter}.zip"
    else:
        return f"https://fis.fda.gov/content/Exports/aers_ascii_{year}q{quarter}.zip"
