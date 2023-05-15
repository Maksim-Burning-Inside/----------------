from tqdm import tqdm
import json
import codecs

class CreateEviedenceData():
    def __init__(self, path):
        self.path = path
        self.json_load = lambda self, file_name: json.load(codecs.open(file_name, 'r', encoding='utf-8'))
        self.json_dump = lambda self, data, file_path: json.dump(data, codecs.open(file_path, 'w', 'utf-8'), indent=2, ensure_ascii=False)


    def __add_evidence(self, key, dictionary, evidence, evidence_index, context):
        #если найден поддерживащий факт
        if key[0] in dictionary:
            #пробуй добавить соответсвующие данные в проверенные данные
            try:
                evidence.append([dictionary[key[0]][key[1]]])
                evidence_index.append([key[0], (key[1], key[1] + 1)])
            except:
                #иначе ошибка, добавляются изменённые данные
                print("ERROR 1")
                evidence.append(dictionary[key[0]])
                evidence_index.append([key[0], (0, len(dictionary[key[0]]))])
            #сохраняем текст
            context[key[0]] = dictionary[key[0]]
        else:
            print("ERROR 2")
            #пытаемся ещё раз найти этот факт
            flags = [k.count(key[0]) for k in dictionary]
            #если нашли что-то
            if any(flags):
                #вытягиваем оп индексу
                index = flags.index(True)
                key[0] = list(dictionary.keys())
                key[0] = key[0][index]
                try:
                    #добавляем найденные данные
                    evidence.append([dictionary[key[0]][key[1]]])
                    evidence_index.append([key[0], (key[1], key[1] + 1)])
                except:
                    #иначе ошибка
                    print("ERROR 4")
                    evidence.append(dictionary[key[0]])
                    evidence_index.append([key[0], (0, len(dictionary[key[0]]))])
                context[key[0]] = dictionary[key[0]]
            else:
                #совсем ничего не нашли, пропускаем
                print("ERROR 3")
                return False
        return True


    def __extract(self, data):
        #вытягиваем из джейсона данные, по умолчанию sample содержит блоки из вопроса+ответа+контекста+вспомогательныъ фактов
        #контекст имеет структуру элемент массива (тема str) + элемента массива массив фактов ([str])
        paragraphs = [sample['context'] for sample in data]
        #форминруем словарь из пар тема:факты о теме
        paragraphs = {c[0]:c[1] for sample in paragraphs for c in sample}

        corpus = []
        #tqdm - отображает процентаж обработки информации, с каждым пройденным элементом цикла процент будет расти
        for sample in tqdm(data, desc='   - (Extract information) -   '):
            #строим конструкцию аналогичную paragraphs
            context = {c[0]:c[1] for c in sample['context']}
            #вытягиваем вспомогательные факты
            supporting_facts = sample['supporting_facts']
            #вытягиваем ответы
            answer = sample['answer']
            #вытягиваем вопросы
            question = sample['question']

            #создаем массивы доказательств корректности данных(вспомогательная информация указывает на существующийо ответ)
            evidence, evidence_index = [], []
            #словарь проверенных пар тема+контекст
            ctxt = {}

            #перебираем вспомогательные факты, которые указывают на правильные ответы(имя ответа, номер ответа)
            for sf in supporting_facts:
                #если все корректно, заполняем массивы, пробуем дважды, add_evidence возвращает False, если ничего не нашла
                if not self.__add_evidence(sf, context, evidence, evidence_index, ctxt):
                    self.__add_evidence(sf, paragraphs, evidence, evidence_index, ctxt)

            #если корректных фактов более нуля, то
            if len(evidence) > 0:
                #словарь evidence с фактами и их местонахождением среди всех текстов
                evidence = [{'text':evd, 'index':idx} for evd, idx in zip(evidence, evidence_index)]
                #словарь sample с вопросами, ответами, проверенными фактами и их контекстами
                sample = {'question':question, 'answer': answer, 'evidence':evidence, 'context':ctxt}
                #возварщаем очищенный словарь
                corpus.append(sample)

        return corpus


    def __overlap(self, corpus):
        #делим данные на тренировочные и тестовые
        train, valid = [], []
        #выделяем массивы под вопросы и ресурсы к вопросам
        questions, sources = [], []
        #снова перебираем массив с загрузкой
        for sample in tqdm(corpus['train'], desc='   - (Deal with overlapping) -   '):
            #собираем уникальные вопросы
            if sample['question'] not in questions:
                questions.append(sample['question'])
                train.append(sample)
                try:
                    #добавляем текст в массив с ресурсами
                    sources.append('\t'.join(['\t'.join(sent['text']) for sent in sample['evidence']]))
                except:
                    #в случае сбоя остановиться процесс работы, чтобы рповерить ошибки
                    import ipdb; ipdb.set_trace()
        for sample in tqdm(corpus['valid'], desc='   - (Deal with overlapping) -   '):
            #пробегаем проверенные части по тестовым данным
            tmp = '\t'.join(['\t'.join(sent['text']) for sent in sample['evidence']])
            if tmp not in sources:
                valid.append(sample)
        #печатаем размеры выборок и возвращаем готовые словари
        print(len(train), len(valid))
        return {'train':train, 'valid':valid}


    def __process(self, train, valid):
        #создаем словарь с проверенными данными для train и valid
        corpus = {'train':self.__extract(train), 'valid':self.__extract(valid)}
        #сборка проверенных данных, чистка дубликатов
        corpus = self.__overlap(corpus)
        return corpus

    def create_clean_data(self):
        #подгружаем датасеты
        train = self.json_load(self.path + 'train.json')
        valid = self.json_load(self.path + 'valid.json')
        #запускаем процесс
        corpus = self.__process(train, valid)
        #получили словари corpus которые содержат вопрос, информацию о наличии контекста из всех источников(их может быть более 1), индексы, контекст. Сохраняем
        self.json_dump(corpus['train'], self.path + 'data.train.json')
        self.json_dump(corpus['valid'], self.path + 'data.valid.json')