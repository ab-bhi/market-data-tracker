import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_FILE = "Live_Indian_Stocks.csv"
TOTAL_PAGES = 111  # Screener total pages for Market Cap > 0

def fetch_screener_data():
    all_rows = []
    headers_saved = False

    print("Fetching market data...")
    for page in range(1, TOTAL_PAGES + 1):
        url = f"https://www.screener.in/screen/raw/?sort=current+price&order=asc&source_id=&query=Market+Capitalization+%3E+0&page={page}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Skipping page {page} (Status: {res.status_code})")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            if not table:
                continue

            # Capture column names on first page
            if not headers_saved:
                headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
                all_rows.append(headers)
                headers_saved = True

            # Extract row values
            for tr in table.find("tbody").find_all("tr"):
                row = [td.get_text(strip=True) for td in tr.find_all("td")]
                if row:
                    all_rows.append(row)

            time.sleep(0.8)  # Gentle delay to avoid rate limiting
        except Exception as e:
            print(f"Error on page {page}: {e}")

    # Overwrite the CSV
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"Done! Updated {len(all_rows) - 1} stocks into {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_screener_data()
