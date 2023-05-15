from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def summarization(article, SENTENCES_COUNT = 5):
    parser = PlaintextParser.from_string(article, Tokenizer("russian"))
    stemmer = Stemmer("russian")

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words("russian")

    text = ''
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        text += sentence._text
    
    return text