import requests
from bs4 import BeautifulSoup
import pandas as pd 
import os

# Data storage for all products
all_products = []

# Function to scrape product details from an individual product page
def scrape_product_details_leaders(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    #title_tag = soup.find('h1', class_='woocommerce-loop-product__title') or soup.find('h1', class_='product_title entry-title')
    title_tag = soup.find('h1', class_='product_title entry-title')
    title = title_tag.get_text(strip=True) if title_tag else "N/A"
    
    # Extract price with multiple format options
    price_tag = soup.find('ins', class_='woocommerce-Price-amount') or soup.find('span', class_='woocommerce-Price-amount amount')
    price = price_tag.get_text(strip=True) if price_tag else "N/A"
    
    # Extract model
    model_tag = soup.find('span', string=lambda x: x and "Model Number:" in x)
    model = model_tag.find('strong').get_text(strip=True) if model_tag and model_tag.find('strong') else "N/A"
    
    # Extract brand
    brand = title.split()[0] if title else "N/A"
    
    # Extract image URL
    image_tag = soup.find('a', href=True)
    image_url = image_tag['href'] if image_tag else "N/A"
    
    # Return product information
    return {
        'Title': title,
        'Model': model,
        'Brand': brand,
        'Price': price,
        'Image URL': image_url,
        'Product URL': url,
        'Store': 'Leaders'
    }

# Function to scrape URLs of products from a search results page
def scrape_product_urls_leaders(search_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Collect product URLs (avoid duplicates by using a set)
    product_links = set()
    for a_tag in soup.find_all('a', class_='woocommerce-LoopProduct-link', href=True):
        product_links.add(a_tag['href'])
    
    return list(product_links)

# Main function to scrape multiple pages and store in a CSV
def scrape_multiple_products_leaders(search_term, max_pages):
    base_url = f'https://leaders.jo/en/?s={search_term}&post_type=product&dgwt_wcas=1&lang=en'
    
    for page in range(1, max_pages + 1):
        search_url = base_url if page == 1 else f'https://leaders.jo/en/page/{page}/?s={search_term}&post_type=product&dgwt_wcas=1&lang=en'
        
        product_urls = scrape_product_urls_leaders(search_url)
        for url in product_urls:
            product_info = scrape_product_details_leaders(url)
            all_products.append(product_info)
    
    # Save data to a unified CSV file that overwrites existing files
    scraped_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scraped_Data'))  # Path to the Scraped_Data folder
    os.makedirs(scraped_data_dir, exist_ok=True)  # Create the folder if it doesn't exist
    csv_filename = os.path.join(scraped_data_dir, 'LeadersProducts.csv')  # Correctly create the full path for the CSV

    df = pd.DataFrame(all_products)
    df.to_csv(csv_filename, mode='w', index=False, header=True)  # Use the full path here



def CrawlLeaders(term, pages = 1):
    search_term = term
    max_pages = pages
    scrape_multiple_products_leaders(search_term, max_pages)
