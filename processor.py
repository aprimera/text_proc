import nltk.data
import numpy as np
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from tempfile import NamedTemporaryFile
import webbrowser
import re


def file_reader(file):
    '''Reads an ASCII file and returns its text
    Parameters
    ----------
    file: str 
        Provide the location of the file
    
    Returs
    ----------
    str
        All text read with UTF8 enconding
    '''
    with open(file, 'r', encoding="utf8") as f:
        text = f.read()
    return text


def text_processor(text, add_stop_words=[], stemming=False, lemmatising=False):
    '''Process a text in a string object using the nltk library with some options
    Parameters
    ----------
    text: str 
        Text to be processed
    add_stop_words: list
        List of strings to be added to the nltk.corpus.stopwords
    stemming: bool
        Whether the Stemming option in nltk should be used
    lemmatising: bool
        Whether the Lemmatizer in nltk should be used
    
    Returs
    ----------
    set_words: list
        List of unique different words found in the text
    word: list
        List of all words found in the text in the order found
    sentences: list
        List of all sentences corresponding to the found word
    '''
    stop_words = stopwords.words('english')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(text)
    tokens = word_tokenize(text)
    stop_words = stop_words + list(set([x.lower() for x in add_stop_words]))
    words = [word for word in tokens if word.isalpha()]
    words = [w.lower() for w in words]
    words = [w for w in words if not w in stop_words]
    #print(stop_words)
    if stemming:
        stemmer = SnowballStemmer("english")
        words = [stemmer.stem(w) for w in words]
    if lemmatising:
        lemmmatizer=WordNetLemmatizer()
        words = [lemmmatizer.lemmatize(w.lower()) for w in words]
    set_words = list(set(words))
    return set_words, words, sentences


def data_frame_compiler(set_words, words, sentences, files):
    '''Generates a DataFrame from the list of words, sentences and files.
        HTML markdown to list files and sentences is included
    Parameters
    ----------
    set_words: list
        List of unique different words found in the text
    word: list
        List of all words found in the text in the order found
    sentences: list
        List of all sentences corresponding to the found word
    files: list
        List of all files where words were found
    
    Returs
    ----------
    df: pandas.DataFrame
        Returns a dataframe with a summary of the words found and the sentence location
    '''
    df = pd.DataFrame()
    word_count = []
    sentences_report = []
    files_list = []
    for word in set_words:
        all_sentences = '<ul>'
        all_files = '<ul>'
        for i, sentence in enumerate(sentences):
            if word in sentence.lower():
                all_sentences = all_sentences + '<li>' + sentence + '</li>'# '\n\n' 
                if files[i] not in all_files:
                    all_files = all_files + '<li>' + files[i] + '</li>'
        all_sentences = all_sentences + '</ul>'
        all_files = all_files + '</ul>'
        word_count.append(words.count(word))
        sentences_report.append(sentence_highlighter(all_sentences, word))  
        #sentences_report.append(all_sentences) 
        files_list.append(all_files)
    df['words'] = set_words
    df['count'] = word_count
    df['files'] = files_list
    df['sentences'] = sentences_report
    df.set_index('words', inplace=True)
    #df.reset_index(drop=True, inplace=True)
    df.sort_values('count', ascending=False, inplace=True)
    return df

    
def sentence_highlighter(sentence, word):
    '''Adds additional HTML markup to highlight some words
    Parameters
    ----------
    sentence: str
        Sentence where word is to be found 
    word: str
        Word to be highlighted in the sentence
    Returs
    ----------
    sentence: str
        New sentence string with highlighted format
    '''
    regex = re.compile(re.escape(word), re.IGNORECASE)
    sentence = regex.sub("<b>" + word + "</b>", sentence)
    sentence = sentence.replace('\n', '<br>')
    #sentence = sentence.replace(word, "<b>" + word + "</b>")
    return sentence


def df_html(df):
    '''Generates a HTML file with a table from dataframe
    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame with words and count columns with html markup in the strings objects  
    Returs
    ----------
    df_html: str
        String in HTML markup format
    '''
    base_html = """
    <!doctype html>
    <html>
        <head>
            <meta http-equiv="Content-type" content="text/html; charset=utf-8">
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.css">
            <script type="text/javascript" src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.js"></script>
        </head>
        <body>
            %s
            <script type="text/javascript">
                $(document).ready(function(){$('table').DataTable({"pageLength": 5});});
            </script>
        </body>
    </html>
    """
    df_html = df.to_html()
    
    return base_html % df_html


def df_window(df, filename):       
    '''Generates and displays a html from a dataframe 
    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame with report of words found in file 
    '''
    with open(filename, encoding="utf8", mode='w+') as f:
        html_text = df_html(df)
        #print(html_text)
        html_text = html_text.replace('&lt;','<')
        html_text = html_text.replace('&gt;','>')
        html_text = html_text.replace('"', r'"')
        html_text = html_text.replace("'", r"'")
        html_text = html_text.replace("`", r"`")
        f.write(html_text)
    webbrowser.open(f.name)
    

def words_for_cloud(df):
    '''Generates text for wordcloud library
    Parameters
    ----------
    df: pandas.DataFrame
        DataFrame with words and count columns   
    Returs
    ----------
    text: str
        Text for wordcloud processor
    '''
    w = df.index.tolist()
    wc = df['count'].tolist()
    text = ''
    for i in range(len(w)):
        text = text + ' '.join(wc[i]*[w[i]])+ ' '
    return text