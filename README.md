# Corruption_Crime_Forecasting_Kazakhstan
This project forecasts corruption crime trends in Kazakhstan using regression models and Time Series Analysis based on official reports and news data. 

# Part one
This project automates the downloading and parsing of official corruption crime reports in Kazakhstan. It extracts monthly crime statistics from `.xlsx` reports and creates a structured dataset for further analysis.  

## 🚀 Features  
✅ Automatically navigates the official statistics website  
✅ Selects reports by **year, month, and section**  
✅ Downloads **all relevant reports** for a given period  
✅ Parses Excel files, **extracting total crime numbers**  
✅ Handles **missing reports** and **merges agency-specific data**  
✅ Outputs a **clean dataset** ready for analysis  

## 📂 Folder Structure  
---

## 🛠 Installation  
1️⃣ Clone the repository  
```
git clone https://github.com/w1lden/Corruption_Crime_Forecasting_Kazakhstan.git
cd Corruption_Crime_Forecasting_Kazakhstan
```
2️⃣ Install dependencies
```
pip install -r requirements.txt
```
3️⃣ Run the scraper (downloads reports)
```
python parsers/crimes_parser.py
```
4️⃣ Run the report parser (extracts data)
```
python parsers/crimes_report_parser.py
```
🏆 Example Output

| Date    | Total Crimes |
|---------|-------------|
| 2016-11 | 3463        |
| 2016-12 | 3214        |
| 2017-01 | 1137        |
| ...     | ...         |
| 2025-01 | 730        |


## 🔍 How It Works  

1️⃣ **Scraping:** The script opens the statistics website and navigates through available reports.  
2️⃣ **Filtering:** It selects reports by **year, month, and section**, ensuring only relevant files are downloaded.  
3️⃣ **Downloading:** Files are automatically saved in the `data/reports/` folder.  
4️⃣ **Parsing:** The report parser extracts the **total number of corruption crimes** from the correct Excel sheet.  
5️⃣ **Merging:** If reports are split by different agencies, it sums them into a **single monthly value**.  
6️⃣ **Output:** The final dataset is stored as `parsed_crimes_report_data.csv` for further analysis.   


📌 Handling Missing Reports
If an official report is missing, the script logs it and fills the gap with NaN.
Missing values in parsed_crimes_report_data.csv can be interpolated using:
```
df["Total Crimes"] = df["Total Crimes"].interpolate(method="linear").apply(
lambda x: np.ceil(x) if x % 1 >= 0.5 else np.floor(x)
)
```
This ensures smooth, realistic data trends.



💡 This project is part of a Master's Thesis on corruption crime forecasting.  
🔗 Author: Bitanov Assanali  
📊 Data Source: qamqor.gov.kz
