import re
from pathlib import Path

from setuptools import find_packages, setup

NAME = "SurVigilance"
DESCRIPTION = "SurVigilance: An application to collect pharmacovigilance data from safety databases around the world."


def read_version() -> str:
    root = Path(__file__).parent
    init_py = root / "SurVigilance" / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if not m:
        raise RuntimeError("Cannot find __version__ in SurVigilance/__init__.py")
    return m.group(1)


def read_long_description() -> str:
    text = (Path(__file__).parent / "README.rst").read_text(encoding="utf-8")
    text = re.sub(r"(?ms)^ *\.\. *raw::.*?(?:\n +\S.*?)*", "", text)
    return text.strip()


REQUIRES = [
    "streamlit>=1.49.1",
    "seleniumbase==4.44.15",
    "pandas>=1.5.0",
    "requests>=2.28.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=6.0.0",
    "openpyxl>=3.1.0",
]

setup(
    name=NAME,
    version=read_version(),
    description=DESCRIPTION,
    long_description=read_long_description(),
    long_description_content_type="text/x-rst",
    python_requires=">=3.10",
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
