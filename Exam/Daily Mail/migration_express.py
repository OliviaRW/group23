import requests, time
import pandas as pd 
from selenium import webdriver
from bs4 import BeautifulSoup
import random
from scraping_class import Connector

def get_article_headers():
    connector = Connector('dailymail_logfile.csv')

    article_links = []
    page = 0
    while True:
        print('Now at page {}'.format(page))
        url = "https://www.dailymail.co.uk/home/search.html?offset={0}&size=50&sel=site&searchPhrase=&sort=recent&type=article&topic=Immigration&days=all".format(page*50)
        try:
            response, _ = connector.get(url, 'data_gathering')
        except:
            print('Connection error')
            return article_links
        soup = BeautifulSoup(response.text, features='lxml')
        article_tags = soup.findAll('h3', attrs = {'class': 'sch-res-title'})
        article_tags = [h3.find('a')['href'] for h3 in article_tags]

        if not article_tags:
            print('break at page {}'.format(page))
            break
        
        article_links += article_tags
        page += 1
        time.sleep(random.uniform(0.5, 1))
    
    prefix = 'https://www.dailymail.co.uk'
    article_links = [prefix + suffix for suffix in article_links]
    return article_links

def get_contents(article_links):
    connector = Connector('dailymail_article_data.csv')
    
    articles = []

    for i, link in enumerate(links):
        article_data = {}
        try:
            response, _ = connector.get(link, 'data_gathering')
        except:
            print('\nThe following link was not parsed:\n{}\n'.format(link))
            continue

        print('Now at link number {}'.format(i))
        
        soup = BeautifulSoup(response.text, features='lxml')

        article_data['ID'] = soup.find('meta', attrs = {'name': 'articleid'})['content'] #article ID

        body_div = soup.find('div', attrs = {'id': 'js-article-text'}) #<div> containing the body of the article

        article_data['Title'] = body_div.find('h2') #title
        article_data['Publish date'] = body_div.find('span', attrs = {'class': 'article-timestamp article-timestamp-published'}).text #date
        article_data['Text'] = ' '.join(p.text for p in body_div.find('div', attrs = {'itemprop': 'articleBody'}).findAll('p')) #body-text
        
        articles.append(article_data)

        time.sleep(random.uniform(0.5, 1))

    return articles

if __name__ == "__main__":
    #pd.Series(get_article_headers()).to_csv('dailymail_article_links.csv', header = False) getting data
    links = pd.read_csv('dailymail_article_links.csv', header = None)[1][:100]
    #print(links)
    #pd.DataFrame(get_contents(links)).to_csv('article_data.csv', header = True)

    data = pd.read_csv('article_data.csv', header = 0)
    US_states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado",
  "Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois",
  "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland",
  "Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana",
  "Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York",
  "North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
  "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
  "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming", "ICE", "Homeland"]

    lst = []
    for idx, article in data.iterrows():
        skip = 0
        for state in US_states:
            if state in article['Text']:
                skip = 1
        if skip:
            lst.append(article['ID'])
    
    print(len(lst))
    #data.iloc[lst].to_csv('article_data_filtered.csv', header = True)