# Загружает инвертированный индекс из файла
def load_inverted_index(filepath):
    inverted_index = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(' ')
            word = parts[0]
            page_ids = set(map(int, parts[1:]))
            inverted_index[word] = page_ids
    return inverted_index


# Загружает соответствие между идентификаторами страниц и их URL из файла
def load_id_to_url_mapping(filepath):
    id_to_url_mapping = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            page_id, url = line.strip().split(' ', 1)
            id_to_url_mapping[int(page_id)] = url
    return id_to_url_mapping


# Разбивает строковый запрос на список подзапросов
def parse_query(query):
    or_split = [part.strip() for part in query.split("OR")]  # Разделяем запрос на подзапросы по OR
    # Для каждого подзапроса далее разделяем по AND и обрезаем пробелы
    parsed_query = [[word.strip() for word in subquery.split("AND")] for subquery in or_split]
    return parsed_query  # Возвращаем список подзапросов


# Выполняет поиск по подзапросу, обрабатывая операторы AND и NOT
def execute_search(subquery, inverted_index, all_page_ids):
    subquery_results = None
    for word in subquery:
        if word.startswith("NOT "):
            word = word[4:]  # удаление префикса "NOT "
            # Вычитаем множество страниц для слова после NOT из текущего результата
            if subquery_results is None:
                subquery_results = all_page_ids - inverted_index.get(word, set())
            else:
                subquery_results -= inverted_index.get(word, set())
        else:
            # Для обычных слов находим пересечение текущего результата с множеством страниц слова
            if subquery_results is None:
                subquery_results = inverted_index.get(word, set())
            else:
                subquery_results &= inverted_index.get(word, set())

    return subquery_results if subquery_results is not None else all_page_ids


# Выполняет булев поиск по заданному запросу.
def boolean_search(query, inverted_index, all_page_ids):
    parsed_query = parse_query(query)  # Парсим запрос на подзапросы
    final_results = set()
    for subquery in parsed_query:
        subquery_result = execute_search(subquery, inverted_index, all_page_ids)
        final_results |= subquery_result  # Объединяем результаты подзапросов с помощью OR
    return final_results  # Возвращаем итоговый набор ID страниц


inverted_index_path = 'inverted_index.txt'
page_ids_path = '../task_1/index.txt'

inverted_index = load_inverted_index(inverted_index_path)
id_to_url_mapping = load_id_to_url_mapping(page_ids_path)

query = input("Ваш запрос: ")
result_ids = boolean_search(query, inverted_index, id_to_url_mapping)

print("Результаты поиска:")
for page_id in result_ids:
    print(id_to_url_mapping.get(page_id, "URL не найден"))
