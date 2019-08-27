from dependencies import *

class dr_scraper():
    def __init__(self, logfile, links_file = 'dr_links.csv', contents_file = 'dr_contents.csv'):
        self.connector = Connector(logfile)
        self.delay = 0.5
        self.links_filename = 'dr_links.csv'
        self.contents_filename = 'dr_contents.csv'
        self.article_counts_filename = 'dr_article_counts.csv'
    
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
                    response, _ = self.connector.get(url, 'Datagathering searchterm: {0}, page: {1}'.format(searchterm, page))
                except:
                    print('Break at page {0} of searchterm {1}'.format(page, searchterm))
                    break
                soup = BeautifulSoup(response.text, features='lxml')
                article_tags = soup.findAll('a', attrs = {'class': 'heading-medium'})
                
                if not article_tags:
                    print('Break at page {0} of searchterm {1}'.format(page, searchterm))
                    break
                
                article_links += [a['href'] for a in article_tags]
                page += 1

                time.sleep(random.uniform(self.delay, self.delay*1.5))
            
            filename = 'dr_links_searchterm_{}.csv'.format(searchterm)
            
            pd.DataFrame({'Link': article_links, 'Searchterm': searchterm}).to_csv(filename, header = True, index = False)
            
            filenames.append(filename)

        #Concatenate the batch-files just created
        df = pd.concat([pd.read_csv(filename, header = 0) for filename in filenames], axis = 0)

        if os.path.isfile(self.links_filename):
            df = pd.concat([pd.read_csv(self.links_filename, header = 0), df], axis = 0) #if existing links-file, concatenate new with existing

        df.drop_duplicates('Link', inplace = True) #Drop duplicate URLs

        df.to_csv(self.links_filename, index = False)

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
                response, _ = self.connector.get(link, 'data_gathering')

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

            time.sleep(random.uniform(self.delay, self.delay*1.5))

        return articles

    def batcher(self, article_links = None, batch_size = 100):
        """This function splits the links into batches, that is scraped and saved into seperate batch-files.
        All batch-files are then merged to a single file. This is to ensure that all the data does not get lost,
        should an error be raised during runtime."""

        if not article_links:
            article_links = pd.read_csv(self.links_filename, header = 0)['Link']

        if os.path.isfile(self.contents_filename): #if existing contentsfile
            contents_df = pd.read_csv(self.contents_filename, header = 0)
            article_links = [link for link in article_links if not contents_df['URL'].str.contains(link).any()] #to avoid scraping the same URL twice

        filenames = [] #Storing filenames to append later

        for i in range(0, len(article_links), batch_size):
            #Get content from batch and save to a file
            filename = 'dr_contents_article_{0}_to_{1}.csv'.format(i, i+batch_size)
            batch = article_links[i: i+batch_size]
            pd.DataFrame(self.get_dr_article_contents(batch)).to_csv(filename, header = True, index = False)
            filenames.append(filename) #save filename for later
        
        df = pd.concat([pd.read_csv(filename, header = 0) for filename in filenames], axis = 0) #concat all batch-files

        if os.path.isfile(self.contents_filename): #if existing contentsfile, append that to new files
            df = pd.concat([contents_df, df], axis = 0)
        
        df['Publish date'] = pd.to_datetime(df['Publish date']) #parse dates
        df['Date month'] = pd.to_datetime(df['Publish date']).dt.to_period('M') #add column with "YYYY-mm"
        
        df.dropna(how = any, axis = 0, inplace = True) #Drop rows contaning nan values

        df.to_csv(self.contents_filename, header = True, index = False) #save the complete file

        for filename in filenames: #delete batch-files
            os.remove(filename) #no need to check for existence as the files were just created

    
    def get_dr_article_count(self, start, end, project_name = 'Get article counts'):
        """Gets publish date, title and url for all articles published for each day in the range defined by start and end.

        -- start: start date as string or DateTime
        -- end: end date as string or DateTime
        -- project_name: name of project, passed to Connector
        """
        date_rng = pd.date_range(start, end) #generate date range
        strdate_rng = [date.strftime(r'%d%m%Y') for date in date_rng] #Format used in the URL
        baseurl = 'https://www.dr.dk/nyheder/allenyheder/{}'
        
        counter = []

        for date, strdate in zip(date_rng, strdate_rng):
            article = {}

            print('Now at date {}'.format(date))
            try:
                response, _ = self.connector.get(baseurl.format(strdate), project_name)
                soup = BeautifulSoup(response.text, features = 'lxml')
                section_tag = soup.find('section', attrs = {'class': 'dr-list'}) #section tag containing list of articles from that date
                
                article['Date'] = date
                articlelist = section_tag.findAll('article', attrs = {'class', 'heading-small'}) #each article is contained in an <article>

                counter += [{'Date': date, 
                            'Title': article.find('a').text, 
                            'URL': 'https://www.dr.dk/' + article.find('a')['href']} 
                            for article in articlelist] #add articles to counter

                time.sleep(random.uniform(self.delay, self.delay*1.5))
            except:
                print('\n{} raised an error.\n'.format(date))

        df = pd.DataFrame(counter)

        if os.path.isfile(self.article_counts_filename):
            df = pd.concat([pd.read_csv(self.article_counts_filename, header = 0), df], axis = 0)
            df['Date'].drop_duplicates(inplace = True)
        
        df.to_csv(self.article_counts_filename, header = True, index = False)

def scraping_section(dr_scraper_):
    searchterms = ['indvandrer']
    dr_scraper_.get_dr_article_links(searchterms = searchterms, start = '2007-01-01', end = '2009-12-31')
    dr_scraper_.batcher()

if __name__ == "__main__":
    dr_scraper_ = dr_scraper('dr_log.csv')

    #scraping_section(dr_scraper_)

    dr_scraper_.get_dr_article_count('01-01-2007', '21-08-2019', project_name = 'Test')