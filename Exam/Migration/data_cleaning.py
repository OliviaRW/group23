import csv 
import numpy as np
import pandas as pd
import string as stringmodule
import lemmy
import collections
from unicodedata import normalize
import re
import matplotlib.pyplot as plt



def lemmatize_strings(body_text, language = 'da'):
    """Function to lemmatize a string or a list of strings, i.e. remove prefixes. Also removes punctuations.
    
    -- body_text: string or list of strings
    -- language: language of the passed string(s), e.g. 'en', 'da' etc.
    """
    
    if isinstance(body_text, str):
        body_text = [body_text] #Convert whatever passed to a list to support passing of single string
    
    if not hasattr(body_text, '__iter__'):
        raise TypeError('Passed argument should be a sequence.')
    
    #sr = stopwords.words('danish')
    lemmatizer = lemmy.load(language) #load lemmatizing dictionary

    #delete -- punctuation = r'?:!.,;)(-.,/#!$%^&*;:{}=\-_`~()`\'' #Characters that are considered punctuation
    
    lemma_list = [] #list to store each lemmatized string 

    word_regex = re.compile('[a-zA-Z0-9æøåÆØÅ]+')

    for string in body_text:
        #remove punctuation and split words
        matches = word_regex.findall(string)

        with open('stopord.txt', 'r') as sw:
            #read the stopwords file
            stopwords = sw.read().split('\n')
            #split words and lowercase them unless they are all caps
            lemmatized_string = [word.lower() if not word.isupper() else word for word in matches]
            
            #remove words that are in the stopwords file
            lemmatized_string = [word for word in lemmatized_string if not word in stopwords] 
            
            #lemmatize each word and choose the shortest word of suggested lemmatizations
            lemmatized_string = [min(lemmatizer.lemmatize('', word), key=len) for word in lemmatized_string]

            #remove words that are in the stopwords file
            lemmatized_string = [word for word in lemmatized_string if not word in stopwords] 

        
        lemma_list.append(' '.join(lemmatized_string))

    return lemma_list if len(lemma_list) > 1 else lemma_list[0] #return list if list was passed, else return string

def count_occurences(body_text, dictionary = None, lemmatize = False, **kw):
    """Function to count occurences of words in either a string or list of strings present in dictionary. 
    Returns a list of dictionaries or a single dictionary.

    -- body_text: string or list of strings.
    -- dictionary: list of strings to be counted.
    -- lemmatize: bool, 
    """

    #counter_list = [] #list to store dictionary for each string in body_text

    if lemmatize:
        body_text = lemmatize_strings(body_text, **kw) #lemmatize if requested
    
    if isinstance(body_text, str):
        body_text = [body_text] #Convert whatever passed to a list to support passing of single string

    if not hasattr(body_text, '__iter__'):
        raise TypeError('Passed argument should be a sequence.')

    #for string in body_text: 
    #    counter = collections.Counter(body_text.split())
    #    counter_list.append({key: counter[key] for key in dictionary})
    if dictionary:
        return [collections.Counter({key: string.count(key) for key in dictionary}) for string in body_text]
    else:
        return [collections.Counter(string.split(' ')) for string in body_text]

def graph_word_frequencies(dictionary):
    df = pd.read_csv('dr_contents.csv', header = 0)
    grouped_df = df.groupby('Date month')['Text'].apply(lambda x: ' '.join(x))
    freq_df = pd.DataFrame(count_occurences(grouped_df, dictionary = dictionary, lemmatize = True, language = 'da'), index = grouped_df.index)
    fig, ax = plt.subplots()
    x = freq_df.index
    for column in freq_df.columns:
        ax.plot(x, freq_df[column], label = column)
    
    ax.legend()
    
    ax.set_xticklabels(x, rotation = 45) #rotate labels

    #remove most labels
    for i, label in enumerate(ax.get_xticklabels()):
        if i % 12 != 0 and i % 6 != 0:
            label.set_visible(False)

    plt.show()

    

if __name__ == "__main__":
    dictionary = ['flygtning', 'migrant', 'asylansøg', 'indvandre', "immigrant"]
    #print(graph_word_frequencies(dictionary))
    
    df = pd.read_csv('dr_contents.csv', header = 0)
    counts = count_occurences(df['Text'], dictionary=dictionary, lemmatize = True)
    #print(pd.Series([sum(count.values()) for count in counts]))
    dr_frequent_articles = df[pd.Series(sum(count.values()) for count in counts)>2]
    dr_frequent_articles.to_csv('dr_frequent_articles.csv', header = True, index = False)


    