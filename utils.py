import requests
from bs4 import BeautifulSoup
import csv
import os
from pathlib import Path
from urllib.parse import urlencode
import logging
import re
import pandas as pd
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


logging.basicConfig(format="%(levelname)s: %(asctime)s: %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

base_url = "https://www.sreality.cz"


base_dir = Path(os.getcwd())
output_dir = base_dir/'data'
input_dir = base_dir/'listings url'

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)


def get_soup(url, param=None):
    r = requests.get(url, params=param)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        return soup
    else:
        raise Exception(f"Error {r.status_code} getting response for {url}")


def get_property_page_urls(property_type):
    """
    Generate paginated URLs for different property types and sizes on sreality.cz.

    Args:
        property_type (str): Type of property to search (byty, domy, pozemky, komercni, ostatni)

    Returns:
        list: List of paginated URLs for the specified property type and sizes
    """
    # Define property sizes for each property type
    PROPERTY_SIZES = {
        "byty": [
            "1+1", "1+kk", "2+kk", "3+1", "3+kk", "2+1", "4+1", "4+kk",
            "5+1", "5+kk", "6-a-vice", "atypicky", "pokoj"
        ],
        "domy": [
            '1-pokoj', '2-pokoje', '3-pokoje', '4-pokoje', '5-a-vice', 'atypicky'
        ],
        "pozemky": [
            "komercni-pozemky", "lesy", "louky", "ostatni-pozemky", "pole",
            "rybniky", "sady-vinice", "stavebni-parcely", "zahrady"
        ],
        "komercni": [
            'apartmany', 'cinzovni-domy', 'kancelare', 'obchodni-prostory',
            'ordinace', 'ostatni-komercni-prostory', 'restaurace', 'sklady',
            'ubytovani', 'virtualni-kancelare', 'vyrobni-prostory', 'zemedelske-objekty'
        ],
        "ostatni": ['ostatni']
    }

    # Validate property type
    if property_type not in PROPERTY_SIZES:
        raise ValueError(f"Invalid property type: {property_type}")

    base_url = f"https://www.sreality.cz/hledani/{property_type}"
    property_sub_urls = []

    # Get global max pages and validate once at the beginning
    max_pages = 0
    authorized_for_high_pages = False

    # First pass to find maximum available pages across all sizes
    for size in PROPERTY_SIZES[property_type]:
        if property_type in ["byty", "domy"]:
            url_generator = lambda page: f"{base_url}?{urlencode({'strana': page, 'velikost': size})}"
        elif property_type in ["pozemky", "komercni"]:
            url_generator = lambda page: f"{base_url}/{size}?strana={page}"
        elif property_type == "ostatni":
            url_generator = lambda page: f"{base_url}?strana={page}"

        try:
            soup = get_soup(url_generator(1))
            last_page_no = int(get_last_page_no(soup))
            max_pages = max(max_pages, last_page_no)
        except Exception as e:
            logging.error(f"Error checking pages for {property_type} - {size}: {e}")
            continue

    # One-time validation for pages to scrape
    try:
        pages_to_scrape = int(input(f"How many pages do you want to scrape? (1-{max_pages}): "))

        # Validate range and adjust if too high
        if pages_to_scrape > max_pages:
            logging.info(f"Adjusting requested pages from {pages_to_scrape} to maximum available: {max_pages}")
            pages_to_scrape = max_pages
        elif pages_to_scrape < 1:
            logging.error("Must scrape at least 1 page")
            return []

        # One-time passcode check if needed
        if pages_to_scrape > 5:
            print(f"It seems you want to scrape above 5 pages!!."
                  f"\nKindly check tg group for passcode: https://t.me/bot_arena_chat")
            try:
                passcode = int(input(f"Input scraper passcode: "))
                if passcode != 12345:
                    logging.error("INVALID CODE")
                    return []
                authorized_for_high_pages = True
            except ValueError:
                logging.error("INVALID CODE FORMAT - Must be a number")
                return []

    except ValueError:
        logging.error("Please enter a valid integer for number of pages")
        return []

    # Now generate URLs using the validated pages_to_scrape
    for size in PROPERTY_SIZES[property_type]:
        if property_type in ["byty", "domy"]:
            url_generator = lambda page: f"{base_url}?{urlencode({'strana': page, 'velikost': size})}"
        elif property_type in ["pozemky", "komercni"]:
            url_generator = lambda page: f"{base_url}/{size}?strana={page}"
        elif property_type == "ostatni":
            url_generator = lambda page: f"{base_url}?strana={page}"

        try:
            soup = get_soup(url_generator(1))
            last_page_no = int(get_last_page_no(soup))

            # Use minimum of pages_to_scrape and available pages for this size
            actual_pages = min(pages_to_scrape, last_page_no)

            logging.info(
                f"{property_type.capitalize()} Listings: Scraping {actual_pages}/{last_page_no} page(s). Property specs: {size}")

            # Generate URLs for the specified number of pages
            property_sub_urls.extend(
                url_generator(page_no)
                for page_no in range(1, actual_pages + 1)
            )

        except Exception as e:
            logging.error(f"Error processing {property_type} - {size}: {e}")
            continue

    return property_sub_urls


# Create a global lock for file operations
file_lock = Lock()


def initialize_csv(file_path, fieldnames):
    """
    Initialize the CSV file with headers if it doesn't exist.

    Parameters:
    file_path (str): Path to the CSV file
    fieldnames (list): List of column names for the header
    """
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='UTF-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()


def write_to_file(response_dict, file_path):
    """
    Writes data to a CSV file in a thread-safe manner.

    Parameters:
    response_dict (dict): Dictionary containing the response data, where each value is a list
    file_path (str): Path to the CSV file where data should be written
    """
    # Initialize the CSV file with headers if it doesn't exist
    initialize_csv(file_path, list(response_dict.keys()))

    # Convert single row to list format if needed
    if not isinstance(next(iter(response_dict.values())), list):
        response_dict = {k: [v] for k, v in response_dict.items()}

    # Create rows from the dictionary
    rows = [dict(zip(response_dict.keys(), values))
            for values in zip(*response_dict.values())]

    # Use a lock to ensure thread-safe writing
    with file_lock:
        with open(file_path, mode='a', newline='', encoding='UTF-8') as file:
            writer = csv.DictWriter(file, fieldnames=response_dict.keys())
            writer.writerows(rows)


def get_last_page_no(soup):
    # soup should contain the pagination
    last_page = soup.find("ul", class_="MuiBox-root css-1mkpgp4").findAll(
        "a", class_="MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-sizeMedium MuiPaginationItem-text MuiPaginationItem-circular MuiPaginationItem-page css-1m22sh4")[-1]
    if last_page is not None:
        last_page = last_page.text
        return last_page
    else:
        raise Exception("Error getting last page")


def get_listing_urls(page_url, property_type):
    """
    Open listing page and get all listings URLs
    Args:
        page_url:
        property_type:

    Returns:

    """
    soup = get_soup(page_url)
    record_list = soup.find("ul").find_all('li', class_="MuiGrid-root")
    listing_urls = []
    for record in record_list:
        detail_page = record.find("a",
                                  class_="MuiTypography-root")
        detail_page_url = base_url + detail_page.get("href") if detail_page is not None else None
        listing_urls.append(detail_page_url)

    # prepping the saved data dict
    property_type_list = [property_type for item in range(1, len(listing_urls) + 1)]  # same length as itemurl
    page_url_list = [page_url for i in range(1, len(listing_urls) + 1)]

    data_dict = {
        "page_url": page_url_list,
        "property_type": property_type_list,
        "listing_url": listing_urls
    }
    write_to_file(data_dict, input_dir / f'{property_type}_listing_urls.csv')
    # logging.info(f"Property {property_type}: Saved listing URLs to CSV file")


def parse_location(location):
    # Regular expression pattern to match:
    # "Street, City - District" or "City - District" or "City"
    pattern = r"^(.*?)(?:,\s*(.*?))?(?:\s*-\s*(.*))?$"
    match = re.match(pattern, location)

    if match:
        # Assign groups to variables
        part1 = match.group(1).strip() if match.group(1) else None
        part2 = match.group(2).strip() if match.group(2) else None
        part3 = match.group(3).strip() if match.group(3) else None

        # Determine the output based on the format
        if part2:  # Format: "Street, City" or "Street, City - District"
            return part1, part2, part3
        else:  # Format: "City - District" or "City"
            return None, part1, part3
    else:
        return None, None, None


def parse_area(areas_string):
    # Regular expression patterns to capture the area values and their units (m²)
    usable_area_pattern = r"Užitná plocha (\d+)\s*m²"
    built_up_area_pattern = r"Zastavěná plocha (\d+)\s*m²"
    total_area_pattern = r"Celková plocha (\d+)\s*m²"

    # Search for the usable area, built-up area, and total area
    usable_area_match = re.search(usable_area_pattern, areas_string)
    built_up_area_match = re.search(built_up_area_pattern, areas_string)
    total_area_match = re.search(total_area_pattern, areas_string)

    # Extract the values and return them with their units
    usable_area = int(usable_area_match.group(1)) if usable_area_match else None
    built_up_area = int(built_up_area_match.group(1)) if built_up_area_match else None
    total_area = int(total_area_match.group(1)) if total_area_match else None

    return usable_area, built_up_area, total_area


def parse_construction(text):
    if text is None:
        return None, None, None
    else:
        text_split = [i.strip() for i in text.split(',')]
        if len(text_split) == 3:
            construction_type = text_split[0]
            construction_status = text_split[1]
            floor_location = text_split[2]
            return construction_type, construction_status, floor_location
        else:
            return None, None, None


def get_element_attribute(soup, tag, class_name, attribute=None, base_url=None):
    """
    Generalized function to retrieve an attribute or text from an HTML element.

    Parameters:
    - soup: BeautifulSoup object containing the HTML content.
    - tag: The HTML tag to search for (e.g., 'a', 'div', 'img').
    - class_name: The class name to identify the element.
    - attribute: The attribute to retrieve (e.g., 'href', 'src'). If None, returns text.
    - base_url: Base URL to prepend if an attribute value needs a full URL. Default is None.

    Returns:
    - The attribute value (str), full URL (str) if base_url is provided, or element text (str).
      Returns None if the element or attribute is not found.
    """
    try:
        element = soup.find(tag, class_=class_name)
        if element:
            if attribute:  # Get the specified attribute
                value = element.get(attribute)
                if base_url and value:  # Prepend base_url if needed
                    return base_url + value
                return value
            else:  # Get text content
                return element.text.strip()
        return None
    except AttributeError:
        return None


def format_price(price):
    if price:
        return price.replace('\u200b', '').replace('\xa0', ' ').replace(' ', '').replace('Kč', '').strip()
    return None


def extract_footer_info(soup):
    footer = soup.find('div', class_="css-11wv1wc")
    if footer:
        keys = [i.text for i in footer.findAll('dt')]
        values = [i.text for i in footer.findAll('dd')]
        footer_dict = dict(zip(keys, values))
        date_inserted = "-".join([i.strip() for i in footer_dict.get("Vloženo:", "").split('.')])
        date_updated = "-".join([i.strip() for i in footer_dict.get("Upraveno:", "").split('.')])
        return {"date_inserted": date_inserted, "date_updated": date_updated}
    return {"date_inserted": None, "date_updated": None}


def extract_agent_info(soup, base_url):
    agent_info = soup.findAll('li', class_="css-yu7uzj")
    agent_info = [i.text for i in agent_info] if agent_info else []

    # Initialize variables
    phone1, phone2, email = None, None, None

    # Regex patterns
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'^\+?[0-9\s\-]{7,15}$'  # Matches international format (+) or local numbers with length 7-15

    # Process agent_info list
    for info in agent_info:
        if re.match(email_pattern, info):  # If it matches an email
            email = info
        elif re.match(phone_pattern, info):  # If it matches a phone number
            if phone1 is None:  # First phone
                phone1 = info
            elif phone2 is None:  # Second phone
                phone2 = info

    agent_name_contact_page = soup.find('a',
                                        class_="MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textSecondary"
                                               " MuiButton-sizeMedium MuiButton-textSizeMedium MuiButton-root MuiButton"
                                               "-text MuiButton-textSecondary MuiButton-sizeMedium MuiButton-textSizeMedium css-ny03lw")
    agent_name = agent_name_contact_page.text if agent_name_contact_page else None
    agent_url = base_url + agent_name_contact_page.get("href") if agent_name_contact_page else None

    agent_website = soup.find('a', class_="MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textSecondary "
                                          "MuiButton-sizeMedium MuiButton-textSizeMedium MuiButton-root MuiButton-text "
                                          "MuiButton-textSecondary MuiButton-sizeMedium MuiButton-textSizeMedium css-1vgywwe")
    agent_website = agent_website.get("href") if agent_website else None

    return {
        "agent_name": agent_name,
        "agent_url": agent_url,
        "agent_website": agent_website,
        "agent_email": email,
        "agent_phone1": phone1,
        "agent_phone2": phone2
    }


def scrape_listings(listing_url, property_type):
    try:
        soup = get_soup(listing_url)

        # Extract title and location
        listing_title_location = soup.find('h1').get_text(separator="\n").split("\n")
        listing_title = listing_title_location[0]
        listing_location = listing_title_location[1] if len(listing_title_location) > 1 else None

        # Parse location
        street, city, district = parse_location(listing_location) if listing_location else (None, None, None)

        # Extract image URL
        image_url = get_element_attribute(soup, 'img', "MuiBox-root css-emihra", "src")

        # Extract listing description
        listing_description = get_element_attribute(soup, 'div', "MuiBox-root css-zbebq3")

        # Parse listing information into a dictionary
        listing_values = [item.text for item in
                          soup.findAll('dd', class_="MuiTypography-root MuiTypography-body1 css-urnwfg")]
        listing_keys = [item.text for item in
                        soup.findAll('dt', class_="MuiTypography-root MuiTypography-body1 css-tm1g54")]
        listing_info_dict = dict(zip(listing_keys, listing_values))

        # Parse price
        price = listing_info_dict.get("Celková cena:", None) or listing_info_dict.get("Cena:", None)
        price = format_price(price)

        # Parse note on price and other fields
        note_on_price = listing_info_dict.get("Poznámka k ceně:", None)
        accessories = listing_info_dict.get("Příslušenství:", None)
        energy_intensity = listing_info_dict.get("Energetická náročnost:", None)
        construction = listing_info_dict.get("Stavba:", None)
        construction_type, construction_status, floor_location = parse_construction(construction) if construction else (
            None, None, None)
        infrastructure = listing_info_dict.get("Infrastruktura:", None)
        location_description = listing_info_dict.get("Lokalita:", None)
        ownership = listing_info_dict.get("Vlastnictví:", None)

        # Parse area details
        area = listing_info_dict.get("Plocha:", None)
        usable_area, built_up_area, total_area = parse_area(area) if area else (None, None, None)

        # Extract footer information
        footer_info = extract_footer_info(soup)

        # Extract agent information
        agent_info = extract_agent_info(soup, base_url)

        # Compile the scraped data
        scraped_data = {
            'dbq_prd_type': 'REAL-ESTATE-BASIC',
            "website_name": base_url,
            "competence_date": "DD-MM-YYYY",
            "listing_title": listing_title,
            "listing_description": listing_description,
            "property_type": property_type,
            "country_code": 203,
            "location_description": location_description,
            "location_long": listing_location,
            "location_city": city,
            "location_region": district,
            "location_street": street,
            "area_unit": "SQMT",
            "total_area": total_area,
            "usable_area": usable_area,
            "built_up_area": built_up_area,
            "amenities_list": accessories,
            "energy_intensity": energy_intensity,
            "construction": construction,
            "construction_type": construction_type,
            "construction_status": construction_status,
            "floor_location": floor_location,
            "listing_date": footer_info.get("date_inserted"),
            "listing_date_updated": footer_info.get("date_updated"),
            "currency_code": "CZK",
            "price": price,
            "note_on_price": note_on_price,
            "agent_name": agent_info.get("agent_name"),
            "agent_url": agent_info.get("agent_url"),
            "agent_website": agent_info.get("agent_website"),
            "agent_email": agent_info.get("agent_email"),
            "agent_phone1": agent_info.get("agent_phone1"),
            "agent_phone2": agent_info.get("agent_phone2"),
            "image_url": f'https:{image_url}',
            "listing_url": listing_url
        }

        df = pd.DataFrame([scraped_data])
        scraped_file_dict = df.to_dict(orient='list')

        write_to_file(scraped_file_dict, output_dir / f"{property_type}.csv")
        logging.info(f"Property {property_type}: Scraped listing {listing_url} Successfully")
    except Exception as e:
        logging.error(f"Property {property_type}: Error scraping URL: {listing_url}")


def listing_urls_scraper(property_type):

    file_path = input_dir / f"{property_type}_page_urls.csv"
    if not os.path.isfile(file_path):
        # logging.error(f"{property_type}_page_urls.csv NOT found in input dir")
        property_page_urls = get_property_page_urls(property_type)
        data = {
            "property_page_url": property_page_urls
        }
        write_to_file(data, input_dir / f"{property_type}_page_urls.csv")
        # logging.info(f"page_urls.csv SAVED to input directory")

    df = pd.read_csv(file_path)
    total_page_urls = df["property_page_url"].to_list()

    # check if item url have been scraped
    listing_urls_path = input_dir / f"{property_type}_listing_urls.csv"
    if os.path.isfile(listing_urls_path):
        # logging.info(f"{property_type}_listing_urls.csv found in input directory")
        df = pd.read_csv(listing_urls_path)
        scraped_page_url = df["page_url"].to_list()
        remaining_page_urls = list(set(total_page_urls) - set(scraped_page_url))

    else:
        remaining_page_urls = total_page_urls
    logging.info(f"Property {property_type}: Scraping listing URLs from page(s)...")
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(get_listing_urls, page_url, property_type) for page_url in remaining_page_urls]
        for future in tqdm(futures, desc="Scraping listing URLs"):
            try:
                future.result()
            except Exception:
                continue

    os.remove(file_path)
    logging.info(f"Property {property_type}: Scraping listing URLs from page(s) completed!")

