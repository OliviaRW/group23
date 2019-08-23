import csv 
import numpy as np
import pandas as pd
import string as stringmodule
import lemmy
from nltk import word_tokenize
from nltk.corpus import stopwords
import collections



def lemmatize_strings(body_text, language = 'da'):
    """Function to lemmatize a string or a list of strings, i.e. remove prefixes. Also removes punctuations.
    
    -- body_text: string or list of strings
    -- language: language of the passed string(s), e.g. 'en', 'da' etc.
    """
    
    if isinstance(body_text, str):
        body_text = [body_text] #Convert whatever passed to a list to support passing of single string
    
    if not hasattr(body_text, '__iter__'):
        raise TypeError('Passed argument should be a sequence.')
    
    sr = stopwords.words('danish')
    lemmatizer = lemmy.load(language) #load danish lemmatizing dictionary

    punctuation = r'?:!.,;)(-.,/#!$%^&*;:{}=\-_`~()`\'' #Characters that are considered punctuation
    
    lemma_list = [] #list to store each lemmatized string 

    for string in body_text:
        #remove punctuation
        string = string.translate(str.maketrans('', '', stringmodule.punctuation))

        #Split sentence into words and stopwords
        lemmatized_string = [word for word in word_tokenize(str(string)) if not word in sr] 
        
        #lemmatize each word and choose the shortest word of suggested lemmatizations
        lemmatized_words = [min(lemmatizer.lemmatize('', word), key=len) for word in lemmatized_string]
        
        lemma_list.append(' '.join(lemmatized_words))

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
        return [{key: collections.Counter(string.split(' '))[key] for key in dictionary} for string in body_text]
    else:
        return [collections.Counter(string.split(' ')) for string in body_text]
    return 

#def clean_data(df)

if __name__ == "__main__":
    df = pd.read_csv('dr_contents.csv', header = 0)
    grouped_df = ' '.join(df.groupby('Date month')['Text'].apply(lambda x: ' '.join(x))[-10:])
    counters = count_occurences(grouped_df, lemmatize = True, language = 'da')
    for c in counters:
        print(c.most_common(20), end = '\n\n')

    