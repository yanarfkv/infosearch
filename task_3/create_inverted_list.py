import re
import os
from collections import defaultdict


# Загружает леммы и соответствующие им токены из файла
def load_lemmas(filepath):
    lemmas = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(' ')
            lemma, tokens = parts[0], parts[1:]
            lemmas[lemma] = tokens
    return lemmas  # Возврат словаря с леммами и токенами


# Построение инвертированного индекса на основе страниц и лемм
def build_inverted_index(pages_path, lemmas):
    inverted_index = defaultdict(set)
    pages_path_full = os.path.join(pages_path, 'pages')

    for page_file in os.listdir(pages_path_full):
        page_id = int(re.findall(r'\d+', page_file)[0])  # Извлечение ID страницы из имени файла

        with open(os.path.join(pages_path_full, page_file), 'r', encoding='utf-8') as file:
            text = file.read().lower()

        words_on_page = set(re.findall(r'\b[а-яА-ЯёЁ]+\b', text))  # Извлечение слов из текста

        for word in words_on_page:  # Перебор слов на странице
            for lemma, tokens in lemmas.items():  # Перебор лемм и токенов
                if word in tokens:  # Если слово соответствует токену леммы
                    inverted_index[lemma].add(page_id)  # Добавление ID страницы к лемме
                    break

    for lemma in inverted_index:  # Конвертация множеств в списки для сохранения
        inverted_index[lemma] = list(inverted_index[lemma])

    return inverted_index  # Возврат построенного инвертированного индекса


lemmas = load_lemmas('../task_2/lemmas.txt')
inverted_index = build_inverted_index('../task_1', lemmas)

with open('inverted_index.txt', 'w', encoding='utf-8') as file:
    for lemma, page_ids in inverted_index.items():
        file.write(f"{lemma} {' '.join(map(str, page_ids))}\n")
