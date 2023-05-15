import nltk
import json
import pymorphy2
from nltk.tokenize import sent_tokenize, word_tokenize
import pathlib
from pathlib import Path
import re

class NLP:
    def __init__(self) -> None:
        pass

    def prepare_step(self):
        nltk.download('stopwords')
        nltk.download('punkt')

    def save_stop_words(self):
        path = Path(pathlib.Path.cwd(), 'NLP', 'stop_words.txt')
        from nltk.corpus import stopwords
        stop_words = stopwords.words("russian")
        with open(path, 'w') as stop:
            json.dump(stop_words, stop)

    def __get_stop_words(self):
        path = Path(pathlib.Path.cwd(), 'NLP', 'stop_words.txt')
        with open(path, 'r') as stop:
            return json.load(stop)

    def word_tokenize(self, text):
        return word_tokenize(text, language="russian")

    def sent_tokenize(self, text):
        return sent_tokenize(text, language="russian")

    def lemmatization(self, tokenize):
        morph = pymorphy2.MorphAnalyzer()
        norm_tokenize = []
        for token in tokenize:
            if token.lower() == 'его':
                norm_tokenize.append('его')
            elif token.lower() == 'их':
                norm_tokenize.append('их')
            else:
                norm_tokenize.append(morph.parse(token)[0].normal_form)
        return norm_tokenize

    def clean_words(self, tokenize):
        stop_words = self.__get_stop_words()
        clean_tokenize = []
        for token in tokenize:
            if token not in stop_words:
                clean_tokenize.append(token)
        return clean_tokenize

    def clean_punctuation(self, tokenize):
        clean_tokenize = []
        for token in tokenize:
            if re.fullmatch(r'\W', token):
                pass
            else:
                clean_tokenize.append(token)
        return clean_tokenize



if __name__ == "__main__":
    NLP().prepare_step()
    NLP().save_stop_words()