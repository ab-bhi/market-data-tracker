import csv
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

OUTPUT_FILE = "Live_Indian_Stocks.csv"

def fetch_screener_data():
    all_rows = []
    headers_saved = False
    page = 1

    print("Fetching market data...")
    
    while True:
        # Your specific public screen URL
        url = f"https://www.screener.in/screens/3994696/git-this/?page={page}"
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            
            if res.status_code in [401, 403]:
                print(f"Access Denied on page {page}. Screener is blocking the request. Ensure you are using a PUBLIC screen URL.")
                break
                
            if res.status_code != 200:
                print(f"Failed on page {page} (Status: {res.status_code}). Retrying in 5 seconds...")
                time.sleep(5)
                continue 

            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            
            if not table:
                print(f"No more data found or hit a login wall. Reached the end at page {page - 1}.")
                break

            if not headers_saved:
                thead = table.find("thead")
                if thead:
                    headers = [th.get_text(strip=True) for th in thead.find_all("th")]
                    all_rows.append(headers)
                    headers_saved = True

            rows_found = 0
            tbody = table.find("tbody")
            if tbody:
                for tr in tbody.find_all("tr"):
                    if not tr.get('data-row-company-id'):
                        continue
                        
                    row = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if row:
                        all_rows.append(row)
                        rows_found += 1
            
            if rows_found == 0:
                print(f"Page {page} loaded but contained no stock rows. Stopping.")
                break

            print(f"Successfully scraped page {page} ({rows_found} stocks)")
            page += 1
            time.sleep(2)  
            
        except Exception as e:
            print(f"Error on page {page}: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)

    total_stocks = max(0, len(all_rows) - 1)
    print(f"Done! Updated {total_stocks} stocks into {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_screener_data()
