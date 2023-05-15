"""
In this code, we collect the results of coreference-resolution 
and semantic-role-labeling for each sentence.

PS: we will enlarge the evidence of each sample by add sentence(s) 
to it in case that there are no sentences covering some import part
of the question in the existed evidence.
"""

import sys
from tqdm import tqdm

import json
import codecs

import nltk
from nltk.corpus import stopwords

class Merge:
    json_load = lambda self, x: json.load(codecs.open(x, 'r', encoding='utf-8'))
    json_dump = lambda self, d, p: json.dump(d, codecs.open(p, 'w', 'utf-8'), indent=2, ensure_ascii=False)
    verb_pos = ['VBZ', 'VBN', 'VBD', 'VBP', 'VB', 'VBG', 'IN', 'TO', 'PP']
    noun_pos = ['NN', 'NNP', 'NNS', 'NNPS']
    other_pos = ['JJ', 'FW', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']

    def __init__(self, path):
        self.path = path

    def __add_corpus(self, question, evidence, crf, dep):
        stopwords_eng = stopwords.words('english')

        question = question[:-1].strip().split()
        pos_tags = nltk.pos_tag(question)

        evidences = [word.lower() for evd in evidence for word in evd['coreference']]
        coref_list = [' '.join(evd['coreference']) for evd in evidence]
        titles = [evd['title'] for evd in evidence]

        for word, pos in zip(question, pos_tags):
            ## requirements: noun-type word; not short; upper case; not stop-word
            if pos[1] in self.noun_pos and len(word) >= 3 and not word.islower() and word.lower() not in stopwords_eng:
                if word.lower() not in evidences and all([w.count(word.lower()) == 0 for w in evidences]):
                    for title in titles:
                        flags = [word in sent for sent in crf[title]]
                        if any(flags):
                            ## found a sentence to add into the evidence
                            index = flags.index(True)
                            addlist = crf[title][index]
                            if ' '.join(addlist) not in coref_list:
                                coref_list.append(' '.join(addlist))
                                evidences += [w.lower() for w in addlist]
                                evidence.append({'text': coref_list[-1], 'dependency_parse': dep[title][index], 
                                                'coreference': addlist, 'title': title})
                            break
                        
        return evidence


    def __merge(self, raw, dep, crf):
        corpus = []
        for sample in tqdm(raw, desc='  - (MERGING) -  '):
            question, answer = sample['question'], sample['answer']
            evidence_index, evidence_sent = [evd['index'] for evd in sample['evidence']], [evd['text'] for evd in sample['evidence']]
            
            evidence, cnt = [], 0
            for index, sent in zip(evidence_index, evidence_sent):
                for i in range(index[1][0], index[1][1]):
                    dependency = dep[index[0]][i]
                    dependency = [] if dependency is None else dependency
                    coref = crf[index[0]][i]
                    evidence.append({'text':sent, 'dependency_parse':dependency, 'coreference':coref, 'title':index[0]})
                    cnt += 1
            
            sample = {'question':question, 'answer':answer, 'evidence':evidence}
            sample['evidence'] = self.__add_corpus(question, evidence, crf, dep)   ## enlarge the evidence if needed
            
            corpus.append(sample)

        return corpus


    def merge(self):
        #data.json dp.json crf_rsltn.json merged_data.json
        raw = self.json_load(self.path + 'data.json')
        crf = self.json_load(self.path + 'crf_rsltn.json')
        dep = self.json_load(self.path + 'dp.json')
        ##=== merge files ===###
        data = self.__merge(raw, dep, crf)
        ##=== dump file ===###
        self.json_dump(data, self.path + 'merged_data.json')