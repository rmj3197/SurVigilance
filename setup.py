import re
from pathlib import Path

from setuptools import find_packages, setup

NAME = "SurVigilance"
DESCRIPTION = "SurVigilance: An application to collect pharmacovigilance data from multiple safety databases."


def read_version() -> str:
    root = Path(__file__).parent
    init_py = root / "SurVigilance" / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if not m:
        raise RuntimeError("Cannot find __version__ in SurVigilance/__init__.py")
    return m.group(1)


def read_long_description() -> str:
    readme = Path(__file__).parent / "README.md"
    if readme.is_file():
        return readme.read_text(encoding="utf-8")
    return DESCRIPTION


REQUIRES = [
    "streamlit>=1.49.1",
    "seleniumbase>=4.0.0",
    "pandas>=1.5.0",
    "requests>=2.28.0",
]


setup(
    name=NAME,
    version=read_version(),
    description=DESCRIPTION,
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
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
        "Framework :: Streamlit",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=False,
)
