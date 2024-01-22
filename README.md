# alert-scraper

Python script using selenium that performs web-scraping of a certain cybersecurity SaaS platform to show the full configuration of all alerts on the platform in an excel.

This functionality was not present in the platform yet was crucial for the team to perform alert reviews for clients - thus the script was created to solve this issue and achieved widespread adoption.

This script saved thousands of hours amongst hundreds of people. Before, the entire alert configuration had to be painstakingly manually copied and pasted - this either resulted in having to spend 4+ tedious hours per client per quarter, or, more commonly, just skipping the process entirely, leaving the client with a sub-optimal configuration.

Bit messy and hacky but it works very well. Will break if/when the front-end is redesigned. Would ideally be coded into the API of the product itself. Originally had tutorial videos too.



Original readme:

## Example Usage

python3 alertscraper.py --username='<site username>' --password='<site password>' --secret='<site TOTP secret>'

python3 alertscraper.py --username='you+site@cybersecuritysaasplatform.com' --password='password1' --secret='123456'

python3 alertscraper.py --username='you+site@cybersecuritysaasplatform.com' --password='password1' --secret='LQPSMZYEOAMDSAO'

python3 alertscraper.py --username='you+site@cybersecuritysaasplatform.com' --password='password1'

Do not click around inside the Chrome window or use other programs or tabs, or the data may become corrupted

To stop the program while it is running, close the Chrome window or right click to quit on the taskbar

TOP TIP: to really supercharge this program, be sure to export the Benchmarking data from the site for the last 90 days, create a pivot table, 
and perform a VLOOKUP to get the number of times each alert has triggered in the last 90 days. For help see the tutorial video in the Drive.

## Use Cases

Gets all alerting rule config data from the site and outputs to file

## Requirements

Python modules 'selenium', 'pyotp', and 'webdriver-manager' must be installed using pip, execute below commands in Mac Terminal:
    pip3 install selenium
    pip3 install pyotp
    pip3 install webdriver-manager

## Bug Fixing

Error about missing arguments, make sure you have encapsulated all arguments with single quotes '' e.g. 'firstname.lastname@cybersecuritysaasplatform.com'
NB different text editors can use a slightly different symbol for single quote ' e.g. 'Notes' program on Mac will give you [WRONG]‘[WRONG] when you actually need '
Extremely subtle difference but it will break if you use the wrong quote symbol. For best results copy and paste from this text document or type directly into Terminal

Error about missing arguments, can also be caused if the password has certain symbols, to be safe use only alphanumeric characters in password

Error mentioning that pip is not installed (likely if you have never installed Python modules before), execute below commands, then execute above commands:
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py

Error mentioning M1/M2 etc. MacBooks, try run the following two commands to get the latest webdriver_manager build from the GitHub repository:
    pip uninstall webdriver_manager
    pip install git+https://github.com/SergeyPirogov/webdriver_manager@master

Error mentioning Xcode, be sure you have the Xcode program installed from the Mac App Store.

Error mentioning git, be sure you have git installed, which comes bundled with Xcode above.

Error mentioning Command Line Tools, install them when prompted.

Error mentioning chromedriver unexpectedly exiting with a status code, make sure your Google Chrome is up to date with the following steps:
Open your regular Chrome and go to -> three dots in top right -> Settings then at bottom left About Chrome -> make sure you are using the latest version

Error mentioning LEGACY when you are not on a legacy site. Try use https://app.cybersecuritysaasplatform.com/live/sc/home?type=alert as the --link.

***ERROR*** inside cells in the excel file, the advanced query logic was too complex for the program to parse, manually add logic for that cell if required

## Required Arguments

Encapsulate all arguments with single quotes '' e.g. 'firstname.lastname@cybersecuritysaasplatform.com'

--username / STRING / site username (required)

--password / STRING / site password (required)

## Optional Arguments

--secret / STRING / site 6-digit 30-second secret from 2FA OR alphanumeric secret key (only appears when you create the 2FA the first time and see the QR code)
    not required for clients without 2FA

--link / STRING / link to Edit Alerting Rules Page as full url: https://...
    no longer used, it is hard coded, leaving in for legacy purposes to avoid breaking everyone's workflows

--outfile / FILEPATH / Location of txt output

--multiorg / if the client is legacy multiorg, add this arg to collect the organisation each alert is assigned to
