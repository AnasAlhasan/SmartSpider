import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

# Function to scrape product URLs from the search results page
def scrape_product_urls(search_url, max_pages):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    product_urls = []
    
    for page in range(1, max_pages + 1):
        if page == 1:
            url = search_url  # First page URL
        else:
            url = f"{search_url}&page={page}"  # Subsequent page URLs
        
        print(f"Scraping search results page {page}: {url}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product links on the page
        product_links = soup.find_all('a', class_='product-item__image-wrapper')
        
        for link in product_links:
            product_url = "https://smartbuy-me.com" + link['href']
            product_urls.append(product_url)
    
    return product_urls

# Function to scrape JSON-LD data from a product page
def scrape_json_ld(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the JSON-LD script in the page
    json_ld_tag = soup.find('script', type='application/ld+json')

    if json_ld_tag:
        try:
            # Parse the JSON data
            json_data = json.loads(json_ld_tag.string)
            
            # Extract product information from the JSON-LD structure
            product_info = {
                'Title': json_data.get('name', 'N/A'),
                'Model': json_data.get('offers', [{}])[0].get('name', 'N/A'),
                'Brand': json_data.get('brand', {}).get('name', 'N/A'),
                'Category': json_data.get('category', 'N/A'),
                'Price': json_data.get('offers', [{}])[0].get('price', 'N/A'),
                'Product URL': json_data.get('url', 'N/A'),
                'Image URL': json_data.get('image', {}).get('url', 'N/A')
            }
            
            return product_info
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print(f"No JSON-LD data found at {url}")
        return None

# Function to scrape multiple product pages
def scrape_multiple_products(search_url, max_pages):
    all_products = []
    
    # Step 1: Scrape all product URLs from the search results pages
    product_urls = scrape_product_urls(search_url, max_pages)
    
    print(f"Found {len(product_urls)} product URLs to scrape.")

    # Step 2: Scrape each product page for JSON-LD data
    for url in product_urls:
        print(f"Scraping product page: {url}")
        product_info = scrape_json_ld(url)
        if product_info:
            all_products.append(product_info)

    return all_products

def CrawlSmartBuy(term,pages = 1):
    search_query =  term
    max_pages = pages  # Number of search result pages to scrape
    search_url = f'https://smartbuy-me.com/search?type=product&q={search_query}'

    products = scrape_multiple_products(search_url, max_pages)

    # Save data to CSV
    scraped_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scraped_Data'))  # Path to the Scraped_Data folder
    os.makedirs(scraped_data_dir, exist_ok=True)  # Create the folder if it doesn't exist
    csv_filename = os.path.join(scraped_data_dir, 'SmartBuyProducts.csv')  # Specify the new filename

    df = pd.DataFrame(products)
    df.to_csv(csv_filename, index=False)  # Use the full path here
    print(f'Scraped {len(products)} products and saved to {csv_filename}')  # Update the message to reflect the new file name
