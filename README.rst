
.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - **Category**
     - **Badges**
   * - **Usage**
     - |License: GPL v3| |Downloads|
   * - **Release**
     - |PyPI - Version| |Build and upload to PyPI| |Netlify Documentation Status|
   * - **Development**
     - |codecov| |CodeFactor| |Ruff|
.. image:: https://raw.githubusercontent.com/rmj3197/SurVigilance/refs/heads/master/docs/source/_static/survigilance_sticker.png
   :target: https://survigilance.netlify.app/
   :height: 150
   :alt: SurVigilance Logo
   :align: left

Introduction
------------

SurVigilance is designed to access and collect data from various
safety databases located across the globe. The primary focus of this
application is to provide a unified interface to researchers to access
data on adverse events that may be associated with the usage of
pharmaceutical drugs or vaccines.

Currently, SurVigilance supports the following databases: 

- FAERS
- VAERS
- VigiAccess
- Lareb
- DAEN
- DMA
- Medsafe

Installation Overview
----------------------

SurVigilance is available on PyPI and can be installed using ``pip install SurVigilance``

**Google Chrome** is required to run **SurVigilance**. You can download it here:
`https://www.google.com/chrome/ <https://www.google.com/chrome/>`_

Any operating system and architecture in which Google Chrome and other dependencies are available should be able to run this application.

**Note:** **Chromium** is different from **Google Chrome**. Please ensure that Google Chrome is installed.

Details on additional dependencies can be found in the `Installation Guide <https://survigilance.netlify.app/getting_started/installation.html>`__.

Usage
-----

The easiest way to use SurVigilance to download data is by running the
following lines of code:

.. code:: py

   from SurVigilance.ui import UI

   UI().run()

This would instantiate a Streamlit dashboard in browser, and you can use
the graphical user interface to navigate between the various databases
and download data.

Authors
-------

-  **Raktim Mukhopadhyay** Email: raktimmu@buffalo.edu

-  **Marianthi Markatou** Email: markatou@buffalo.edu

Maintainer
----------

| **Raktim Mukhopadhyay**
| Email: raktimmu@buffalo.edu

Documentation
-------------

The documentation is hosted on Netlify at -
https://survigilance.netlify.app/

Community
---------

For installing the development version, please download the code files
from the master branch of the GitHub repository. Please note that
installation from GitHub might be buggy, for the latest stable release
please download using ``pip``. For downloading from GitHub, use the
following instructions:

.. code:: bash

   git clone https://github.com/rmj3197/SurVigilance.git
   cd SurVigilance
   pip install -e .

Contributing Guide
~~~~~~~~~~~~~~~~~~

Please refer to the `Contributing
Guide <https://survigilance.netlify.app/development/CONTRIBUTING.html>`__.

Code of Conduct
~~~~~~~~~~~~~~~

The code of conduct can be found at `Code of
Conduct <https://survigilance.netlify.app/development/CODE_OF_CONDUCT.html>`__.

License
-------

This project uses the `GPL-3.0
license <https://github.com/rmj3197/SurVigilance/blob/master/LICENSE>`__,
with a full version of the license included in the repository.

Funding Information
-------------------

The work has been supported by Kaleida Health Foundation Award # 82114.

Disclaimer
----------

-  SurVigilance is not affiliated with, endorsed by, or supported by the
   administrators, maintainers, or owners of any safety databases it can
   access.
-  All database names and trademarks are the property of their
   respective owners.
-  We gratefully acknowledge the organizations that maintain the **FAERS**, 
   **VAERS**, **VigiAccess**, **Lareb**, **DAEN**, **DMA**, and **Medsafe** 
   databases, whose efforts make these datasets publicly accessible.

.. |License: GPL v3| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://github.com/rmj3197/SurVigilance/blob/master/LICENSE
.. |Downloads| image:: https://static.pepy.tech/badge/SurVigilance
   :target: https://pepy.tech/project/SurVigilance
.. |PyPI - Version| image:: https://img.shields.io/pypi/v/SurVigilance
.. |Build and upload to PyPI| image:: https://github.com/rmj3197/SurVigilance/actions/workflows/publish.yml/badge.svg
   :target: https://github.com/rmj3197/SurVigilance/actions/workflows/publish.yml
.. |Netlify Documentation Status| image:: https://api.netlify.com/api/v1/badges/e358958d-8ae8-4f45-9dbe-52849e2e71bc/deploy-status
   :target: https://app.netlify.com/projects/survigilance/deploys
.. |codecov| image:: https://codecov.io/gh/rmj3197/SurVigilance/graph/badge.svg?token=8Q6S051RSC
   :target: https://codecov.io/gh/rmj3197/SurVigilance
.. |CodeFactor| image:: https://www.codefactor.io/repository/github/rmj3197/survigilance/badge
   :target: https://www.codefactor.io/repository/github/rmj3197/survigilance
.. |Ruff| image:: https://github.com/rmj3197/SurVigilance/actions/workflows/ruff.yml/badge.svg
   :target: https://github.com/rmj3197/SurVigilance/actions/workflows/ruff.yml
