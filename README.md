# Deeds
## Getting Started
### 1. Download the latest Google Chrome (if not already installed)
Link to Chrome download: https://www.google.com/chrome/
### 2. Install python (if not already installed)
1. Go to https://www.python.org/downloads/release/python-3102/
2. Scroll to the bottom, and choose your installer
3. Assuming your system is 64-bit, click "Windows installer (64-bit)"
4. Open installer, make sure you click "Add Python 3.8 to PATH"
5. Choose default installation
6. https://www.youtube.com/watch?v=uKHVNKd3f20&ab_channel=AmitThinks also explains how to do this
### 3. Setup Scraper
Double-click the batch file `scraper_setup.bat` to run. This will install all necessary tools and frameworks not mentioned above.
### 4. Edit Login Information
1. Right-click `login.txt` and select "Edit"
2. Type in your login information for the Larimer County Records website as follows:<br>
      ```
      Username: your_usename@email.com
      Password: pwd_here
      ```
3. Save file before exiting. 
## Using the Scraper
1. Click to run Deed_Scraper.exe. This will open a Command Prompt window, which will then ask you for a date range (see Considerations below for more information).
2. Enter start date in format `MM/DD/YYYY`, press `Enter`
3. Enter end date in format `MM/DD/YYYY`, press `Enter`
4. Allow scraper to run unimpeded. A window will open that will log into the website, and then show the document that is currently being looked at. <b>NOTE:</b> This document will only change when it's found a record that doesn't have a release of deed document attached to it, so don't be surprised if you sometimes see the same document on the screen for a little while. 
5. When it has finished, the document window will close and you'll be left with an Excel file named `Deeds_StartDate_thru_EndDate.xlsx`
## Considerations
### Deciding when to run the scraper
While running this program, you <b>cannot</b> use your system, or else it will not properly analyze the documents. This is because the scraper relies on taking a screenshot of the first page of a document before it can search the text. If you have other windows open over top, then those can interfere with the screenshot and yield bad results.
The scraper takes a long time to run, largely due to the response times of the Records site. Since it must be left alone during this time, it's wise to run it at the end of the day when you no longer need to use your computer, or even overnight. 
### How long will it take?
On my system, I ran `01/01/2017` thru `01/31/2017` in about 75 minutes. Results may vary depending on number of records in a date range, internet connection, or even processor speed.
### Viewing Results
Since each run of the scraper produces a new Excel workbook, you'll need to simply copy/paste the results into a master spreadsheet.
### First Run
For your first scrape, I'd recommend using the date range `01/01/2017` through `01/17/2017`. This will test all functionality on your system. If it performs similarly to my system, this should take roughly 35 to 40 minutes. 
### Getting Help
If you're seeing issues, it's caused by one of only a couple things. Reach out to me and we can discuss. 
In addition, I can run some scrapes overnight on my side to help you get up to date. Let me know, and I can perform a scrape from `01/01/2017` through `12/31/2019`, and I'll let you handle the rest! Once you're up to date, you can run it periodically just to keep up with current records.
