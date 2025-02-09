# This project contains implementation of scrapy with selenium for scraping websites effectively.
## Libraries used
- Scrapy==2.11.2
- scrapy-selenium
- selenium
- virtualenv
- selenium stealth
- undetected_chromedriver
- ipython
## project structure
```bash
scraper/
│── scrapy-selenium/
│── venv/
│── scraper/               # Project module
│   ├── spiders/                # Spider definitions
│   │   ├── __init__.py
│   │   ├── quotespider.py        # Custom spider
│   ├── __init__.py
│   ├── items.py                # Define scraped data structure
│   ├── middlewares.py          # Custom middlewares
│   ├── pipelines.py            # Data processing pipelines
│   ├── settings.py             # Scrapy settings
│── scrapy.cfg                  # Scrapy configuration file
│── requirements.txt            # Dependencies
│── README.md                   # Project documentation
```
```bash
## to create virtual env
python -m venv venv
python venv\Scripts\activate
## to create project
scrapy startproject scraper
## go the spider folder
scrapy genspider spidername '##paste webpage url'
## to activate scrapy shell
scrapy shell
```
### Spider Initialization
- Configures Scrapy settings.
- Initializes a headless or non-headless Selenium WebDriver.
- Uses stealth to avoid detection.
### Start Requests (start_requests)
- Visits the main page of the website.
- Initiates a Selenium request.
### Interacting with the Web Page (parse)
- Navigates to the search tab.
- Selects a category (FUL).
- Enters date values in search fields.
- Submits the search query.
- Waits for the results page to load.
- Updates the page source to Scrapy for parsing.
### Extracting Links (parse_data)
- Collects links of individual application pages.
- Opens each link in a new tab.
- Extracts data from each page.
- Iterates through pagination to scrape all available data.
### Parsing Data (parse_data_page)
- Extracts structured data from the details table.
- Stores data in SearchItem.
## 🛠 Scope for Improvement

- **Optimize Selenium WebDriver setup**
  - Remove redundant initialization of the WebDriver.
  - Ensure proper cleanup of WebDriver instances to prevent memory leaks.

- **Improve exception handling**
  - Handle cases where elements might not be present on all pages.
  - Use `try-except` blocks to catch Selenium-specific exceptions (e.g., `NoSuchElementException`, `TimeoutException`).

- **Enhance logging and debugging**
  - Implement structured logging for better traceability.
  - Store logs in a file for later analysis.

- **Reduce reliance on `time.sleep()`**
  - Use explicit waits (`WebDriverWait`) instead of static delays.
  - Optimize waiting conditions to speed up execution.
    





