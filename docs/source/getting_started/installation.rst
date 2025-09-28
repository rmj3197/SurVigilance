Installation
=============

.. title:: Getting Started : contents
.. _installation:


Which Python?
--------------

You’ll need **Python 3.10 or greater** (>=3.10, <3.14).

Installation using ``pip``
----------------------------
SurVigilance is available on PyPI and can be installed using ``pip install SurVigilance``.

Dependencies
-------------
SurVigilance requires the following (arranged alphabetically):

- `beautifulsoup4 <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_ (>= 4.12.0)
- `Google Chrome <https://www.google.com/chrome/>`_ (latest stable)
- `pandas <https://pandas.pydata.org/>`_ (>= 1.5.0)
- `requests <https://requests.readthedocs.io/>`_ (>= 2.28.0)
- `seleniumbase <https://seleniumbase.io>`_ (>= 4.0.0)
- `streamlit <https://streamlit.io/>`_ (>= 1.49.1)

Note: SeleniumBase manages the appropriate WebDriver automatically for Chrome.

Testing
--------
This project uses the Python ``pytest`` package.
To install ``pytest``, please go `here <https://docs.pytest.org/en/latest/getting-started.html#>`_.
To run the tests using ``pytest``, please follow these `instructions <https://docs.pytest.org/en/latest/how-to/usage.html>`_.
Navigate to the tests folder to run the tests. 
