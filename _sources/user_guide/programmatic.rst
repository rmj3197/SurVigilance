====================================================================
Programmatic Scraping (without using the Graphical User Interface)
====================================================================

Even though SurVigilance is a GUI application to download data from various safety databases, 
we have also kept the possibility for a user to interact in a programmatic manner to download the data.
This vignette demonstrates how to access the different databases programmatically and download the required data.

VigiAccess
==========
In this example, we would like to download data from VigiAccess for the drug "aspirin".

.. exec_code::
   :filename: user_guide/vigiaccess_example.py

Lareb
======
In this example, we would like to download data from Lareb for the drug "paracetamol".

.. exec_code::
   :filename: user_guide/lareb_example.py

FAERS
======
For the FAERS databases, we can download the ZIP files. To see which data files are available 
for different quarters, we should first review the list of available files.

.. exec_code::
   :filename: user_guide/faers_example1.py

From the list of available files, let's try to download the data for Q1 (Jan - Mar), 2025 using the code below.

.. exec_code::
   :filename: user_guide/faers_example2.py

Please note that for downloading the VAERS data, the user needs to provide a CAPTCHA, hence it is not possible to download
the data without opening a GUI. It is for this reason, we have not included the 