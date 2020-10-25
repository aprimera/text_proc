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


def file_reader(file):
    ''' Provide the location of the ascii file
        The function returns the full text
    '''
    with open(file, 'r', encoding="utf8") as f:
        text = f.read()
    return text


def text_processor(text, add_stop_words=[], stemming=False, lemmatising=False):
    '''
    
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
    df = pd.DataFrame()
    word_count = []
    sentences_report = []
    files_list = []
    for word in set_words:
        all_sentences = ''
        all_files = ''
        for i, sentence in enumerate(sentences):
            if word in sentence.lower():
                all_sentences = all_sentences + sentence + '\n\n' 
                if files[i] not in all_files:
                    all_files = all_files + files[i] + ', '
        word_count.append(words.count(word))
        sentences_report.append(sentence_highlighter(all_sentences, word))  
        #sentences_report.append(all_sentences) 
        files_list.append(all_files)
    df['words'] = set_words
    df['count'] = word_count
    df['files'] = files_list
    df['sentences'] = sentences_report
    df.reset_index(drop=True, inplace=True)
    df.sort_values('count', ascending=False, inplace=True)
    return df


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

    
def sentence_highlighter(sentence, word):
    sentence = sentence.replace('\n', '<br>')
    #sentence = sentence.replace('\', '')
    sentence = sentence.replace(word, "<b>" + word + "</b>")
    #sentence = sentence.replace(word, color.BOLD + color.UNDERLINE + word + color.END)
    return sentence


def df_html(df):
    base_html = """
    <!doctype html>
    <html>
        <head>
            <meta http-equiv="Content-type" content="text/html; charset=utf-8">
            <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.16/css/jquery.dataTables.css">
            <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.js"></script>
        </head>
        <body>
            %s<script type="text/javascript">
                $(document).ready(function(){$('table').DataTable({"pageLength": 5});});
            </script>
        </body>
    </html>
    """
    df_html = df.to_html()
    return base_html % df_html


def df_window(df):
    with NamedTemporaryFile(delete=False, suffix='.html', mode='w+') as f:
        f.write(df_html(df))
    webbrowser.open(f.name)
    

def words_for_cloud(df):
    w = df['words'].tolist()
    wc = df['count'].tolist()
    text = ''
    for i in range(len(w)):
        text = text + ' '.join(wc[i]*[w[i]])+ ' '
    return text