# ico_data_collector
Collects data about ICOs and exports them to a CSV file for further analysis

## Prerequisites
Install all needed dependencies with pip3
```
pip3 install -r requirements.txt
```

## Usage
To start the script run the scraper.py file with python3
```
python3 scraper.py
```

Once all IDs are retrieved from ICObench, the corresponding ico details will be saved in the csv file. In case the scraping is stopped somehow you can easily continue it by running the command again. You can see if all data is downloaded by checking the output_check.json file. If a scraping session got interrupted and you do not want to continue the session, just change the status in the output_check.json file to "complete".

When all details are scraped, the name of the corresponding csv file will be expanded by the date. 
If you run the script again the old csv file will be moved to the archive file.

## Configuration
Add your ICObench public and private Key to the config.json file