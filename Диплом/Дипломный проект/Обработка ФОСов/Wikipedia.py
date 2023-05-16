import wikipedia
import re
import random
from NLP.summarization import summarization

class Wiki:
    def __init__(self):
        pass

    def __clear_wiki(self, result):
        raw_article = result[:str.find('== См. также ==', result)]
        raw_article = re.sub(r'===.*===', '', raw_article)
        raw_article = re.sub(r'==.*==', '', raw_article)
        raw_article = raw_article.replace('\n', '')
        raw_article = raw_article.replace('\r', '')
        raw_article = re.sub(r'{.*}', '', raw_article)
        raw_article = re.sub(r'\s{3,}.*\s{3,}', '', raw_article)
        raw_article = re.sub(r'~', '', raw_article)
        article = raw_article.strip()[:-1500]
        article = article[:article.rfind('.') + 1]
        return article

    def expand_pool_articles(self, name):
        result = self.__try_find_article(name)
        if result is not None:
            try:
                links = result.links
                return random.SystemRandom().sample(links, int(0.1 * len(links)))
            except:
                return []
        return []

    def get_wiki_articles(self, name):
        result = self.__try_find_article(name)
        if result is not None:
            data_article = self.__clear_wiki(result.content)
            return data_article, summarization(data_article)
        return ''
    
    def __try_find_article(self, name):
        wikipedia.set_lang('ru')
        try:
            return wikipedia.page(name, auto_suggest=True, preload=True)
        except wikipedia.DisambiguationError as e:
            try:
                select = e.options[1]
                return wikipedia.page(select)
            except:
                return None
        except wikipedia.PageError:
            return None
        except:
            return None