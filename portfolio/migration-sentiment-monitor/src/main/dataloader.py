"""
Routines for downloading data from scrapers.
"""

# standard libraries
import pandas as pd
import os

# local functions
from .scraper import NewsScraper

def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'raw.csv')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    texts = (
        pd.read_csv(file_path, header=None)
        .set_axis(['title', 'date', 'text', 'link'], axis=1)
        .dropna(subset=['text'])
        .drop_duplicates(subset='link', keep='last')
        .reset_index(drop=True)
    )
    return texts

def update_data(): 
    ap_scraper = NewsScraper()
    ap_scraper.run_scraper()
    texts = load_data()
    return texts