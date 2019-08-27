from dependencies import *
from data_cleaning import *

def plot1():
    sns.set_palette(colorpalette)
    fmt = DateFormatter(r'%y-%m')

    article_data = article_volume_by_word(pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/dr_frequent_articles.csv', header = 0), dictionary = ['asylansøg'], groupby = 'D', lemmatize = True)
    article_data.index = article_data.index.to_timestamp()
    article_data = article_data[article_data.index.year >= 2010]

    dst_data = pd.read_csv('/Users/sebastianbaltser/Documents/GitHub/group23/Exam/Migration/asylansøgninger.csv', header = 0, index_col = 'Date')
    dst_data.index = pd.to_datetime(dst_data.index.str.replace('K', 'Q'))
    dst_data = dst_data[dst_data.index.year >= 2010]

    fig, ax2 = plt.subplots(figsize = (15, 4))

    ax1 = ax2.twinx()

    plt.title("Number of asylum application and number of articles mentioning 'asylansøg'\n2010 - 2020")

    color = 'lightblue'
    ax1.plot(article_data['asylansøg'], color = color)
    ax1.set_ylabel('Number of articles', color = color)
    ax1.tick_params('y', color = color)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())

    ax1.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2.5))

    ax1.set_ylim([0, 50])
    ax1.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    
    color = 'lightgreen'
    ax2.bar(x = dst_data.index, height = dst_data['Asylansøgninger'], width = 93, align = 'edge', color = color)
    ax2.set_ylabel('Number of asylum applications', color = color)
    ax2.tick_params('y', color = color)
    ax2.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(500))

    plt.show()

def plot2():
    fmt = DateFormatter(r'%Y-%m') #formatter for x-axis

    df = pd.read_csv('cleaned_dr_article_counts.csv', index_col = 'Date')
    df.index = pd.to_datetime(df.index) #convert to datetime
    grouped_df = df.groupby(pd.Grouper(freq = 'm')).count()['Title'] #Groupby year and month

    fig, ax = plt.subplots(figsize = (18, 4))

    plt.title('Number of articles on dr.dk from the news category\n01-01-2010 - 31-08-2019')

    #Plotting of outer ax
    ax.plot(grouped_df)

    #Format x-axis
    ax.xaxis.set_major_formatter(fmt)
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator())
    ax.set_xlim([datetime.date(2010, 1, 1), datetime.date(2019, 8, 31)])
    #Format y-axis
    ax.set_ylabel('Number of articles')
    ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(250))


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

if __name__ == "__main__":
    plot1()
