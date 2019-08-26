import requests, time, os, random
import pandas as pd 
import numpy as np
from bs4 import BeautifulSoup
from scraping_class import Connector
import collections
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from data_cleaning import *
import matplotlib
import datetime
import seaborn as sns

def plot1():
    fmt = DateFormatter(r'%y-%m')

    article_data = data_cleaning.article_volume_by_word(pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/dr_frequent_articles.csv', header = 0), dictionary = ['asylansøg'], groupby = 'D', lemmatize = True)
    article_data.index = article_data.index.to_timestamp()
    article_data = article_data[article_data.index.year >= 2010]

    dst_data = pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/asylansøgninger.csv', header = 0, index_col = 'Date')
    dst_data.index = pd.to_datetime(dst_data.index.str.replace('K', 'Q'))
    dst_data = dst_data[dst_data.index.year >= 2010]

    fig, ax2 = plt.subplots(figsize = (15, 4))

    ax1 = ax2.twinx()

    plt.title("Number of asylum application and number of articles mentioning 'asylansøg', 2010 - 2020")

    color = 'lightgray'
    ax1.plot(article_data['asylansøg'], color = color)
    ax1.set_ylabel('Number of articles', color = color)
    ax1.tick_params('y', colors = color)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())

    ax1.set_ylim([0, 50])
    ax1.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    
    color = 'black'
    ax2.bar(x = dst_data.index, height = dst_data['Asylansøgninger'], width = 93, align = 'edge', color = color)
    ax2.set_ylabel('Number of asylum applications', color = color)
    ax2.tick_params('y', colors = color)

    plt.show()

def plot2():
    fmt = DateFormatter(r'%y-%m')

    df = pd.read_csv('cleaned_dr_article_counts.csv')
    df = df.groupby('Date').count()

    fig, ax = plt.subplots(figsize = (15, 4))

    ax.plot(df)
    ax.set_ylabel('Number of articles')

def get_modifiers(df, dictionary, remove_stopwords = True, n = 1):
    df['Text'] = lemmatize_strings(df['Text'], 
    modifiers = []
    for word in dictionary:
        stop = False
        while not stop:
            try:
                idx = string.index(word)
                modifiers.append(tuple(string[idx-2:idx]))
                string = string[idx+1:]
            except:
                stop = True


if __name__ == "__main__":
    plot1()
