import pymorphy2
import re
import random
import time
from collections import defaultdict
import pandas as pd
import requests
from collections import defaultdict
from bs4 import BeautifulSoup


# Список ключевых слов
keywords = [
    "Коррупция", "Взятка", "Подкуп", "Злоупотребление полномочиями", "Непотизм", "Бездействие",
    "Конфликт интересов", "Теневая экономика", "Финансовые махинации", "Противодействие коррупции", 
    "Транспарентность", "Подотчетность", "Мониторинг", "Антикоррупционная политика", "приговор", "дело",
    "Прозрачность финансирования", "Теневые сделки", "Откаты", "Хищение", "Родственник", "расследуется", 
    "расследование",  "Лоббизм", "Незаконное", "обогащение", "Контроль расходов", "Проверки деятельности", 
    "подозреваемый", "подоздревается", "Аудит", "Закупка", "Электронное правительство", "Похищение", "Отмывание", 
    "Задержание", "Рейдерство", "тенге", "долларов", "доллары", "Превышение власти", "Задержали", "Антикор", 
    "Агенство", "Уголовный кодекс", "Получение", "незаконного", "вознаграждения", "Концепция", "Преступление", 
    "средней тяжести", "небольшой тяжести", "Тяжкие", "Особо тяжкие", "Мошенничество", "Легализация",
    "миллиард", "миллион", "триллиард", "Обогатился", "Обогатились", "судебный", "процесс", "аким", 
    "начальник", "зам", "заместитель", "район", "город", "область", "село", "деревня", "Аул", "правонарушение", 
    "Антикора", "Антикору", "Антикором", "Антикоре"
    ]

dataset = pd.DataFrame(columns=["Date"] + keywords)

# Инициализация pymorphy2
morph = pymorphy2.MorphAnalyzer()
# Генерация всех форм ключевых слов
def generate_forms(word):
    parsed = morph.parse(word)[0]
    return {form.word for form in parsed.lexeme}
# Генерируем формы для ключевых слов
keyword_forms = {}
for keyword in keywords:
    keyword_forms[keyword.lower()] = generate_forms(keyword.lower())
# Объединяем все формы в один набор
all_keyword_forms = set()
for forms in keyword_forms.values():
    all_keyword_forms.update(forms)
# Функция подсчёта общего количества вхождений ключевых слов
def find_total_keyword_occurrences(text):
    tokens = re.findall(r'\b\w+\b', text.lower())  # Извлекаем только слова
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens]  # Лемматизация
    
    # Подсчитываем общее количество вхождений ключевых слов
    word_count = defaultdict(int)
    for word in lemmatized_tokens:
        if word in all_keyword_forms:
            word_count[word] += 1  # Увеличиваем счётчик для каждого вхождения
    
    return word_count


base_url1 = "https://tengrinews.kz"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

# Загрузка ссылок из CSV
links_df = pd.read_csv("news_links.csv")
total_links = len(links_df)
chunk_size = total_links // 5  # Делим на 5 частей

# Укажите начальный индекс для итерации
start_index = chunk_size * 2  # Изменяйте при каждом запуске

# Парсинг ссылок
all_results = []


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

        # Подсчитываем ключевые слова
        keyword_counts = find_total_keyword_occurrences(text)

        # Формируем результаты
        result = {"Дата": date, "URL": url}
        for keyword in keywords:
            result[keyword] = keyword_counts.get(keyword.lower(), 0)
        all_results.append(result)
        # Пауза для избежания блокировок
        time.sleep(random.uniform(2, 6))

    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

# Сохраняем результаты в CSV
iteration_number = start_index // chunk_size + 1
output_file = f"news_results_part{iteration_number}.csv"
results_df = pd.DataFrame(all_results)
results_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Результаты сохранены в '{output_file}'")