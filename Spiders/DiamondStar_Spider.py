import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Function to scrape product details from a single product page
def scrape_product_details_diamondstar(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract product title
    title_tag = soup.find('h1', class_='product_title wd-entities-title')
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    # Extract product model
    model_tag = soup.find('span', class_='sku')
    model = model_tag.get_text(strip=True) if model_tag else "N/A"

    # Extract product price
    price_tag = soup.find('p', class_='price')
    ins_price = price_tag.find('ins').find('span', class_='woocommerce-Price-amount amount') if price_tag.find('ins') else None
    price = ins_price.get_text(strip=True) if ins_price else price_tag.find('span', class_='woocommerce-Price-amount amount').get_text(strip=True)

    # Extract category (swapped with brand)
    category_tag = soup.find('a', rel='tag')
    category = category_tag.get_text(strip=True) if category_tag else "N/A"

    # Extract brand from title (assuming the first word in the title is the brand)
    brand = title.split()[0] if title else "N/A"

    # Extract image URL
    image_tag = soup.find('a', {'data-elementor-open-lightbox': 'no'})
    image_url = image_tag['href'] if image_tag else "N/A"

    return {
        'Title': title,
        'Model': model,
        'Brand': brand,
        'Category': category,
        'Price': price,
        'Product URL': url,
        'Image URL': image_url
    }

# Function to scrape product URLs from the search results page
def scrape_product_urls_diamondstar(search_query, max_pages):
    all_product_urls = []
    base_url = f'https://diamondstarjo.com/?s={search_query}&post_type=product'
    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url  # First page URL
        else:
            url = f'https://diamondstarjo.com/page/{page}?s={search_query}&post_type=product'  # Subsequent page URLs

        print(f'Scraping URLs from page {page}: {url}')
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all product links on the page
        product_links = soup.find_all('h3', class_='wd-entities-title')
        for link in product_links:
            a_tag = link.find('a')
            if a_tag and 'href' in a_tag.attrs:
                all_product_urls.append(a_tag['href'])

    return all_product_urls

# Function to scrape multiple products from Diamond Star
def scrape_multiple_products_diamondstar(search_query, max_pages):
    all_products = []
    product_urls = scrape_product_urls_diamondstar(search_query, max_pages)
    for url in product_urls:
        print(f'Scraping product details from: {url}')
        product_info = scrape_product_details_diamondstar(url)
        all_products.append(product_info)
    
    return all_products

# Main function to execute the scraping
def CrawlDiamondStar(term, pages=1):
    search_query = term  # Change this to any desired search term
    max_pages = pages  # Number of pages to scrape

    products = scrape_multiple_products_diamondstar(search_query, max_pages)
    # Save data to CSV, overwriting the existing file
    scraped_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scraped_Data'))  # Path to the Scraped_Data folder
    os.makedirs(scraped_data_dir, exist_ok=True)  # Create the folder if it doesn't exist
    output_file = os.path.join(scraped_data_dir, 'DiamondStarProducts.csv')  # Specify the new filename with path

    df = pd.DataFrame(products)
    df.to_csv(output_file, index=False)  # Use the full path here
    print(f'Scraped {len(products)} products and saved to {output_file}')  # Update the message to reflect the new file name
