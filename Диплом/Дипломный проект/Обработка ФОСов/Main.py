from FOS import FOS
from Wikipedia import Wiki
from JSON import JSON
from InternetParser import QuestionToArticle
import pathlib
import os
from pathlib import Path
import chime
from tqdm import tqdm

class Main():
    def __init__(self):
        self.main_directory_path = Path(pathlib.Path.cwd(), 'Диплом', 'Дипломный проект', 'ФОСы')
        self.index_path = Path(pathlib.Path.cwd(), 'Диплом', 'Дипломный проект', 'Обработка ФОСов', 'index.txt')
        self.question_to_current_file = []
        self.articles_contents = []
        self.articles_summary = []

    def __process_files(self, file):
        question_to_current_file = self.__get_current_file_questions(file, 2)
        chime.success()
        if question_to_current_file is None:
            self.question_to_current_file, self.articles_contents = None, None
        else:
            self.__split_questions(question_to_current_file)
            articles_contents, articles_summary = self.__get_wiki_articles(self.question_to_current_file, file)
            chime.success()
            self.question_to_current_file, self.articles_contents, self.articles_summary = question_to_current_file, articles_contents, articles_summary

    def __save_index(self):
        index = open(self.index_path, 'r')
        index_str = int(index.read())
        index.close()
        index = open(self.index_path, 'w')
        index.write(str(index_str + 1))
        index.close()

    def __split_questions(self, questions):
        split_questions = []
        clean_split_questions = []
        for question in questions:
            split_questions += [clean_questions.strip() for clean_questions in question.split('.')]
        for split_question in split_questions:
            if split_question != '':
                clean_split_questions.append(split_question)
        self.question_to_current_file = clean_split_questions

    def __get_current_file_questions(self, file, number_questions = -1):
        path_file = Path(self.main_directory_path, file)
        questions = FOS(path_file).parse()
        if len(questions) == 0:
            return None
        else:
            return questions[:number_questions]

    def __get_wiki_articles(self, question_to_current_file, file_name):
        wiki, articles = Wiki(), QuestionToArticle(question_to_current_file, file_name).find_articles()
        chime.success()
        articles_contents, articles_summary = self.__get_article_content(articles, wiki)
        return articles_contents, articles_summary

    def __get_article_content(self, articles, wiki):
        articles_contents, articles_summary = [], []
        for i in tqdm(range(len(articles)), desc='   - (Extract information) -   '):
            articles_contents.append([])
            articles_summary.append([])
            for article in articles[i]:
                results = wiki.get_wiki_articles(article)
                articles_contents[i].append(results[0])
                articles_summary[i].append(results[1])
        chime.success()
        return articles_contents, articles_summary

    def start_build_JSON(self):
        index = open(self.index_path, 'r')
        listdir = os.listdir(self.main_directory_path)[int(index.read()):]
        index.close()

        for i in range(len(listdir)):
            self.__process_files(listdir[i])
            index_files = open(self.index_path, 'r')
            index = int(index_files.read())
            index_files.close()

            if self.question_to_current_file is not None:
                JSON(listdir[i], self.question_to_current_file, self.articles_contents, self.articles_summary, index).create_json()
            self.__save_index()
            chime.success()

if __name__ == "__main__":
    Main().start_build_JSON()