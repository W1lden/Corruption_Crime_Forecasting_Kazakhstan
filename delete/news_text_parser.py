import pymorphy2
import re
import random
import time
from collections import defaultdict
import pandas as pd
import requests
from bs4 import BeautifulSoup

# List of keywords
keywords = [
    "Коррупция", "Взятка", "Подкуп", "Злоупотребление полномочиями", "Непотизм", "Бездействие",
    "Конфликт интересов", "Теневая экономика", "Финансовые махинации", "Противодействие коррупции", 
    "Транспарентность", "Подотчетность", "Мониторинг", "Антикоррупционная политика", "приговор", "дело",
    "Прозрачность финансирования", "Теневые сделки", "Откаты", "Хищение", "Родственник", "расследуется", 
    "расследование", "Лоббизм", "Незаконное", "обогащение", "Контроль расходов", "Проверки деятельности", 
    "подозреваемый", "подоздревается", "Аудит", "Закупка", "Электронное правительство", "Похищение", "Отмывание", 
    "Задержание", "Рейдерство", "тенге", "долларов", "доллары", "Превышение власти", "Задержали", "Антикор", 
    "Агенство", "Уголовный кодекс", "Получение", "незаконного", "вознаграждения", "Концепция", "Преступление", 
    "средней тяжести", "небольшой тяжести", "Тяжкие", "Особо тяжкие", "Мошенничество", "Легализация",
    "миллиард", "миллион", "триллиард", "Обогатился", "Обогатились", "судебный", "процесс", "аким", 
    "начальник", "зам", "заместитель", "район", "город", "область", "село", "деревня", "Аул", "правонарушение", 
    "Антикора", "Антикору", "Антикором", "Антикоре"
]

dataset = pd.DataFrame(columns=["Date"] + keywords)

# Initialize pymorphy2
morph = pymorphy2.MorphAnalyzer()

# Generate all forms of a keyword
def generate_forms(word):
    parsed = morph.parse(word)[0]
    return {form.word for form in parsed.lexeme}

# Generate forms for all keywords
keyword_forms = {}
for keyword in keywords:
    keyword_forms[keyword.lower()] = generate_forms(keyword.lower())

# Combine all forms into a single set
all_keyword_forms = set()
for forms in keyword_forms.values():
    all_keyword_forms.update(forms)

# Function to count total occurrences of keywords
def find_total_keyword_occurrences(text):
    tokens = re.findall(r'\b\w+\b', text.lower())  # Extract only words
    lemmatized_tokens = [morph.parse(token)[0].normal_form for token in tokens]  # Lemmatize
    
    # Count keyword occurrences
    word_count = defaultdict(int)
    for word in lemmatized_tokens:
        if word in all_keyword_forms:
            word_count[word] += 1
    return word_count

base_url1 = "https://tengrinews.kz"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

# Load links from CSV
links_df = pd.read_csv("news_links.csv")
total_links = len(links_df)
chunk_size = total_links // 5  # Divide into 5 parts

# Set the starting index for iteration
start_index = chunk_size * 2  # Change this value for each run

# Parse links
all_results = []

for index, row in links_df.iloc[start_index:start_index + chunk_size].iterrows():
    url = row["News Link"]
    if not url.startswith("http"):
        url = f"{base_url1}{url}"  # Add domain to relative links
    print(f"Parsing news: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error loading {url}: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract publication date
        date = row["Date"]

        # Extract news article text
        article_body = soup.find('div', {'class': 'content_main_text'})
        text = article_body.get_text(strip=True) if article_body else ""

        # Count keywords
        keyword_counts = find_total_keyword_occurrences(text)

        # Build results
        result = {"Дата": date, "URL": url}
        for keyword in keywords:
            result[keyword] = keyword_counts.get(keyword.lower(), 0)
        all_results.append(result)

        # Delay to avoid being blocked
        time.sleep(random.uniform(2, 6))

    except Exception as e:
        print(f"Error processing {url}: {e}")

# Save results to CSV
iteration_number = start_index // chunk_size + 1
output_file = f"news_results_part{iteration_number}.csv"
results_df = pd.DataFrame(all_results)
results_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"Results saved to '{output_file}'")
