import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_FILE = "Live_Indian_Stocks.csv"

def fetch_screener_data():
    all_rows = []
    headers_saved = False
    page = 1

    print("Fetching market data...")
    # Using a while loop to keep going until there are no more pages
    while True:
        # We removed the >0 rule so it catches everything, including 0 cap stocks
        url = f"https://www.screener.in/screen/raw/?sort=current+price&order=asc&source_id=&page={page}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code != 200:
                print(f"Failed on page {page} (Status: {res.status_code}). Retrying in 5 seconds...")
                time.sleep(5)
                continue # Retries the exact same page instead of skipping it

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            
            # If there's no table, we have officially passed the last page
            if not table:
                print(f"No more data found. Reached the end at page {page - 1}.")
                break

            # Capture column names on the very first page
            if not headers_saved:
                headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
                all_rows.append(headers)
                headers_saved = True

            # Extract row values
            rows_found = 0
            for tr in table.find("tbody").find_all("tr"):
                row = [td.get_text(strip=True) for td in tr.find_all("td")]
                if row:
                    all_rows.append(row)
                    rows_found += 1
            
            # If a page loads but has zero rows of stocks, we are done
            if rows_found == 0:
                break

            print(f"Successfully scraped page {page}")
            page += 1
            time.sleep(1)  # Gentle delay so we don't get blocked
            
        except Exception as e:
            print(f"Error on page {page}: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    # Save everything to the CSV
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    print(f"Done! Updated {len(all_rows) - 1} stocks into {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_screener_data()
