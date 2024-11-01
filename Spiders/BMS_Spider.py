import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Function to get product URLs from the search results page
def get_product_urls_bmsmena(search_query, max_pages=5):
    base_url = f'https://bmsmena.com/search?type=product&options%5Bunavailable_products%5D=last&options%5Bprefix%5D=none&q={search_query}'
    product_urls = []
    
    for page in range(1, max_pages + 1):
        url = base_url + f'&page={page}'
        print(f'Scraping URLs from page {page}: {url}')
        
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product links
        product_containers = soup.find_all('div', class_='product-collection__title')
        
        if not product_containers:
            print("No products found on this page. Stopping pagination.")
            break  # Stop if no products are found
        
        for container in product_containers:
            link_tag = container.find('a')
            if link_tag and 'href' in link_tag.attrs:
                product_url = "https://bmsmena.com" + link_tag['href']
                product_urls.append(product_url)
        
        time.sleep(1)  # Pause to avoid overloading the server
    
    return product_urls

# Function to scrape details from a single product page
def scrape_product_details_bmsmena(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract Product Name
    name_tag = soup.find('h4')
    product_name = name_tag.get_text(strip=True) if name_tag else "N/A"
    
    # Extract Price
    price_tag = soup.find('span', id='js-product-price')
    product_price = price_tag.get_text(strip=True) if price_tag else "N/A"
    
    # Extract Image URL
    image_tag = soup.find('img', class_='main-image')
    image_url = "https:" + image_tag['data-zoom-image'] if image_tag and 'data-zoom-image' in image_tag.attrs else "N/A"
    
    return {
        'Product Name': product_name,
        'Price (JD)': product_price,
        'Image URL': image_url,
        'Product URL': url
    }

# Main function to scrape multiple products and save them to a unified CSV file
def scrape_multiple_products_bmsmena(search_query, max_pages=5):
    product_urls = get_product_urls_bmsmena(search_query, max_pages)
    all_products = []
    
    for url in product_urls:
        print(f'Scraping product details from: {url}')
        product_info = scrape_product_details_bmsmena(url)
        all_products.append(product_info)
        time.sleep(1)  # Pause to avoid overloading the server
    
    # Save data to a unified CSV file that overwrites existing files
    scraped_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scraped_Data'))  # Path to the Scraped_Data folder
    os.makedirs(scraped_data_dir, exist_ok=True)  # Create the folder if it doesn't exist
    csv_filename = os.path.join(scraped_data_dir, 'BMSproducts.csv')
    
    df = pd.DataFrame(all_products)
    df.to_csv(csv_filename, index=False)
    print(f'Scraped {len(all_products)} products and saved to {csv_filename}')

def CrawlBMS(term,pages = 1):
    search_query = term # Example search term
    max_pages = pages  # Set the maximum number of pages to scrape
    scrape_multiple_products_bmsmena(search_query, max_pages)
