# streamlit
import streamlit as st

# standard libs
import pandas as pd 
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv; load_dotenv()

# local packages
import main
from main import dataloader
from main import analyzer
from main import plotting

st.set_page_config(
    page_title='Migration Sentiment Monitor',
    layout='wide',
    initial_sidebar_state='auto',
    menu_items={
        'About': 'Migration Sentiment Monitor v0.1.0-alpha'
    }
)

#st.title('Migration Sentiment Monitor')

with open( "main/styles.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

with st.spinner('Please wait...'):

    # datasets
    if 'results_data' not in st.session_state:
        st.session_state['results_data'] = dataloader.load_data()

    if 'main_data' not in st.session_state:
        st.session_state['main_data'] = analyzer.get_sentiment_df(st.session_state.results_data)

    if 'daily_data' not in st.session_state:
        st.session_state['daily_data'] = analyzer.get_daily_df(st.session_state.main_data)

    if 'region_data' not in st.session_state:
        st.session_state['region_data'] = analyzer.get_region_df(st.session_state.main_data)

    if 'token_data' not in st.session_state:
        st.session_state['token_data'] = analyzer.get_token_df()

    if 'topic_data' not in st.session_state:
        st.session_state['topic_data'] = analyzer.get_topic_df(st.session_state.token_data)

    # metrics selection
    metrics_mapping = {
        "Select one": "home",
        "1. Time series": "time",
        "2. By region": "region",
        "3. By topic": "topic"
    }

    metric = st.selectbox('Select metric', list(metrics_mapping.keys()))
    selected_metric = metrics_mapping[metric]

    if selected_metric == 'home':
            st.markdown(
            """
            <style>
            .centered {
                display: flex;
                justify-content: left;
                align-items: center;
                height: 20vh;
            }
            </style>
            <div class="centered">
                <div>
                    <p>The <b>migration sentiment monitor</b> uses migration-related news articles from the Reuters website.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        #st.write('The **migration sentiment monitor** uses migration-related news articles from the Reuters website.')

    if selected_metric == 'time':
        st.caption('Figure 1. Migration sentiment scores over time')
        st.markdown("""
        <style>
        .stSlider [data-baseweb=slider]{
            width: 40%;
        }
        </style>
        """,unsafe_allow_html=True)
        start_date = st.slider(
            'Start date: ',
            min_value = datetime(2023, 6, 8),
            max_value = datetime(2024, 7, 13), 
            value = datetime(2024, 4, 1),
            format = 'MM-DD-YYYY'
        )
        moving_ave = st.checkbox("Show moving average")
        if moving_ave:
            fig = plotting.plot_time(st.session_state.daily_data, start_date=start_date, show_average=True)
        else: 
            fig = plotting.plot_time(st.session_state.daily_data, start_date=start_date)
        st.plotly_chart(fig, use_container_width=True)  

    if selected_metric == 'region':
        st.markdown("""
        <style>
        .stSlider [data-baseweb=slider]{
            width: 40%;
        }
        </style>
        """,unsafe_allow_html=True)
        start_date = st.slider(
            'Start date: ',
            min_value = datetime(2023, 6, 1),
            max_value = datetime(2024, 7, 1), 
            value = datetime(2024, 1, 1),
            format = 'MM-YYYY'
        )
        fig = plotting.plot_region(st.session_state.region_data, start_date=start_date)
        st.plotly_chart(fig, use_container_width=True)  

    if selected_metric == 'topic':
        topic_views = {
            'Scores for latest 15 articles': 'head',
            'Average score across all articles': 'time'
        }
        view = st.selectbox('Select view', list(topic_views.keys()))
        view = topic_views[view]

        if view == 'head':
            fig = plotting.plot_topic_scatter(st.session_state.token_data)
            
        elif view == 'time':
            fig = plotting.plot_topic_bar(st.session_state.topic_data)
            
        st.plotly_chart(fig, use_container_width=True)
        st.caption("<span style='font-size: smaller;'>Note: Topics are determined through a latent dirichlet allocation (LDA) model.</span>", unsafe_allow_html=True)