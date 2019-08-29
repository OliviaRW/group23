from dependencies import *
from data_cleaning import *

def plot1():
    """
    Plot of Statistics Denmark data up against number of articles with mentionings of 'asylansøg'.
    """
    fmt = DateFormatter(r'%y-%m')

    article_data = article_volume_by_word(pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/dr_frequent_articles.csv', header = 0), dictionary = ['asylansøg'], groupby = 'w', lemmatize = True)
    article_data.index = article_data.index.to_timestamp()
    article_data = article_data[article_data.index.year >= 2010] #Include only data from 2010 and beyond

    dst_data = pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/asylansøgninger.csv', header = 0, index_col = 'Date')
    dst_data.index = pd.to_datetime(dst_data.index.str.replace('K', 'Q')) #This replacement is necessary for Pandas to parse the dates 
    dst_data = dst_data[dst_data.index.year >= 2010] #Include only data from 2010 and beyond

    fig, ax2 = plt.subplots(figsize = (15, 4))

    ax1 = ax2.twinx() #add a second axis

    plt.title("Number of asylum applications and number of articles mentioning 'asylansøg'\n2010 - 2020")

    #Plot first ax
    color = (0.5688000000000001, 0.86, 0.33999999999999997)
    ax1.plot(article_data['asylansøg'], color = color, label = 'Articles')
    ax1.set_ylabel('Number of articles', color = color)
    ax1.tick_params('y', color = color)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())

    ax1.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2.5))

    #plot means
    first_mean_end_date = datetime.date(2014, 7, 1) #date that the refugee-crisis was considered begun
    third_mean_start_date = datetime.date(2016, 4, 1) #date that the refugee-crisis was considered ended

    first_mean = article_data[article_data.index.date <= first_mean_end_date]\
                    .groupby(pd.Grouper(freq = 'w'))\
                    .sum().mean()

    second_mean = article_data[(first_mean_end_date <= article_data.index.date) & (article_data.index.date <= third_mean_start_date)]\
                    .groupby(pd.Grouper(freq = 'w'))\
                    .sum().mean()

    third_mean = article_data[article_data.index.date >= third_mean_start_date]\
                    .groupby(pd.Grouper(freq = 'w'))\
                    .sum().mean()

    color = 'black'
    ax1.hlines(y = first_mean, xmin = datetime.date(2010, 1, 1), xmax = first_mean_end_date, color = color, linestyle = '--', label = 'Article mean  (x-span shows over which period)')
    ax1.hlines(y = second_mean, xmin = first_mean_end_date, xmax = third_mean_start_date, color = color, linestyle = '--')
    ax1.hlines(y = third_mean, xmin = third_mean_start_date, xmax = datetime.date(2020, 1, 1), color = color, linestyle = '--')

    #Set limits
    ax1.set_ylim([0, 50])
    ax1.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    
    #Plot second ax
    color = (0.86, 0.3712, 0.33999999999999997)
    ax2.bar(x = dst_data.index, 
            height = dst_data['Asylansøgninger'], 
            width = 93, #This is approximately 3 months in the graph
            align = 'edge', #leftalign
            color = color, 
            label = 'Asylum applications')
    ax2.set_ylabel('Number of asylum applications', color = color)
    ax2.tick_params('y', color = color)
    ax2.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))

    #Add legend, which is cumbersome due to the twin-xaxis
    p1, l1 = ax1.get_legend_handles_labels()
    p2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(p1+p2, l1+l2, loc = 'upper left')

    plt.show()

def plot2():
    """
    Plot of total number of articles from DR.
    """
    fmt = DateFormatter(r'%Y-%m') #formatter for x-axis

    df = pd.read_csv('cleaned_dr_article_counts.csv', index_col = 'Date')
    df.index = pd.to_datetime(df.index) #convert to datetime
    grouped_df = df.groupby(pd.Grouper(freq = 'm')).count()['Title'] #Groupby year and month

    fig, ax = plt.subplots(figsize = (18, 4))

    plt.title('Number of articles on dr.dk from the news category\n01-01-2010 - 31-08-2019')

    #Plotting of outer ax
    ax.plot(grouped_df, label = 'Number of articles')

    #Format x-axis
    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
    ax.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    #Format y-axis
    ax.set_ylabel('Number of articles')
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(250))

    #include mean
    mean = df.groupby(pd.Grouper(freq = 'm')).count()['Title'].mean() #calculate monthly mean
    ax.axhline(y = mean, xmin = 0, xmax = 1, color = 'black', linestyle = '--', label = 'Mean')

    ax.legend(loc = 'upper left')

    #Plotting of inner ax
    grouped_df = df[datetime.date(2013, 1, 1):datetime.date(2015, 1, 1)]\
                        .groupby([pd.Grouper(freq = 'm'), 'Subcategory'])\
                        .count()['Title'] #group by year, month and subcategory
    grouped_df = grouped_df.unstack(level=0).T #unstack and transpose for plotting

    inner_ax = ax.inset_axes([0.65, 0.65, 0.20, 0.3]) #create inner ax

    #Format x-axis
    inner_ax.set_xticklabels(grouped_df.index, 
                            rotation = 35, 
                            fontdict = {'fontsize': 'x-small'}, 
                            horizontalalignment = 'right')
    inner_ax.xaxis.set_major_formatter(fmt)
    inner_ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
    #Format y-axis
    inner_ax.set_ylabel('Number of articles', fontsize = 'x-small')
    inner_ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(250))
    [label.set_fontsize('x-small') for label in inner_ax.get_yticklabels()]

    for column in grouped_df.columns:
        inner_ax.plot(grouped_df[column], label = column) #Plot every subcategory to inner-ax

    inner_ax.legend(title = 'Subcategory', 
                    loc = 'upper right',
                    bbox_to_anchor = (1.7, 1.1),
                    ncol = 2,
                    fontsize = 'x-small')


    plt.show()

def plot3():
    """
    Plot of total number of articles from our Dataset.
    """
    fmt = DateFormatter(r'%Y-%m') #formatter for x-axis

    df = pd.read_csv('dr_frequent_articles.csv', index_col = 'Publish date')
    df.index = pd.to_datetime(df.index) #convert to datetime
    grouped_df = df.groupby(pd.Grouper(freq = 'w')).count()['Title'] #Groupby year and month

    fig, ax = plt.subplots(figsize = (18, 4))

    #Plotting of outer ax
    ax.bar(x = grouped_df.index, height = grouped_df, width = 7, label = 'Number of articles', color = (0.86, 0.3712, 0.33999999999999997))

    #Format x-axis
    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
    ax.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    #Format y-axis
    ax.set_ylabel('Number of articles')
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(250))

    plt.show()

def get_modifiers(df, dictionary, remove_stopwords_ = True, n = 1):
    strings = [string.split(' ') for string in lemmatize_strings(df['Text'], remove_stopwords_ = False)]
    articles = []
    for string in strings:
        for word in dictionary:
            modifiers = []
            stop = False
            while not stop:
                try:
                    idx = string.index(word)
                    modifiers.append(tuple(string[idx-n:idx]))
                    string = string[idx+1:]
                except:
                    stop = True
            articles.append(modifiers)
    if remove_stopwords_:
        articles = [collections.Counter(remove_stopwords(lst)) for lst in articles]
    else: 
        articles = [collections.Counter(lst) for lst in articles]

    pd.DataFrame(articles).to_csv('modifiers.csv')

def contains_string(text, string):
    """Helper function for article_volume_by_words.
    
    -- text: text to be checked for string
    -- string: string to be checked for in text
    """
    return 1 if string in str(text) else 0

def article_volume_by_word(df, dictionary, groupby = 'w', lemmatize = False, **kw):
    """Function that counts the number of articles containing each of the words in dictionary.
    Returns a dataframe with groupby as index and words as columns.

    -- df: Dataframe contaning the articles.
    -- dictionary: list of words to look for in articles.
    -- groupby: code that pandas should group the datetime columnn by.
    -- lemmatize: bool that indicates wether the text should be lemmatized
    -- **kw: keyword arguments for lemmatize_string()
    """

    if lemmatize:
        df['Text'] = lemmatize_strings(df['Text'], **kw) #lemmatize if requested

    df['Publish date'] = pd.to_datetime(df['Publish date'])

    counts = {} #Dictionary to hould Series of counts for each word in dictionary
    
    for string in dictionary:
        grouped_df = df['Text'].apply(contains_string, string = string) #Check if text contains string
        counts[string] = grouped_df.groupby(df['Publish date'].dt.to_period(groupby)).sum() #Group and sum

    return pd.DataFrame.from_dict(counts)

def plot_word_frequencies(df, dictionary = None, top_n = None):
    """Plots a plot of word frequencies over time.

    -- df: dataframe containing word counts, with x as index and words as columns
    -- dictionary: words that should be included in the plot
    -- top_n: if no dictionary is passed the function plots the top_n most common words
    """

    fig, ax = plt.subplots()
    x = df.index

    if dictionary:
        for column in dictionary:
            ax.plot(x, df[column], label = column)
    else:
        for column in list(df.columns):
            ax.plot(x, df[column], label = column)

    ax.legend()
    
    ax.set_xticklabels(x, rotation = 45) #rotate labels

    #remove most labels
    for i, label in enumerate(ax.get_xticklabels()):
        if i % 11 != 0 and i % 5 != 0:
            label.set_visible(False)

    plt.show()

def word_frequencies(dictionary = None):
    df = pd.read_csv('dr_frequent_articles.csv', header = 0, parse_dates = ['Publish date']) #load data

    grouped_df = df.groupby(df['Publish date'].dt.to_period('w'))['Text'].apply(lambda x: ' '.join(x)) #group by month and join strings within the same month.
    counts = count_occurences(grouped_df, dictionary = dictionary, lemmatize = True, language = 'da') #count words

    if not dictionary:
        dictionary = [[c[0] for c in count.most_common(10)] for count in counts]
        counts = [{key: count[key] for key in dictionary} for dictionary, count in zip(dictionary, counts)]

    freq_df = pd.DataFrame(counts, index = grouped_df.index) #dataframe of counts with words as columns and months as index

    freq_df.to_csv('dr_wordfrequencies.csv', header = True)

if __name__ == "__main__":
    plot3()