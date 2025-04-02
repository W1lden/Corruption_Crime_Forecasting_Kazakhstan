import pymorphy3
import re
import pandas as pd
from collections import defaultdict

# List of keywords (including multi-word expressions)
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

# Initialize pymorphy3
morph = pymorphy3.MorphAnalyzer()

# Generate all forms of keywords (only for single words)
def generate_forms(word):
    parsed = morph.parse(word)[0]
    return {form.word for form in parsed.lexeme}

# Create a set of all keyword forms (exclude multi-word expressions)
keyword_forms = {}
for keyword in keywords:
    if " " not in keyword:  # Skip multi-word expressions
        keyword_forms[keyword.lower()] = generate_forms(keyword.lower())

# Combine all forms into one set
all_keyword_forms = set()
for forms in keyword_forms.values():
    all_keyword_forms.update(forms)

# Function to count total keyword occurrences
def find_total_keyword_occurrences(text):
    text = text.lower()
    word_count = defaultdict(int)

    # Check for multi-word phrases in the text
    for phrase in keywords:
        if " " in phrase and phrase in text:
            word_count[phrase] += text.count(phrase)

    # Tokenization (including hyphenated words)
    tokens = re.findall(r'\b[\w-]+\b', text)

    # Count single word keywords
    for token in tokens:
        if token in all_keyword_forms:
            lemma = morph.parse(token)[0].normal_form
            if lemma in all_keyword_forms:
                word_count[lemma] += 1

    return word_count

# Load the news dataset
df = pd.read_csv("../data/news_text_all.csv")
all_results = []

# Process each news article
for index, row in df.iterrows():
    print(f"Processing article: {row['Date']}")
    try:
        date = row["Date"]
        text = row["Text"]

        # Count keyword occurrences
        keyword_counts = find_total_keyword_occurrences(text)

        # Prepare result row
        result = {"Date": date}
        for keyword in keywords:
            result[keyword] = keyword_counts.get(keyword.lower(), 0)
        all_results.append(result)

    except Exception as e:
        print(f"Error while processing {row['Date']}: {e}")

# Save results to CSV
results_df = pd.DataFrame(all_results)
results_df.to_csv("../data/news_text_parsed.csv", index=False, encoding='utf-8')
print("Results saved to news_text_parsed.csv")
