# SurVigilance <img src="https://github.com/rmj3197/SurVigilance/blob/master/docs/source/_static/survigilance_sticker.png?raw=true" align="right" height="138" alt="SurVigilance" />

| Category          | Badge                                                                                                                                                                                                                                                                                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Usage**       | [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/rmj3197/SurVigilance/blob/master/LICENSE) [![Downloads](https://static.pepy.tech/badge/SurVigilance)](https://pepy.tech/project/SurVigilance)                                                                                                                                                                                                                                       |
| **Release**         | ![PyPI - Version](https://img.shields.io/pypi/v/SurVigilance) [![Build and upload to PyPI](https://github.com/rmj3197/SurVigilance/actions/workflows/publish.yml/badge.svg)](https://github.com/rmj3197/SurVigilance/actions/workflows/publish.yml) [![Documentation Status](https://readthedocs.org/projects/survigilance/badge/?version=latest)](https://survigilance.readthedocs.io/en/latest/?badge=latest)                                                                                                                      |
| **Development**  | [![codecov](https://codecov.io/gh/rmj3197/SurVigilance/graph/badge.svg?token=8Q6S051RSC)](https://codecov.io/gh/rmj3197/SurVigilance) [![CodeFactor](https://www.codefactor.io/repository/github/rmj3197/survigilance/badge)](https://www.codefactor.io/repository/github/rmj3197/survigilance) [![Ruff](https://github.com/rmj3197/SurVigilance/actions/workflows/ruff.yml/badge.svg)](https://github.com/rmj3197/SurVigilance/actions/workflows/ruff.yml) |


## Introduction

SurVigilance is designed to access and collect data from various safety databases located across the globe. The primary focus of this application is to provide an unified interface to researchers to access data on adverse events that may be associated the usage of pharmaceutical drugs or vaccines.

Currently, SurVigilance suppots the following databases: 
- FAERS
- VAERS
- VigiAccess
- Lareb

## Installation using `pip`

``pip install SurVigilance``

## Usage

The easiest way to use SurVigilance to download data is by running the following lines of code: 

```py
from SurVigilance.ui import UI

UI().run()
```

This would instantiate a streamlit dashboard in browser, and you can use the graphical user interface to navigate between the various databases and download data. 

Details on dependencies can be found in the [Installation Guide](getting_started/index.rst).

## Authors

- **Raktim Mukhopadhyay** 
  Email: [raktimmu@buffalo.edu](mailto:raktimmu@buffalo.edu)  

- **Marianthi Markatou** 
  Email: [markatou@buffalo.edu](mailto:markatou@buffalo.edu)  

## Maintainer

**Raktim Mukhopadhyay**  
Email: [raktimmu@buffalo.edu](mailto:raktimmu@buffalo.edu)

## Documentation

The documentation is hosted on `Read the Docs` at - <https://survigilance.readthedocs.io/en/latest/>

## Community

For installing the development version, please download the code files from the master branch of the Github repository.
Please note that installation from Github might be buggy, for the latest stable release please download using `pip`.
For downloading from Github, use the following instructions:

```bash
git clone https://github.com/rmj3197/SurVigilance.git
cd SurVigilance
pip install -e .
```

### Contributing Guide

Please refer to the [Contributing Guide](https://survigilance.readthedocs.io/en/latest/development/CONTRIBUTING.html).

### Code of Conduct

The code of conduct can be found at [Code of Conduct](https://survigilance.readthedocs.io/en/latest/development/CODE_OF_CONDUCT.html).

## License

This project uses the [GPL-3.0 license](https://github.com/rmj3197/SurVigilance/blob/main/LICENSE), with a full version of the license included in the repository.

## Funding Information
The work has been supported by Kaleida Health Foundation Award \# 82114.

## Disclaimer

- SurVigilance is not affiliated with, endorsed by, or supported by the administrators, maintainers, or owners of any safety databases it can access.
- All database names and trademarks are the property of their respective owners.
- We gratefully acknowledge the organizations that maintain the FAERS, VAERS, VigiAccess, and Lareb databases, whose efforts make these datasets publicly accessible.
