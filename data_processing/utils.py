import sys
# setting path
sys.path.append('../StereoKG')

import os
import html
import re
import preprocessor as tp
import nltk
from nltk.tokenize import TweetTokenizer
from pathlib import Path

from Credentials import *
from data_processing.StatementMaker import StatementMaker
statement_maker = StatementMaker(use_cache=False)

question_words = ["what", "why", "how", "who", "where", "which", "whom", "when", "whose"]

def make_statement(sentence, subject):
    """
    Convert an interrogative sentence into a statement if possible, else leave it
    as it is.
    """
    ques_true=False
    for word in question_words:
        if sentence.lower().startswith(word):
            ques_true=True
            break

    if "?" in sentence or ques_true:
        stmt = statement_maker.to_statement(sentence, subject)
        if stmt == "":
            stmt = sentence
    else:
        stmt = sentence
    
    return stmt


def preprocess_reddit(data):
    """Preprocess text scraped from Reddit"""
    def remove_punctuation(text):
        words = text.split(" ")
        new_words = []
        for word in words:
            new_word = re.sub('[^A-Za-z0-9?]+', '', word)
            if new_word != '':
                new_words.append(new_word)
        return new_words

    t_sentences = []

    data = html.unescape(tp.clean(data))
    data = data.replace("!", "! ")
    data = data.replace("?", "? ")
    data = data.replace(".", ". ")
    sentences = nltk.sent_tokenize(data)

    for sentence in sentences:
        sentence = ' '.join(remove_punctuation(sentence))
        t_sentences.append(sentence)

    return t_sentences


def process_tweet(data):
    def remove_punctuation(text):
        words = [w for w in w_tokenizer.tokenize(text)]
        new_words = []
        for word in words:
            new_word = re.sub(r'[^\w\s?]', '', (word))
            if new_word != '':
                new_words.append(new_word)
        return new_words

    t_sentences = []

    data = html.unescape(tp.clean(data))
    data = data.replace("!", "! ")
    data = data.replace("?", "? ")
    data = data.replace(".", ". ")
    sentences = nltk.sent_tokenize(data)

    for sentence in sentences:
        w_tokenizer = TweetTokenizer()
        sentence = ' '.join(remove_punctuation(sentence))
        t_sentences.append(sentence)

    return t_sentences


def file_scraped_data_reddit(obj, maindir, query, fname):
    """
    Creates a file in the respective Subject directory for the query
    e.g. French men_Why do French men
    """
    path = scrapedir +"/" + maindir + "/" + query.replace(" ", "_").replace('"','')
    Path(path).mkdir(parents=True, exist_ok=True)
    fname = path + "/"+ fname + ".txt"
    f = open(fname, "w")
    f.write(obj.toJSON())
    f.close()


def file_scraped_data_twitter(obj, parent, fname):
    path = scrapedir + "/" + parent
    Path(path).mkdir(parents=True, exist_ok=True)
    fname = path + "/" + fname + ".csv"
    obj.to_csv(fname, index=False)


def add_to_file(sentence, subject, name):
    """Append sentence to file"""
    path = sentencedir + "/" + name + ".txt"

    if os.path.exists(path):
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not

    sentence = sentence.lower()
    sentence = make_statement(sentence, subject).lower() #Check if this is necessary

    f = open(path, append_write)
    f.write(sentence + "\n")
    f.close()