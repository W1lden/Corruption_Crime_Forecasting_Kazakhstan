import pymorphy3
import re
import pandas as pd
from collections import defaultdict

# Список ключевых слов (с сохранением многословных выражений)
keywords = [
    "коррупция", "взятка", "подкуп", "злоупотребление полномочиями", "непотизм", "бездействие",
    "конфликт интересов", "теневая экономика", "финансовые махинации", "противодействие коррупции", 
    "транспарентность", "подотчетность", "мониторинг", "приговор", "уголовное дело",
    "прозрачность финансирования", "теневые сделки", "откат", "откаты", "хищение", "родственник", 
    "расследуется", "расследование", "лоббизм", "незаконное обогащение", "контроль расходов", 
    "проверки деятельности", "подозреваемый", "подозревается", "аудит", "закупка", 
    "госзакупки", "госконтракт", "электронное правительство", "похищение", "отмывание", 
    "задержание", "рейдерство", "тенге", "доллар", "доллары", "миллион", "миллиард", "триллион",
    "превышение власти", "задержали", "агентство", "уголовный кодекс", "получение взятки", 
    "незаконное вознаграждение", "концепция", "преступление", "мошенничество", "легализация",
    "обогатился", "обогатились", "судебный процесс", "суд", "министерство", "парламент", 
    "мвд", "кнб", "депутат", "сенат", "комиссия", "конкурс", "должностное лицо", 
    "служебное положение", "фиктивный", "растратил", "растрата", "вымогательство", "халатность", 
    "аким", "начальник", "зам", "заместитель", "район", "город", "область", "село", "деревня", "аул",
    "правонарушение", "антикор", "антикора"
]

# Инициализация pymorphy3
morph = pymorphy3.MorphAnalyzer()

# Генерация всех форм ключевых слов (только для одиночных слов)
def generate_forms(word):
    parsed = morph.parse(word)[0]
    return {form.word for form in parsed.lexeme}

# Создаём набор всех форм ключевых слов (исключаем многословные выражения)
keyword_forms = {}
for keyword in keywords:
    if " " not in keyword:  # Пропускаем многословные фразы
        keyword_forms[keyword.lower()] = generate_forms(keyword.lower())

# Объединяем формы в один набор
all_keyword_forms = set()
for forms in keyword_forms.values():
    all_keyword_forms.update(forms)

# Функция подсчёта общего количества вхождений ключевых слов
def find_total_keyword_occurrences(text):
    text = text.lower()
    word_count = defaultdict(int)

    # Проверяем многословные фразы в тексте
    for phrase in keywords:
        if " " in phrase and phrase in text:  # Проверка фраз
            word_count[phrase] += text.count(phrase)  

    # Токенизация (учёт слов с дефисами)
    tokens = re.findall(r'\b[\w-]+\b', text)

    # Подсчёт одиночных слов
    for token in tokens:
        if token in all_keyword_forms:  # Проверяем без лемматизации
            lemma = morph.parse(token)[0].normal_form  # Лемматизируем
            if lemma in all_keyword_forms:
                word_count[lemma] += 1  

    return word_count

# Загружаем датасет новостей
df = pd.read_csv("../data/news_text_all.csv")
all_results = []

# Обрабатываем каждую новость
for index, row in df.iterrows():
    print(f"Парсим новость: {row['Date']}")
    try:
        date = row["Date"]
        text = row["Text"]

        # Подсчитываем ключевые слова
        keyword_counts = find_total_keyword_occurrences(text)

        # Формируем результаты
        result = {"Дата": date}
        for keyword in keywords:
            result[keyword] = keyword_counts.get(keyword.lower(), 0)
        all_results.append(result)

    except Exception as e:
        print(f"Ошибка при обработке {row['Date']}: {e}")

# Сохраняем результаты в CSV
results_df = pd.DataFrame(all_results)
results_df.to_csv("../data/news_text_parsed.csv", index=False, encoding='utf-8')
print("Результаты сохранены в news_text_parsed")
