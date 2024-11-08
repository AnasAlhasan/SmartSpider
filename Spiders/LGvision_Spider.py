import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to get product URLs from the search results page
def get_product_urls_newvision(search_query, max_pages=5):
    base_url = f'https://newvision.jo/en/?post_type=product&s={search_query}&asp_active=1&p_asid=1&p_asp_data=1&filters_initial=1&filters_changed=0&wpml_lang=en&qtranslate_lang=0&woo_currency=JOD&current_page_id=16460'
    product_urls = []
    
    for page in range(1, max_pages + 1):
        url = base_url + f'&paged={page}'
        print(f'Scraping URLs from page {page}: {url}')
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product links
        product_containers = soup.find_all('h3', class_='wd-entities-title')
        
        if not product_containers:
            print("No products found on this page. Stopping pagination.")
            break  # Stop if no products are found
        
        for container in product_containers:
            link_tag = container.find('a')
            if link_tag and 'href' in link_tag.attrs:
                product_url = link_tag['href']
                product_urls.append(product_url)
        
        time.sleep(1)  # Pause to avoid overloading the server
    
    return product_urls

# Function to scrape details from a single product page
def scrape_product_details_newvision(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract Product Title
    title_tag = soup.find('h3', class_='wd-entities-title')
    product_title = title_tag.get_text(strip=True) if title_tag else "N/A"
    
    # Extract Product Model
    model_tag = soup.find('span', class_='sku')
    product_model = model_tag.get_text(strip=True) if model_tag else "N/A"
    
    # Extract Price
    price_tag = soup.find('p', class_='price pewc-main-price')
    if not price_tag:
        price_tag = soup.find('span', class_='woocommerce-Price-amount')
    
    if price_tag:
        price_text = price_tag.get_text(strip=True)
        if "Current price is:" in price_text:
            # Extract the current price only
            product_price = price_text.split("Current price is:")[-1].split('JOD')[0].strip()
        else:
            product_price = price_text
    else:
        product_price = "N/A"
    
    # Extract Product Category
    category_tag = soup.find('span', class_='posted_in')
    product_category = ', '.join([a.get_text(strip=True) for a in category_tag.find_all('a')]) if category_tag else "N/A"
    
    # Extract Image URL
    image_tag = soup.find('a', {'data-elementor-open-lightbox': 'no'})
    image_url = image_tag['href'] if image_tag and 'href' in image_tag.attrs else "N/A"
    
    brand = 'LG'
    
    return {
        'Title': product_title,
        'Model': product_model,
        'Brand': brand,
        'Category': product_category,
        'Price': product_price,
        'Product URL': url,
        'Image URL': image_url
    }

# Main function to scrape multiple products and save them to a unified CSV file
def scrape_multiple_products_newvision(search_query, max_pages=5):
    product_urls = get_product_urls_newvision(search_query, max_pages)
    all_products = []
    
    for url in product_urls:
        print(f'Scraping product details from: {url}')
        product_info = scrape_product_details_newvision(url)
        all_products.append(product_info)
        time.sleep(1)  # Pause to avoid overloading the server

    # Create the directory if it doesn't exist
    scraped_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scraped_Data'))  # Path to the Scraped_Data folder
    os.makedirs(scraped_data_dir, exist_ok=True)  # Create the folder if it doesn't exist
    csv_filename = os.path.join(scraped_data_dir, 'LGVisionProducts.csv')
    df = pd.DataFrame(all_products)
    df.to_csv(csv_filename, index=False)
    print(f'Scraped {len(all_products)} products and saved to {csv_filename}')

def CrawlLGvision(term, pages=1):
    search_query = term  # Example search term
    max_pages = pages  # Set the maximum number of pages to scrape
    scrape_multiple_products_newvision(search_query, max_pages)
