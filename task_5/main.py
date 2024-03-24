import numpy as np
import re
from os import listdir
from os.path import join
from scipy.spatial import distance
import pymorphy2


# Функция для получения списка ссылок из файла
def load_links(filepath):
    links = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            # Игнорируем идентификатор, сохраняем только URL
            _, url = line.strip().split(' ', 1)
            links[str(idx)] = url
    return links


# Загрузка лемм и формирование списка уникальных лемм из всех документов
def extract_lemmas(tf_idf_path):
    lemmas = set()
    for filename in listdir(tf_idf_path):
        with open(join(tf_idf_path, filename), 'r', encoding='utf-8') as file:
            for line in file:
                lemma = line.split()[0]
                lemmas.add(lemma)  # Добавляем уникальную лемму в множество
    return list(lemmas)


# Создание матрицы TF-IDF для документов
def build_tf_idf_matrix(tf_idf_path, lemmas):
    files = listdir(tf_idf_path)
    matrix = np.zeros((len(files), len(lemmas)))  # Инициализация матрицы нулями
    for filename in files:
        doc_id = int(re.search(r'\d+', filename).group())  # Извлекаем ID документа из имени файла
        with open(join(tf_idf_path, filename), 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 3:
                    lemma, _, tf_idf = parts
                    if lemma in lemmas:
                        lemma_index = lemmas.index(lemma)
                        matrix[doc_id][lemma_index] = float(tf_idf)
    return matrix


# Функция для лемматизации запроса пользователя
def lemmatize_query(query, morph_analyzer, lemmas):
    tokens = re.findall(r'\w+', query.lower())
    lemmatized_vector = np.zeros(len(lemmas))
    for token in tokens:
        lemma = morph_analyzer.parse(token)[0].normal_form
        if lemma in lemmas:
            index = lemmas.index(lemma)
            lemmatized_vector[index] = 1  # Устанавливаем 1 для леммы в векторе запроса
    return lemmatized_vector


# Функция поиска документов по запросу
def perform_search(query, links, lemmas, matrix, morph_analyzer):
    query_vector = lemmatize_query(query, morph_analyzer, lemmas)
    scores = {}
    for idx, doc_vector in enumerate(matrix):
        similarity = 1 - distance.cosine(query_vector, doc_vector)  # Рассчитываем косинусное сходство
        if similarity > 0:
            scores[links[str(idx)]] = similarity  # Сохраняем сходство, если оно больше 0
    # Возвращаем отсортированный список результатов
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]


# Функция поиска
def vector_search(query):
    return perform_search(query, links, lemmas, tf_idf_matrix, morph_analyzer)


# Инициализация
morph_analyzer = pymorphy2.MorphAnalyzer()
links_path = '../task_1/index.txt'
tf_idf_path = '../task_4/tf_idf_lemmas'
links = load_links(links_path)
lemmas = extract_lemmas(tf_idf_path)
tf_idf_matrix = build_tf_idf_matrix(tf_idf_path, lemmas)
