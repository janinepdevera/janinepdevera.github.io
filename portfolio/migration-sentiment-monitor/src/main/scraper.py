"""
A scraper for migration related news articles in Reuters (https://www.reuters.com/).
"""

# standard libraries
import re
import csv
import os
import numpy as np
from tqdm import tqdm
import time

# web services
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By

#os.chdir('portfolio/migration-sentiment-monitor/src/')

class NewsScraper():
    def __init__(self):
        self.base_url = 'https://www.reuters.com'
        self.search_url = '/site-search/?query=migration+OR+migrant&date=any_time&offset='
        self.num_pages = 10
        self.soup = None
        self.result_pages = None
        self.news_urls = None
        self.urls_file = 'urls.csv'
        
    def _parse_page(self, link):
        '''Method for extracting html elements from website'''
        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')

        #driver = webdriver.Chrome(service = ChromeService(ChromeDriverManager().install()))
        driver = webdriver.Safari()
        driver.get(link)
        time.sleep(20)
        self.soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        driver.quit()
        return self.soup
    
    def _load_existing_urls(self):
        '''Method for loading existing urls from file'''
        existing_urls = set()
        try:
            with open(self.urls_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        existing_urls.add(row[0])
        except FileNotFoundError:
            pass  
        return existing_urls

    def _save_new_urls(self, new_urls):
        '''Method to save new urls to file'''
        with open(self.urls_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for url in new_urls:
                writer.writerow([url])

    def get_result_pages(self):
        '''Method for saving urls to paged results'''
        self.result_pages = []
        for i in range(1, self.num_pages*20, 20):
            page_link = f'{self.base_url}{self.search_url}{i}'
            self.result_pages.append(page_link)
        return self.result_pages

    def get_news_urls(self):
        '''Method for saving individual news urls'''
        self.news_urls = []
        existing_urls = self._load_existing_urls()
        result_pages = self.get_result_pages()
        new_urls = []

        for result in result_pages:
            main_soup = self._parse_page(result)
            main_class = main_soup.find_all(class_='basic-card__container__1y8wi')

            for item in main_class:
                url = item.attrs['href']
                url = f'{self.base_url}{url}'
                if url not in existing_urls:
                    new_urls.append(url)
                    self.news_urls.append(url)
        
        self._save_new_urls(new_urls)
        return self.news_urls
    
    def extract_text(self):
        '''Method for extracting title, date, and text from individual news articles'''
        no_urls = len(self.news_urls)
        print(f"Number of links: {no_urls}")

        with tqdm(total=no_urls, desc="Extracting text") as pbar:
            with open('raw.csv', 'a', newline='', encoding='utf-8') as csvfile:
                #fieldnames = ["title", "date", "text", "link"]
                #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer = csv.writer(csvfile)

                for url in self.news_urls:
                    url_soup = self._parse_page(url)
                    title_elem = date_elem = maintext_elem = None

                    try:
                        title_elem = url_soup.find('h1', attrs={'data-testid': 'Heading'})
                        date_elem = url_soup.find(class_='date-line__date___kNbY')
                        maintext_elem = url_soup.find_all('div', attrs={'data-testid': re.compile(r'^paragraph-\d+$')})

                    except Exception as e:
                        print(f"Error on link {url}: {e}")

                    title = title_elem.text if title_elem else np.nan
                    date = date_elem.text if date_elem else np.nan
                    maintext = ' '.join([para.text for para in maintext_elem]) if maintext_elem else np.nan

                    # writer.writerow({
                    #     "title": title,
                    #     "date": date,
                    #     "text": maintext,
                    #     "link": str(url)
                    # })

                    writer.writerow([title, date, maintext, str(url)])

                    pbar.update(1)

    def run_scraper(self):
        self.get_news_urls()
        self.extract_text()

### 

# reuters_scraper = NewsScraper()
# reuters_scraper.run_scraper()






    




