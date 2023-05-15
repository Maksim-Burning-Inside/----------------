import codecs
import json
from tqdm import tqdm
from allennlp.predictors.predictor import Predictor
from nltk import word_tokenize

class DependenciesСoreferences():
    json_load = lambda self, x: json.load(codecs.open(x, 'r', encoding='utf-8'))
    json_dump = lambda self, d, p: json.dump(d, codecs.open(p, 'w', 'utf-8'), indent=2, ensure_ascii=False)

    def __init__(self, data_path):
        self.data_path = data_path

    def __get_context(self, data):
        context = {}
        #отображение прогресса
        for sample in tqdm(data):
            #для пар тема конектса+контекст создаём словарь
            for k, v in sample['context'].items():
                context[k] = v
        return context

    ''' POS-расшифровка
    ADJ: прилагательное
    ADP: добавочные элементы(приставки, 's и т.д.)
    ADV: наречие
    AUX: вспомогательный элемент
    CCONJ: сочинительный союз
    DET: определитель
    INTJ: междометие
    NOUN: существительно
    NUM: число
    PART: частица
    PRON: метсоимение
    PROPN: имя собсвтенное
    PUNCT: пунктуация
    SCONJ: подчинительный союз
    SYM: символ
    VERB: глагол
    X: другое
    '''

    ''' predicted_dependencies расшифровка
    acomp: прилагательное-комплимент
    amod: прилагательное-определение
    aux: вспомогательный глагол
    compound: часть составного слова
    det: определитель
    dobj: дополнение
    nsubj: подлежащее
    pobj: предложное предложение
    ROOT: корневой элемент
    '''
    def __get_dependency(self, sent, dependency_parser):
        #если пустое предложение ничего не делаем
        if len(sent.strip()) == 0:
            return None
        try:
            #пробуем с поомщью модели разобрать предложение
            sent = dependency_parser.predict(sentence=sent)
        except:
            #обрабатываем искючение
            import ipdb; ipdb.set_trace()
        #вычленяем из модеи информацию о словах, их частях речи, их близости к корню предложения, их зависимости
        words, pos, heads, dependencies = sent['words'], sent['pos'], sent['predicted_heads'], sent['predicted_dependencies']
        #формируем соответсвующий словарь и возвращаем его
        result = [{'word':w, 'pos':p, 'head':h - 1, 'dep':d} for w, p, h, d in zip(words, pos, heads, dependencies)]
        return result


    def __dependency_parse(self, raw, filename):
        #скачиваем предобученный предиктор для очистки данных и создания связей между словами
        dependency_parser = Predictor.from_path('used models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz')
        #создаём словарь название темы+массив парсированных предложений
        context = {
            key: [
                self.__get_dependency(sent, dependency_parser) for sent in value
            ] for key, value in tqdm(raw.items(), desc='   - (Dependency Parsing: 1st) -   ')
        }
        #сохраняем результат
        self.json_dump(context, filename)


    def __get_coreference(self, doc, coref_reslt, pronouns, title):
        #функция вычленения кластеров
        def get_crf(span, words):
            #собираем фразы
            phrase = []
            for i in range(span[0], span[1] + 1):
                #фраза состоит из индексов слов, объеденённых в кластеры моделью
                phrase += [words[i]]
            #возвращаем объект с кластером и индексами его начала и конца
            return (' '.join(phrase), span[0], span[1] - span[0] + 1)
        #функция выделения лучшего кластера
        def get_best(crf):
            #сортируем кластеры по индексам конца кластеров
            crf.sort(key=lambda x: x[2], reverse=True)
            #если конец первого кластера это первое слово
            if crf[0][2] == 1:
                #сортируем по длине класетров
                crf.sort(key=lambda x: len(x[0]), reverse=True)
            #рассматриваем каждые кластеры
            for w in crf:
                #если кластер не содержит местоимения и  не является концом строки, то возвращаем его
                if w[0].lower() not in pronouns and w[0].lower() != '\t':
                    return w[0]
            return None

        #предсказываем с помощью модели задачу кореферентности
        doc = coref_reslt.predict(document=doc)
        #собираем слова
        words = [w.strip(' ') for w in doc['document']]
        #собираем кластеры слов
        clusters = doc['clusters']
        #рассматриваем каждую группу
        for group in clusters:
            #создаём кластеры для каждой подгруппы группы, избавляемся от кластеров местоимений и конца строки, коротких кластеров, выбираем лучший
            crf = [get_crf(span, words) for span in group]
            entity = get_best(crf)
            #если кластер пуст
            if entity in ['\t', None]:
                #заполняем его названием темы
                try:
                    entity = coref_reslt.predict(document=title)
                    entity = ' '.join(entity['document'])
                #в любом случае
                except:
                    entity = ' '.join(word_tokenize(title))
            #иначе
            if entity not in ['\t', None]:
                for phrase in crf:
                    #для каждой фоазы, если она содержит местоимения, сохраняем индекс и первое слово кластера
                    if phrase[0].lower() in pronouns:
                        index = phrase[1]
                        words[index] = entity
        #собираем предложения и документ
        doc, sent = [], []
        for word in words:
            if word.strip(' ') == '\t':
                doc.append(sent)
                sent = []
            #если это не простое окончание строки
            else:
                if word.count('\t'):
                    print(word)
                    word = word.strip('\t')
                sent.append(word)
        doc.append(sent)
        return doc


    def __coreference_resolution(self, raw, filename):
        #сохраняем местоимения
        pronouns = ['it', 'its', 'he', 'him', 'his', 'she', 'her', 'they', 'their', 'them']
        #создаем словарь из джейсон файла
        raw = {k: '\t'.join(v) for k,v in raw.items()}
        #подключаем модель для решения задачи кореферентности
        coref_reslt = Predictor.from_path('used models/coref-spanbert-large-2020.02.27.tar.gz')
        #создаём словарь
        context = {
            key: self.__get_coreference(value, coref_reslt, pronouns, key) for key, value in tqdm(raw.items(), desc='  - (crf for evidence) ')
        }
        #сохраняем результат как джейсон файл
        self.json_dump(context, filename)


    def __get_ner(doc, ner_tagger):
        #
        try:
            doc = ner_tagger.predict(sentence=doc)
        except:
            return [[doc, 'O']]
        #
        words, tags = doc['words'], doc['tags']
        return [[w, t] for w, t in zip(words, tags)]


    def __ner_tag(self, raw, filename):
        #
        ner_tagger = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz")
        raw = [[d[0], d[0]] for d in raw]    #raw = [[d[0], '\t'.join(d[1])] for d in raw]
        #
        context = {sample[0]: self.__get_ner(sample[1], ner_tagger) for sample in tqdm(raw, desc='  - (ner for evidence) ')}
        self.json_dump(context, filename)


    def __sr_labeling(sent, sr_labeler):
        #
        if len(sent.strip()) == 0:
            return None
        try:
            sent = sr_labeler.predict(sentence=sent)
        except:
            import ipdb; ipdb.set_trace()
        #
        words, verbs = sent['words'], sent['verbs']
        tags = [verb['tags'] for verb in verbs]
        return {'words':words, 'tags':tags}


    def __semantic_role_labeling(self, raw, filename):
        #
        sr_labeler = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")
        context = {sample[0]: [self.__sr_labeling(sent, sr_labeler) for sent in sample[1]] for sample in tqdm(raw, desc='   - (Semantic Role Labeling: 1st) -   ')}
        self.json_dump(context, filename)


    def build(self):
        train_data_file, valid_data_file = self.data_path + 'data.train.json', self.data_path + 'data.valid.json'
        #подгружаем полную базу
        data = self.json_load(train_data_file) + self.json_load(valid_data_file)
        self.json_dump(data, self.data_path + 'data.json')
        #распаковываем контекст, переменная контекста теперь содержит блоки {тема:весь контекст к теме}
        context = self.__get_context(data)
        #считаем, сколько элементов контекста имеем
        print('number of context:', len(context))

        #запускаем синтаксический анализ всех предложений, результат записываем в dp.json
        self.__dependency_parse(context, self.data_path + 'dp.json')
        #Разрешение кореферентности — это задача поиска всех выражений, которые относятся к одному и тому же объекту в тексте.
        self.__coreference_resolution(context, self.data_path + 'crf_rsltn.json')

        #пока неиспользованная алтернатива
        #ner_tag(context, data_path + 'dp.json')
        #пока неиспользованная алтернатива
        #semantic_role_labeling(context, data_path + 'dp.json')