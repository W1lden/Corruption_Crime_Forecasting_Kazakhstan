import csv
import random
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


base_url1 = "https://tengrinews.kz"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

# Загрузка ссылок из CSV
links_df = pd.read_csv("../data/news_links.csv")
total_links = len(links_df)
chunk_size = total_links // 5  # Делим на 5 частей

# Укажите начальный индекс для итерации
start_index = chunk_size * 3  # Изменяйте при каждом запуске

# Парсинг ссылок
all_results = []

# Создаем CSV файл с заголовками (один раз)
output_file = f"news_text_part{start_index // chunk_size + 1}.csv"
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Text"])  # Заголовки

for index, row in links_df.iloc[start_index:start_index + chunk_size].iterrows():
    url = row["News Link"]
    if not url.startswith("http"):
        url = f"{base_url1}{url}"  # Добавляем домен к относительным ссылкам
    print(f"Парсим новость: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка при загрузке {url}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Извлекаем дату публикации
        date = row["Date"]

        # Извлекаем текст новости
        article_body = soup.find('div', {'class': 'content_main_text'})
        text = article_body.get_text(strip=True) if article_body else ""

        # Записываем в CSV
        with open(output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([date, text])
        

        # Пауза для избежания блокировок
        time.sleep(random.uniform(2, 6))

    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

print(f"Результаты сохранены в '{output_file}'")
