"""
Routines for data processing and sentiment analysis.
"""

# standard libraries
import pandas as pd
import numpy as np
from datetime import datetime

# text processing
import ssl
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import spacy 
from spacy import displacy
import gensim
from gensim.corpora import Dictionary
from gensim.models import LdaModel, LdaMulticore, CoherenceModel

# local functions
from . import dataloader

def nltk_data():
    """
    Download NLTK data.
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('vader_lexicon')

def load_sentiment_analyzer():
    """
    Load NLTK vader sentiment analyzer.
    """
    nltk_data()
    sentanalyzer = SentimentIntensityAnalyzer()
    return sentanalyzer

def get_sentiment_df(texts_df: pd.DataFrame):
    """
    Create dataframe of news articles with corresponding sentiment scores. 

    Parameters
    ----------
    df_texts: pd.DataFrame
        Dataframe containing the title, date, and main text of news articles. 
    """
    # get sentiment scores
    vader = load_sentiment_analyzer()
    results = [vader.polarity_scores(x) for x in texts_df['text']]
    results = pd.DataFrame.from_dict(results)
    sentiment_df = pd.concat([texts_df, results], axis=1)

    # define time aggregators
    sentiment_df['date'] = sentiment_df['date'].apply(lambda x: datetime.strptime(x, "%d-%b-%y"))
    sentiment_df['month'] = sentiment_df['date'].dt.to_period('M')
    sentiment_df['month'] = sentiment_df['month'].dt.to_timestamp()
    return sentiment_df

def get_daily_df(sentiment_df: pd.DataFrame):
    """
    Create dataframe with average sentiment scores per day. 

    Parameters
    ----------
    df_sentiment: pd.DataFrame
        Dataframe returned by get_sentiment_df.
    """
    daily_df = (
        sentiment_df[['date', 'neg', 'neu', 'pos', 'compound']]
        .groupby(['date']).mean()
        .reset_index()
    )
    return daily_df

def get_region_df(sentiment_df: pd.DataFrame):
    """
    Create dataframe with average sentiment scores per month and by region. 

    Parameters
    ----------
    df_sentiment: pd.DataFrame
        Dataframe returned by get_sentiment_df.
    """
    regions = ['Africa', 'America', 'Asia', 'Europe', 'Middle East']

    for region in regions:
        sentiment_df['region'] = 0

    for region in regions:
        sentiment_df[region] = sentiment_df['text'].apply(lambda x: 1 if region.lower() in x.lower() else 0)

    region_df = sentiment_df.melt(
        id_vars=['date', 'month', 'neu', 'pos', 'neg', 'compound'], 
        value_vars=regions, 
        var_name='region', value_name='value'
    )

    region_df = region_df[region_df['value'] == 1]
    region_df = (
    region_df[['month', 'region', 'neg', 'neu', 'pos', 'compound']]
    .groupby(['month', 'region']).mean()
    .reset_index()
    )
    
    return region_df

def get_token_df():
    token_df = pd.read_pickle('./portfolio/migration-sentiment-monitor/src/main/raw_topics.pkl')
    return token_df

def get_topic_df(token_df: pd.DataFrame):
    topic_df = (
    token_df[['topic', 'topic_name', 'neg', 'neu', 'pos', 'compound']]
    .groupby(['topic', 'topic_name']).mean()
    .reset_index()
    )
    topic_df['value'] = topic_df['compound'].apply(lambda x: 'pos' if x > 0 else 'neg')
    return topic_df








