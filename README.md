# NamUs Scraper
Python scraper for collecting metadata and files for Missing-, Unidentified-, and Unclaimed-person cases from the [National Missing and Unidentified Persons System (NamUs)](https://www.namus.gov) organization. The scraper uses APIs used for internal purposes at NamUs and may therefore change at any point.

To work around the 10.000 case search limit, cases are found by searching on a per-state basis. This may miss some cases if they are entered incorrectly! Compare result counts with the ones available on the site. 

⚠️ This requests a large amount of data. Please run it responsibly!

## Installation
```
sudo pip3 install requests
sudo pip3 install grequests
sudo pip3 install face_recognition
```

## Scraping
```
python3 scrape-data.py   # Downloads all metadata related to the cases.
python3 scrape-files.py  # Downloads all files related to the scraped cases.
python3 process-faces.py # Extracts faces from the downloaded images.
```
