import os
import math
from collections import defaultdict
import re
from bs4 import BeautifulSoup
import pymorphy2
from nltk.corpus import stopwords

# Загрузка списка стоп-слов
try:
    russian_stopwords = stopwords.words('russian')
except LookupError:
    import nltk

    nltk.download('stopwords')
    russian_stopwords = stopwords.words('russian')

morph = pymorphy2.MorphAnalyzer()


# Чтение строк из файла и возврат их в виде списка
def read_file_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().splitlines()


# Очистка и лемматизация слов
def process_text(html_content, process_lemmas=True):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b', text)
    # Использование множества для исключения повторений
    processed_words = set()
    for word in words:
        word_lower = word.lower()
        if word_lower not in russian_stopwords:  # Проверка на наличие слова в списке стоп-слов
            if process_lemmas:
                processed_word = morph.parse(word_lower)[0].normal_form  # Лемматизация слова
            else:
                processed_word = word_lower
            if processed_word not in russian_stopwords:
                processed_words.add(processed_word)
    return processed_words


# Расчет TF и IDF для слов, найденных в документе
def calculate_tf_idf_for_document(processed_words, total_docs, inverted_index):
    tf = defaultdict(int)
    for word in processed_words:
        tf[word] += 1  # Подсчет частоты слова (TF)

    tf_idf = {}
    for word, count in tf.items():
        doc_count = len(inverted_index.get(word, []))  # Получение количества документов, содержащих слово
        idf = calculate_idf(doc_count, total_docs)  # Расчет IDF
        tf_idf[word] = (idf, count * idf)  # Расчет TF-IDF
    return tf_idf


# Расчет IDF для слова
def calculate_idf(doc_count, total_docs):
    return math.log((total_docs + 1) / (doc_count + 1)) + 1


# Запись результатов TF-IDF в файл
def write_tf_idf_to_file(tf_idf, output_file_path):
    with open(output_file_path, 'w+', encoding='utf-8') as file:
        for word, (idf, tf_idf_value) in tf_idf.items():
            file.write(f"{word} {idf} {tf_idf_value}\n")


def main(lemmas_path, tokens_path, inverted_index_path, pages_directory):
    # Чтение файлов с леммами и токенами, а также инвертированным индексом
    lemmas = set(read_file_lines(lemmas_path))
    tokens = set(read_file_lines(tokens_path))
    inverted_index_lines = read_file_lines(inverted_index_path)
    # Преобразование инвертированного индекса в словарь
    inverted_index = {line.split()[0]: set(line.split()[1:]) for line in inverted_index_lines}

    # Получение общего количества документов в директории
    total_docs = len(os.listdir(pages_directory))

    # Обработка каждого документа в директории
    for doc_file in os.listdir(pages_directory):
        # Формирование полного пути к файлу документа
        doc_path = os.path.join(pages_directory, doc_file)
        # Чтение содержимого HTML-файла
        with open(doc_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Обработка и подсчет TF-IDF для токенов без лемматизации
        processed_tokens = process_text(html_content, process_lemmas=False)
        tf_idf_tokens = calculate_tf_idf_for_document(processed_tokens, total_docs, inverted_index)
        tokens_file_path = f"tf_idf_tokens/tokens_tfidf_{doc_file}"
        # Запись результатов TF-IDF для токенов в файл
        write_tf_idf_to_file(tf_idf_tokens, tokens_file_path)

        # Обработка и подсчет TF-IDF для лемм с лемматизацией
        processed_lemmas = process_text(html_content, process_lemmas=True)
        tf_idf_lemmas = calculate_tf_idf_for_document(processed_lemmas, total_docs, inverted_index)
        lemmas_file_path = f"tf_idf_lemmas/lemmas_tfidf_{doc_file}"
        # Запись результатов TF-IDF для лемм в файл
        write_tf_idf_to_file(tf_idf_lemmas, lemmas_file_path)


if __name__ == '__main__':
    lemmas_path = '../task_2/lemmas.txt'
    tokens_path = '../task_2/tokens.txt'
    inverted_index_path = '../task_3/inverted_index.txt'
    pages_directory = '../task_1/pages'
    main(lemmas_path, tokens_path, inverted_index_path, pages_directory)
