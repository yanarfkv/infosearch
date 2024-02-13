import requests
from bs4 import BeautifulSoup
import os

# Базовый URL сайта
base_url = 'https://sibac.info'

# Создание папки для страниц, если она не существует
if not os.path.exists('pages'):
    os.makedirs('pages')

# Запись в файл index.txt
with open('index.txt', 'w', encoding='utf-8') as index_file:
    page_number = 1
    article_count = 0

    # Перебор страниц (на каждой странице 15 статей => получаем 150 страниц со статьями)
    while page_number <= 10:
        archive_url = f"{base_url}/arhive-article?page={page_number}"
        response = requests.get(archive_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            archive_wrap = soup.find('div', id='archive-wrapp')

            # Извлечение всех ссылок на статьи
            for link in archive_wrap.find_all('a', href=True):
                article_url = base_url + link['href']
                article_response = requests.get(article_url)
                if article_response.status_code == 200:
                    # Запись в файл index.txt и сохранение страницы
                    filename = f"pages/page_{article_count}.txt"
                    with open(filename, 'w', encoding='utf-8') as file:
                        file.write(article_response.text)
                    index_file.write(f"{article_count} {article_url}\n")
                    article_count += 1
        else:
            print(f"Ошибка при доступе к странице: {archive_url}")
        page_number += 1
