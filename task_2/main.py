from bs4 import BeautifulSoup
import pymorphy2
import re
import os
from nltk.corpus import stopwords
import nltk

# Загрузка списка стоп-слов для русского языка
nltk.download('stopwords')
russian_stopwords = stopwords.words('russian')

# Инициализация анализатора
morph = pymorphy2.MorphAnalyzer()


# Функция для очистки и лемматизации текста
def process_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')
        text = soup.get_text()
    # Токенизация текста с исключением слов, содержащих не только буквы
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b', text)
    # Очистка списка слов от стоп-слов и неалфавитных символов
    cleaned_words = [word.lower() for word in words if word.lower() not in russian_stopwords]
    lemmas = {}  # Словарь для хранения лемм и соответствующих им слов
    for word in cleaned_words:
        lemma = morph.parse(word)[0].normal_form  # Лемматизация слова
        if lemma not in russian_stopwords:  # Дополнительная проверка на стоп-слова после лемматизации
            if lemma not in lemmas:
                lemmas[lemma] = set()
            lemmas[lemma].add(word)
    return lemmas


directory_path = '../task_1/pages/'
output_tokens_path = 'tokens.txt'
output_lemmas_path = 'lemmas.txt'

# Словарь для сбора всех лемм из всех файлов
all_lemmas = {}

for i in range(150):  # Обработка каждого файла в директории
    file_path = os.path.join(directory_path, f'page_{i}.txt')
    lemmas = process_text(file_path)
    # Обновление глобального словаря лемм
    for lemma, tokens in lemmas.items():
        if lemma not in all_lemmas:
            all_lemmas[lemma] = set()
        all_lemmas[lemma].update(tokens)

# Запись уникальных токенов
with open(output_tokens_path, 'w', encoding='utf-8') as tokens_file:
    unique_tokens = set()
    for tokens in all_lemmas.values():
        unique_tokens.update(tokens)  # Сбор уникальных токенов
    for token in sorted(unique_tokens):
        tokens_file.write(token + '\n')

# Запись лемм и соответствующих токенов
with open(output_lemmas_path, 'w', encoding='utf-8') as lemmas_file:
    for lemma, tokens in sorted(all_lemmas.items()):
        lemmas_file.write(f"{lemma}: {' '.join(sorted(tokens))}\n")
