import re
import json
import codecs
import pandas as pd

class JSON:
    def __init__(self, file_name, questions, articles, summary, index):
        self.json_dump = lambda d, p: json.dump(d, codecs.open(p, 'w', 'utf-8'), indent=2, ensure_ascii=False)
        self.file_name = file_name
        self.questions = questions
        self.articles = articles
        self.summary = summary
        self.name = ''
        self.index = index
        self.jsons = []

    def create_json(self):
        self.__get_name()
        for questions, articles, summary in zip(self.questions, self.articles, self.summary):
            new_json = {}
            evidence = [{'text':articles, 'index':[self.name, [0, 1]]}]
            context = {'questions':articles}
            new_json = {'question': questions, 'answer': summary, 'evidence': evidence, 'context': context}
            self.jsons.append(new_json)
        self.json_dump(self.jsons, r'my_dataset/' + self.name + str(self.index) + '.json')

    def __get_name(self):
        name_fos = re.sub(r'\d', '', self.file_name)
        name_fos = re.search(r'[^.]{5,}', name_fos)[0].strip()
        self.name = name_fos