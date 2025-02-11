from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os
from utils import logging, scrape_listings, listing_urls_scraper, input_dir, output_dir


print(
    "=============================================\n"
    "          🌟 S-REALITY SCRAPER 🌟\n"
    "                by Anzywiz\n"
    
    "=============================================\n"
    "Choose a listing category to scrape:\n"
    "---------------------------------------------\n"
    " 1️⃣  Apartment (Byty)\n"
    " 2️⃣  Houses (Domy)\n"
    " 3️⃣  Land (Pozemky)\n"
    " 4️⃣  Commercial (Komercni)\n"
    " 5️⃣  Others (Ostatni)\n"
    "---------------------------------------------\n"
)

try:
    prompt = int(input("🔎 Enter the number corresponding to your category: "))
    if prompt not in range(1, 6):
        print("❌ Invalid choice! Please select a number between 1 and 5.")
        exit()
except ValueError:
    print("❌ Invalid input! Please enter a number between 1 and 5.")
    exit()


property_type_dict = {1: "byty", 2: "domy", 3: "pozemky", 4: "komercni", 5: "ostatni"}
property_type = property_type_dict[prompt]

print(f"✅ You selected category {prompt} ({property_type}). Starting the scraper...")

# scrape listings URL from all pages
listing_urls_scraper(property_type)

df = pd.read_csv(input_dir/f"{property_type}_listing_urls.csv")
total_listing_urls = df["listing_url"].dropna().to_list()


# check if data have ben scraped
scraped_data_path = output_dir / f"{property_type}.csv"
if os.path.isfile(scraped_data_path):
    # logging.info(f"Scraped data FOUND in output directory")

    df = pd.read_csv(scraped_data_path, on_bad_lines='skip', encoding='UTF-8', encoding_errors="replace")
    df.to_csv(scraped_data_path, index=False, encoding='UTF-8')
    df = df.drop_duplicates().dropna(axis=0, how="all")
    scraped_data = df["listing_url"].to_list()
    remaining_page_urls = list(set(total_listing_urls) - set(scraped_data))
else:
    remaining_page_urls = total_listing_urls

logging.info(f"{len(remaining_page_urls)} listing url to go!")

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(scrape_listings, listing_url, property_type) for listing_url in remaining_page_urls]
    for future in futures:
        try:
            result = future.result()
        except Exception as e:
            logging.error(f"Error: {e}")
            continue
