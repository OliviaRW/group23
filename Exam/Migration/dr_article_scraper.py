import requests, time, os, random
import pandas as pd 
import numpy as np
from bs4 import BeautifulSoup
import scrapingclass as sc

class dr_scraper():
    def __init__(self, logfile, links_file = 'dr_links.csv', contents_file = 'dr_contents.csv'):
        self.connector = sc.Connector(logfile)
    
    def get_dr_article_links(self, searchterms, start, end):

        filenames = []

        for searchterm in searchterms:
            article_links = []
            page = 1
            while True:
                print('Now at page {0} of searchterm {1}'.format(page, searchterm))
                
                url = "https://www.dr.dk/search/Result?query={0}&filter_facet_universe=Nyheder&filter_published=between({1}-{2})&page={3}"
                url = url.format(searchterm, start, end, page)

                try:
                    response, id_ = self.connector.get(url, 'Datagathering searchterm: {0}, page: {1}'.format(searchterm, page))
                except:
                    print('Connection error')
                    break
                soup = BeautifulSoup(response.text, features='lxml')
                article_tags = soup.findAll('a', attrs = {'class': 'heading-medium'})
                
                if not article_tags:
                    print('Break at page {0} of searchterm {1}'.format(page, searchterm))
                    break
                
                article_links += [a['href'] for a in article_tags]
                page += 1
                time.sleep(random.uniform(1, 2))
            
            filename = 'dr_links_searchterm_{}.csv'.format(searchterm)
            pd.DataFrame({'Link': article_links, 'Searchterm': searchterm}).to_csv(filename, header = True, index = False)
            filenames.append(filename)

        df = pd.concat([pd.read_csv(filename, header = 0) for filename in filenames], axis = 0)
        df.drop_duplicates('Link', inplace = True)
        
        self.link_filenames = 'dr_links.csv'

        df.to_csv(self.link_filenames, index = False)

        for filename in filenames:
            os.remove(filename) #no need to check for existence as the filenames were just created

    def get_dr_article_contents(self, article_links):
        """Scrapes content from links to DR articles provided in article_links.
        Contents inklude: link, title, publish date, and body text.

        article_links: list of links to DR-articles
        """
        
        articles = []

        for i, link in enumerate(article_links):
            article_data = {}
            try:
                response, id_ = self.connector.get(link, 'data_gathering')

                print('Now at link number {}'.format(i))
                
                soup = BeautifulSoup(response.text, features='lxml')

                article_data['URL'] = link
                body_div = soup.find('article', attrs = {'class': 'dre-article'}) #<div> containing the body of the article

                article_data['Title'] = body_div.find('h1', attrs = {'class': 'dre-article-title__heading'}).text #title
                article_data['Publish date'] = body_div.find('time', attrs = {'class': 'dre-article-byline__date'})['datetime'] #date
                article_data['Text'] = ' '.join(p.text for p in body_div.find('div', attrs = {'itemprop': 'articleBody'}).findAll('p')) #body-text
            except: #if an article does not follow the general structure it is simply not inlcuded
                print('\nThe following link was not parsed:\n{}\n'.format(link))

            articles.append(article_data)

            time.sleep(random.uniform(1, 2))

        return articles

    def batcher(self, article_links = None, batch_size = 100):
        """This function splits the links into batches, that is scraped and saved into seperate batch-files.
        All batch-files are then merged to a single file. This is to ensure that all the data does not get lost,
        should an error be raised during runtime."""

        if not article_links:
            article_links = pd.read_csv(self.link_filenames, header = 0)['Link']

        filenames = []

        for i in range(0, len(article_links), batch_size):
            filename = 'dr_contents_article_{0}_to_{1}.csv'.format(i, i+batch_size)
            batch = article_links[i: i+batch_size]
            pd.DataFrame(self.get_dr_article_contents(batch)).to_csv(filename, header = True, index = False)
            filenames.append(filename)
        
        df = pd.concat([pd.read_csv(filename, header = 0) for filename in filenames], axis = 0) #concat all batch-files
        df['Publish data'] = pd.to_datetime(df['Publish date']) #parse dates
        df.to_csv('dr_contents.csv', header = True, index = False) #save the complete file

        for filename in filenames: #delete batch-files
            os.remove(filename) #no need to check for existence as the files were just created


    
    def get_dr_article_count(start, end, profect_name = 'Get article counts'):
        date_rng = [date.strftime(%d%m%Y) for date in pd.date_range(start, end)]
        url = 'https://www.dr.dk/nyheder/allenyheder/{}'
        for date in date_rng:
            self.connector.get(url.format(date), project_name)
            soup = BeautifulSoup(, features = 'lxml')
            section_tag = soup.find('section', attrs = {'class': 'dr-list'}) #section tag containing list of articles from that date
            len(findAll('article', attrs = {'class', 'heading-small'})) #each article is contained in an <article>

def append_files(files):
    df = pd.concat([pd.read_csv(f, header = 0, sep = ';') for f in files], axis = 0)
    df.to_csv('./data/{}_concat.csv'.format(files[0].split('.')[0]), index = False) #Save to csv named as the first file with 'concat' appended

if __name__ == "__main__":
    #dr_scraper_ = dr_scraper('dr_log.csv')
    #searchterms = ['migrant', 'asylansøg', 'immigrant', 'flygtning']
    #dr_scraper_.get_dr_article_links(searchterms = searchterms, start = '2007-01-01', end = '2013-12-31')
    #dr_scraper_.batcher()

    lst = ['dr_log{}.csv'] #['dr_contents{}.csv', 'dr_links{}.csv', 'dr_log{}.csv']
    for i in range(len(lst)):
        append_files([lst[i].format(''), lst[i].format('2')])
