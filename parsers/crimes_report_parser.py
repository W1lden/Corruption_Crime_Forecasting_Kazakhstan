import os
import pandas as pd
import re
from collections import defaultdict
from datetime import datetime, timedelta


def parse_filename(filename):
    """Parses the report file name and extracts date and type (general/agency)."""

    old_format_match = re.match(r"(\d{6})3K.*?_ru\.(xlsx|XLSX)", filename, re.IGNORECASE)
    if old_format_match:
        date_str = old_format_match.group(1)
        month = int(date_str[:2])
        year = int(date_str[2:])
        return {"year": year, "month": month, "type": "general"}

    new_format_match = re.match(r"(\d{6})_3k_(\d{5})___ru\.(xlsx|XLSX)", filename, re.IGNORECASE)
    if new_format_match:
        date_str = new_format_match.group(1)
        agency_code = new_format_match.group(2)
        year = int(date_str[:4])
        month = int(date_str[4:])
        report_type = "general" if agency_code == "00000" else "agency"
        return {"year": year, "month": month, "type": report_type, "agency_code": agency_code}

    return None


def extract_crime_count(file_path):
    """Reads an Excel file, finds the correct sheet by checking B7, and extracts E7."""
    try:
        xls = pd.ExcelFile(file_path, engine="openpyxl")

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

            if df.shape[0] > 6 and df.shape[1] > 4:
                if str(df.iat[6, 1]).strip() == "Всего коррупционных преступлений":
                    crime_count = df.iat[6, 4]

                    if isinstance(crime_count, (int, float)):
                        return int(crime_count)

        print(f"Warning: No valid crime count found in {file_path}")
        return None

    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# --- Path to reports ---
REPORTS_DIR = "../data/reports"

# --- Dictionary to store results ---
crime_data = defaultdict(lambda: None)  # Default is None for missing months
agency_data = defaultdict(int)  # Stores agency-specific totals

# --- Process each file ---
for filename in os.listdir(REPORTS_DIR):
    file_path = os.path.join(REPORTS_DIR, filename)

    file_info = parse_filename(filename)
    if not file_info:
        print(f"Skipping unknown file format: {filename}")
        continue

    year, month, report_type = file_info["year"], file_info["month"], file_info["type"]
    key = (year, month)

    crime_count = extract_crime_count(file_path)
    if crime_count is None:
        continue

    if report_type == "general":
        if crime_count < 10:
            print(f"Skipping {filename} as it may be incorrect (possibly section 4).")
            continue
        else:
            crime_data[key] = crime_count
    else:
        agency_data[key] += crime_count

    print(f"Processed {filename}: {crime_count}")

# --- Fill missing months ---
all_dates = sorted(set(crime_data.keys()) | set(agency_data.keys()))  # Get all available months
start_date = min(all_dates)
end_date = max(all_dates)

current_date = datetime(start_date[0], start_date[1], 1)
while current_date <= datetime(end_date[0], end_date[1], 1):
    key = (current_date.year, current_date.month)

    if crime_data[key] is None:  # If no general report, use agencies
        if agency_data[key] > 0:
            print(f"Using agency reports for {key[0]}-{str(key[1]).zfill(2)} (total: {agency_data[key]})")
            crime_data[key] = agency_data[key]

    current_date += timedelta(days=32)
    current_date = current_date.replace(day=1)

# --- Convert results to DataFrame and save ---
df_result = pd.DataFrame([
    {"Date": f"{year}-{str(month).zfill(2)}", "Total Crimes": total}
    for (year, month), total in sorted(crime_data.items())
])

df_result.to_csv("../data/parsed_crimes_report_data.csv", index=False, encoding="utf-8")
print("\nParsing complete. Results saved to 'parsed_crime_data.csv'.")
