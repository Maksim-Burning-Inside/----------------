from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from NLP.NLP import NLP
from NLP.PN import clean_sent_with_possessive_pronouns
import re

class QuestionToArticle:
    def __init__(self, questions, file_name):
        self.nlp = NLP()
        self.questions = self.__prepare_questions(questions)
        self.file_name = file_name

    def find_articles(self):
        articles = []
        for questions in self.questions:
            current_articles = []
            for request in questions:
                current_articles.append(self.__find_on_request(request))
            articles.append(current_articles)
        return articles

    def __get_name(self):
        name_fos = re.sub(r'\d', '', self.file_name)
        name_fos = re.search(r'[^.]{5,}', name_fos)[0].strip()
        return name_fos

    def __find_on_request(self, request, number_articles = 1):
        results = []
        while True:
            try:
                driver = webdriver.Chrome()
                search_term = self.__get_name() + ' ' + request + ' \"википедия\"'
                url = f'https://duckduckgo.com/html/?q={search_term}&kl=ru-ru'
                driver.get(url)
                driver.minimize_window()
                wait = WebDriverWait(driver, 10)
                results = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//h2[@class="result__title"]/a')))
                break
            except:
                driver.quit()

        articles = []
        for result in results:
            header = result.text
            if header.find(' — Википедия') >= 0:
                articles.append(header[0:header.find(' — Википедия')])

        driver.quit()
        return articles[0:number_articles]

    def __prepare_questions(self, questions):
        new_questions = []
        for question in questions:
            clean_question = clean_sent_with_possessive_pronouns(question)
            new_questions.append(self.nlp.sent_tokenize(clean_question))
        return new_questions