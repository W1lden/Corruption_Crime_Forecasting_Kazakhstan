import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup


# Russian month mapping
month_mapping = {
    "января": "January", "февраля": "February", "марта": "March",
    "апреля": "April", "мая": "May", "июня": "June",
    "июля": "July", "августа": "August", "сентября": "September",
    "октября": "October", "ноября": "November", "декабря": "December"
}

# --- User input ---
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")

# Convert input dates to datetime objects
start_date = datetime.strptime(start_date, "%Y-%m-%d")
end_date = datetime.strptime(end_date, "%Y-%m-%d")

# --- Config ---
BASE_URL = "https://tengrinews.kz/tag/коррупция/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
OUTPUT_FILE = "news_links.csv"

all_news_links = []
page = 1  # Start from the first page

# --- Parse pages ---
while True:
    url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
    print(f"Parsing page: {url}")

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Error loading page {url}")
            break  # Stop if the page fails to load

        soup = BeautifulSoup(response.text, "html.parser")
        news_list = soup.find_all("div", {"class": "content_main_item"})  # News list

        # Stop if no more news found
        if not news_list:
            print("No more news found. Stopping...")
            break

        stop_parsing = False  # Flag for stopping parsing of all pages

        for news_item in news_list:
            first_link = news_item.find("a", href=True)
            date_element = news_item.find("div", {"class": "content_main_item_meta"}).find_all("span")[0]

            if first_link and date_element:
                date_text = date_element.text.strip()
                
                # Replace Russian month with English equivalent
                for ru_month, en_month in month_mapping.items():
                    date_text = date_text.replace(ru_month, en_month)

                # Convert to datetime
                news_date = datetime.strptime(date_text, "%d %B %Y")
                
                # Stop parsing if the news is older than the start date
                if news_date < start_date:
                    print("Reached older news. Stopping...")
                    stop_parsing = True
                    break  # Stop further parsing

                # Add only if the date is within the range
                if start_date <= news_date <= end_date:
                    all_news_links.append((first_link["href"], news_date.strftime("%Y-%m-%d")))
        
        # If we find news that is too old, we stop parsing all pages.
        if stop_parsing:
            break


        # Random delay to avoid blocking
        time.sleep(random.uniform(2, 5))
        page += 1  # Move to the next page

    except Exception as e:
        print(f"Error processing page {url}: {e}")
        break  # Stop parsing in case of error

# --- Remove duplicates ---
all_news_links = list(set(all_news_links))
print(f"Found {len(all_news_links)} news links.")

# --- Save results ---
links_df = pd.DataFrame(all_news_links, columns=["News Link", "Date"])
OUTPUT_DIR = "..\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
links_df.to_csv(output_path, index=False, encoding="utf-8")
print(f"Links saved to '{output_path}'")
