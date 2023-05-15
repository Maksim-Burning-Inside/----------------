from NLP.NLP import NLP
import re

def clean_sent_with_possessive_pronouns(text):
    possessive_pronouns = ['мой', 'твой', 'его', 'её', 'наш', 'ваш', 'их']

    nlp = NLP()
    sent_text = nlp.sent_tokenize(text)

    word_text = []
    for sent in sent_text:
        tokens = nlp.word_tokenize(sent)
        lemmatization_tokens = nlp.lemmatization(tokens)
        word_text.append(lemmatization_tokens)

    sent_text_without_possessive_pronouns = []
    for i in range(len(sent_text)):
        for word in word_text[i]:
            if word in possessive_pronouns:
                break
            elif re.fullmatch(r'\W', word):
                sent_text_without_possessive_pronouns.append(sent_text[i])
                break
        else:
            sent_text_without_possessive_pronouns.append(sent_text[i])
    text_without_possessive_pronouns = " ".join(sent_text_without_possessive_pronouns)

    return text_without_possessive_pronouns