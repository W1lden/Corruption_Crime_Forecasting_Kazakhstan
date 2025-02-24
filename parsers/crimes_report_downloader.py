from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import re
import requests
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- User input ---
start_date = input("Enter start date (YYYY-MM): ")
end_date = input("Enter end date (YYYY-MM): ")
report_name = input('Enter report name (default: "Отчет №3-К"): ') or "Отчет №3-К"
sections_input = input("Enter section numbers (comma-separated, or 'all' for all sections): ")

# Convert to datetime objects
start_date = datetime.strptime(start_date, "%Y-%m")
end_date = datetime.strptime(end_date, "%Y-%m")

# Determine required sections
if sections_input.lower() == "all":
    required_sections = None  # This means we accept any section
else:
    required_sections = set(map(int, sections_input.split(",")))

# --- Selenium setup ---
download_folder = "reports"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)  # Создаем папку, если ее нет

options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.path.abspath(download_folder)}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

# Open the website
url = "https://qamqor.gov.kz/crimestat/statistics"
driver.get(url)
wait = WebDriverWait(driver, 10)

# Function to ensure we're on the main statistics page
def ensure_main_page():
    """Checks if we are on the Statistical Reports page, and if not— restarts it."""
    current_url = driver.current_url
    if current_url != "https://qamqor.gov.kz/crimestat/statistics":
        print("Not on the main page. Reloading...")
        driver.get("https://qamqor.gov.kz/crimestat/statistics")
        time.sleep(3)
    else:
        print("Already on the main statistics page.")

# Tracking statistics
total_found = 0
successful_downloads = 0
failed_downloads = []

# --- Iterate over months ---
current_date = start_date
while current_date <= end_date:
    year = str(current_date.year)
    month = str(current_date.month)

    print(f"\nProcessing {year}-{month.zfill(2)}...")

    ensure_main_page()

    # Click on the target year
    year_element = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@aria-controls and text()='{year}']")))
    year_element.click()
    time.sleep(2)  # Ensure the page updates

    # Find the correct month dropdown for the selected year
    year_container_id = year_element.get_attribute("aria-controls")
    year_container = wait.until(EC.visibility_of_element_located((By.ID, year_container_id)))

    # Select the correct month
    month_dropdown = year_container.find_element(By.TAG_NAME, "select")
    select = Select(month_dropdown)
    select.select_by_value(month)  # Choose the correct month

    time.sleep(3)  # Wait for reports to load

    # Get the list of reports for the selected month
    reports = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "list-group-item-action")))

    for report in reports:
        try:
            text = report.text  # Handling the element disappearing error
        except:
            print("Skipping stale element...")
            continue  # If the element is missing, skip it.

        # Check if report matches the selected name
        if report_name in text:
            # Extract section numbers using regex
            sections_match = re.findall(r"\b(\d+)[\s,-]", text)
            sections_in_report = set(map(int, sections_match)) if sections_match else set()

            # Download the report if it contains required sections or all sections are allowed
            if required_sections is None or sections_in_report & required_sections:
                file_link = report.get_attribute("href")
                print(f"Found file: {text}")
                total_found += 1

                if file_link and file_link.lower().endswith(".xlsx"):
                    try:
                        # Checking the file availability
                        response = requests.head(file_link, verify=False)  # Ignoring the SSL error
                        if response.status_code == 200:  # The file exists, but there may be an empty page.
                            filename = file_link.split("/")[-1]
                            filepath = os.path.join(download_folder, filename)

                            # Delete the file before downloading (if there is an old one left)
                            if os.path.exists(filepath):
                                os.remove(filepath)

                            report.click()
                            time.sleep(5)

                            # Checking if the file has actually been downloaded
                            if os.path.exists(filepath):
                                successful_downloads += 1
                            else:
                                print(f"File {filename} was not downloaded!")
                                failed_downloads.append(f"{text} (Download failed)")

                        else:
                            failed_downloads.append(f"{text} (File not found)")
                            print(f"File not found: {text}")

                            # --- Go back to the "Statistical Reports" page ---
                            ensure_main_page()

                    except Exception as e:
                        failed_downloads.append(f"{text} (Error: {e})")
                        print(f"Error checking file: {text} - {e}")

    # Move to the next month
    current_date += timedelta(days=32)
    current_date = current_date.replace(day=1)  # Ensure we stay at the start of the month

# --- Save failed downloads to a text file ---
if failed_downloads:
    with open("failed_downloads.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_downloads))
    print(f"\nSome files could not be downloaded. See 'failed_downloads.txt' for details.")

# --- Print statistics ---
print("\nDownload completed.")
print(f"Total files found: {total_found}")
print(f"Successfully downloaded: {successful_downloads}")
print(f"Failed downloads: {len(failed_downloads)}")

driver.quit()
