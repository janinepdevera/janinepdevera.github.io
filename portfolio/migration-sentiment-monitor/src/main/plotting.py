"""
Routines for plotting sentiment charts and descriptive statistics.
"""

# data wrangling 
import pandas as pd
from pandas.tseries.offsets import DateOffset

# visualization
import plotly.express as px
import plotly.graph_objects as go 
import plotly.io as pio
from scipy import signal

# local functions
from . import analyzer

# other settings
pio.templates.default = 'plotly_white'
colors = ['#0D3C4F',  '#3B91B3', '#168578', '#8AB17D', '#E9C46A',
          '#E76F51', '#B03C1F', '#F4A261', '#1C6D6F', '#CC5638']


def plot_time(daily_df: pd.DataFrame, show_average=False, start_date=None):
    daily_df = daily_df[daily_df['date'] >= start_date]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['compound'],
        mode='lines',
        marker=dict(size=0.7, color='#246781'),
        name='sentiment score'
    ))
    fig.update_traces(
        hovertemplate='Date: %{x}<br> Score: %{y:.2f}<extra></extra>',
        )

    if show_average:
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=signal.savgol_filter(daily_df['compound'],
                                    53,
                                    3),
            mode='lines',
            marker=dict(size=1, color='#CC5638'),
                name='moving average'
            ))
        fig.update_traces(
            hovertemplate='Date: %{x}<br> Score: %{y:.2f}',
            )

    return fig

def plot_region(region_df: pd.DataFrame, start_date = None):
    region_df = region_df[region_df['month'] >= start_date - DateOffset(months=1)]
        
    fig = px.bar(
        region_df, x='month', y='compound', 
        color='region', color_discrete_sequence=colors,
        barmode='group'
    )
    fig.update_traces(
        hovertemplate='Date: %{x}<br> Score: %{y:.2f}<br>',
    )
    fig.update_layout(
            xaxis={
                'title': 'month'   
            },
            yaxis={
                'title': 'sentiment score'
            },
        )

    return fig

def plot_topic_bar(topic_df: pd.DataFrame):
    fig = px.bar(
        topic_df, x='compound', y='topic_name', orientation='h', 
        color='value', color_discrete_sequence=['#B03C1F',  '#168578']
        )
    fig.update_traces(
        hovertemplate='Score: %{x:.2f}<br><extra></extra>',
    )
    fig.update_layout(
            xaxis={
                'title': 'sentiment score'   
            },
            yaxis={
                'title': 'topic'
            },
            showlegend=False
        )
    return fig

def plot_topic_scatter(token_df: pd.DataFrame):
    plot_df = token_df.groupby('topic_name').head(15)
    plot_df['color'] = ['neg' if x < 0 else 'pos' for x in plot_df['compound']]
    plot_df['date'] = pd.to_datetime(plot_df['date']).dt.strftime('%Y-%m-%d')

    fig = px.scatter(
        plot_df, x='compound', y='topic_name',
        color = 'color', 
        color_discrete_sequence=['#168578', '#B03C1F'],
        hover_data=['date', 'title']
        )
    #fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="black")
    fig.update_traces(marker=dict(
                        size=20, 
                        opacity=0.8, 
                        line=dict(width=2,
                                  color='black')
                    ),
                  selector=dict(mode='markers'),
                  hovertemplate='Score: %{x:.2f}<br><extra></extra><b>Date:</b> %{customdata[0]}<br><b>Title:</b> %{customdata[1]}<br><extra></extra>')
    fig.update_layout(
            xaxis={
                'title': 'sentiment score'   
            },
            yaxis={
                'title': 'topic'
            },
            showlegend=False
        )
    return fig