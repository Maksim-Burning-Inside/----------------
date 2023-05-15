import re
import docx

class FOS():
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.raw_questions = []

    def parse(self):
        self.__get_raw_questions(self.path_to_file)
        if len(self.raw_questions) == 0:
            return []

        self.__clear_empty_blocks()
        self.__clear_other()
        self.raw_questions = sorted(self.raw_questions)
        self.__clear_empty_elements()

        questions = []
        for i in range(len(self.raw_questions)):
            questions.append(re.sub(r'.*\d{1,3}[.]', '', self.raw_questions[i]).lower().strip())
        return questions

    def __get_raw_questions(self, path_files):
        document = docx.Document(path_files)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]

        for i in range(len(paragraphs) - 1, 0, -1):
            if paragraphs[i].lower().find('блок d') >= 0:
                paragraphs = paragraphs[i:]
                break

        for i in range(len(paragraphs)):
            end = self.__find_end(paragraphs[i].lower())
            if end:
                self.raw_questions = paragraphs[:i]
                break

    def __find_end(self, text):
        variants = ['описание показателей', 'критерии оценивания', 'состав билета', 'таблица']
        for end_variant in variants:
            if text.find(end_variant) >= 0:
                return True
        return False
    
    def __clear_empty_blocks(self):
        raw_questions = self.raw_questions
        for i in range(len(raw_questions)):
            try:
                if raw_questions[i] == '':
                    if raw_questions[i + 1] == '':
                        raw_questions = raw_questions[:i]
                        break
            except:
                break
        self.raw_questions = raw_questions

    def __clear_other(self):
        raw_questions = self.raw_questions[1:]
        for i in range(len(raw_questions)):
            if (raw_questions[i].lower()).find('список вопросов') >= 0:
                raw_questions[i] = ''
        self.raw_questions = raw_questions

    def __clear_empty_elements(self):
        raw_questions = self.raw_questions
        for i in range(len(raw_questions)):
            if raw_questions[i] != '':
                raw_questions = raw_questions[i:]
                break
        self.raw_questions = raw_questions