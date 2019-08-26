import csv 
import numpy as np
import pandas as pd
import string as stringmodule
import lemmy
import collections
from unicodedata import normalize
import re
import matplotlib.pyplot as plt

def contains_string(text, string):
    """Helper function for article_volume_by_words.
    
    -- text: text to be checked for string
    -- string: string to be checked for in text
    """
    return 1 if string in str(text) else 0

def word_frequencies(dictionary = None):
    df = pd.read_csv('dr_frequent_articles.csv', header = 0, parse_dates = ['Publish date']) #load data

    grouped_df = df.groupby(df['Publish date'].dt.to_period('w'))['Text'].apply(lambda x: ' '.join(x)) #group by month and join strings within the same month.
    counts = count_occurences(grouped_df, dictionary = dictionary, lemmatize = True, language = 'da') #count words

    if not dictionary:
        dictionary = [[c[0] for c in count.most_common(10)] for count in counts]
        counts = [{key: count[key] for key in dictionary} for dictionary, count in zip(dictionary, counts)]

    freq_df = pd.DataFrame(counts, index = grouped_df.index) #dataframe of counts with words as columns and months as index

    freq_df.to_csv('dr_wordfrequencies.csv', header = True)

def remove_stopwords(lst):
    with open('stopord.txt', 'r') as sw:
        #read the stopwords file 
        return [word for word in lemmatized_string if not word in stopwords]

def lemmatize_strings(body_text, language = 'da', remove_stopwords_ = True):
    """Function to lemmatize a string or a list of strings, i.e. remove prefixes. Also removes punctuations.
    
    -- body_text: string or list of strings
    -- language: language of the passed string(s), e.g. 'en', 'da' etc.
    """
    
    if isinstance(body_text, str):
        body_text = [body_text] #Convert whatever passed to a list to support passing of single string
    
    if not hasattr(body_text, '__iter__'):
        raise TypeError('Passed argument should be a sequence.')
    
    lemmatizer = lemmy.load(language) #load lemmatizing dictionary
    
    lemma_list = [] #list to store each lemmatized string 

    word_regex = re.compile('[a-zA-Z0-9æøåÆØÅ]+') #All charachters and digits i.e. all possible words

    for string in body_text:
        #remove punctuation and split words
        matches = word_regex.findall(string)

        with open('stopord.txt', 'r') as sw:
            #read the stopwords file
            stopwords = sw.read().split('\n')
            #split words and lowercase them unless they are all caps
            lemmatized_string = [word.lower() if not word.isupper() else word for word in matches]
            
            #remove words that are in the stopwords file
            if remove_stopwords_:
                lemmatized_string = remove_stopwords(lemmatized_string)
            
            #lemmatize each word and choose the shortest word of suggested lemmatizations
            lemmatized_string = [min(lemmatizer.lemmatize('', word), key=len) for word in lemmatized_string]

            #remove words that are in the stopwords file
            if remove_stopwords_:
                lemmatized_string = remove_stopwords(lemmatized_string)

        lemma_list.append(' '.join(lemmatized_string))

    return lemma_list if len(lemma_list) > 1 else lemma_list[0] #return list if list was passed, else return string

def count_occurences(body_text, dictionary = None, lemmatize = False, **kw):
    """Function to count occurences of words in either a string or list of strings present in dictionary. 
    Returns a list of dictionaries or a single dictionary.

    -- body_text: string or list of strings.
    -- dictionary: list of strings to be counted. If None every word is counted
    -- lemmatize: bool that indicates wether the text should be lemmatized
    -- **kw: keyword arguments for lemmatize_string()
    """

    if lemmatize:
        body_text = lemmatize_strings(body_text, **kw) #lemmatize if requested
    
    if isinstance(body_text, str):
        body_text = [body_text] #Convert whatever passed to a list to support passing of single string

    if not hasattr(body_text, '__iter__'):
        raise TypeError('Passed argument should be a sequence.')

    if dictionary:
        return [collections.Counter({key: string.count(key) for key in dictionary}) for string in body_text]
    else:
        return [collections.Counter(string.split(' ')) for string in body_text]

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
        counts[string] = grouped_df.groupby(df['Publish date'].dt.to_period('w')).sum() #Group and sum

    return pd.DataFrame.from_dict(counts)

def get_frequent_articles(df, dictionary, n = 3):
    """Function to filter out articles that does not contain a certain amount of words in dictionary.
    
    -- df: DataFrame containing articles. Must have a 'Text' column.
    -- dictionary: words that should be counted as significant.
    -- n: the minimum number of dictionary words an article should contain to be considered 'frequent'
    """

    counts = count_occurences(df['Text'], dictionary = dictionary, lemmatize = True)

    dr_frequent_articles = df[pd.Series(sum(count.values()) for count in counts) >= 3]

    dr_frequent_articles.to_csv('dr_frequent_articles.csv', header = True, index = False)

def clean_article_counts(filename, categories, subcategories = None):
    """Function to remove articles from uninteresting categories.

    -- filename: Path to file contaning articles and url
    -- categories: list of categories that should be kept
    """

    df = pd.read_csv(filename, header = 0)

    categories_series = df['URL'].str\
                        .extract(r'https://www.dr.dk//(\w+/?\w+)/')[0]\
                        .apply(lambda x: x.split('/') if '/' in x else [x, np.nan]) #apply regex to extract categories
    
    df['Category'] = categories_series.str[0]
    df['Subcategory'] = categories_series.str[1]

    df = pd.concat([df[df['Category'] == category] for category in categories]) #Remove categories not in list

    if subcategories: #remove subcategories not in list
        df = pd.concat([df[df['Subcategory'] == subcategory].copy() for subcategory in subcategories])

    df.to_csv('cleaned_' + filename, header = True, index = False)

def clean_dr_articles():
    df = pd.read_csv('dr_contents.csv', header = 0)
    dictionary = ['flygtning', 'migrant', 'asylansøg', 'indvandre', 'immigrant']
    
    get_frequent_articles(df, dictionary)

    clean_article_counts('dr_article_counts.csv', ['nyheder'])


if __name__ == "__main__":
    df = pd.read_csv('article_volume_by_word.csv', header = 0, index_col = 'Publish date')
    plot_word_frequencies(df, dictionary=['flygtning', 'asylansøg'])