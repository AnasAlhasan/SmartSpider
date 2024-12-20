import pandas as pd
import re
from flask import Flask
import os
from difflib import get_close_matches
from sklearn.impute import SimpleImputer
from flask_sqlalchemy import SQLAlchemy

# Define the folder path containing the CSV files
FOLDER_PATH = r"C:\Users\alhas\Desktop\Smart Web Spider\SmartSpider\Scraped_Data"
OUTPUT_FILE_NAME = "cleaned_combined_data.csv"

# Predefined list of known brands for normalization
KNOWN_BRANDS = ['Samsung', 'LG', 'Sony', 'Panasonic', 'Toshiba', 'Philips', 'Hisense', 'Sharp']

# Initialize the Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    model = db.Column(db.String(255))
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    product_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    store = db.Column(db.String(100))
    search_query = db.Column(db.String(255))  # Add search_query column

# Helper functions for cleaning and normalization
def clean_text(text):
    return text.strip().title() if pd.notna(text) and text != '' else 'N/A'

def correct_brand(brand):
    brand = clean_text(brand)
    if brand != 'N/A':
        matches = get_close_matches(brand, KNOWN_BRANDS, n=1, cutoff=0.7)
        return matches[0] if matches else brand
    return 'N/A'

def clean_price(price):
    try:
        return float(re.sub(r'[^0-9.]', '', str(price))) if pd.notna(price) and price != '' else float('nan')
    except ValueError:
        return float('nan')

def clean_url(url):
    return url.strip() if pd.notna(url) and url != '' else 'N/A'

def preprocess_row(row, query):
    title = clean_text(row.get('title', 'N/A'))
    model = clean_text(row.get('model', 'N/A'))
    brand = correct_brand(row.get('brand', 'N/A'))
    category = clean_text(row.get('category', 'N/A'))
    price = clean_price(row.get('price', ''))
    product_url = clean_url(row.get('product_url', 'N/A'))
    image_url = clean_url(row.get('image_url', 'N/A'))
    store = clean_text(row.get('store', 'N/A'))
    search_query = query.lower() if query else 'n/a'
    processed_row = {
        'title': title,
        'model': model,
        'brand': brand,
        'category': category,
        'price': price,
        'product_url': product_url,
        'image_url': image_url,
        'store': store,
        'search_query': search_query  # Include search query
    }
    print(f"Processed Row: {processed_row}")  # Debugging
    return processed_row

# Function to clean and combine data from multiple files
def clean_and_combine(files, query):
    all_data = []
    for file_name in files:
        file_path = os.path.join(FOLDER_PATH, file_name)
        print(f"Processing file: {file_name}...")
        try:
            data = pd.read_csv(file_path)
            data.columns = [col.strip().lower().replace(" ", "_") for col in data.columns]
            data.drop_duplicates(inplace=True)
            # Ensure all required columns exist in the DataFrame
            required_columns = ['title', 'model', 'brand', 'category', 'price', 'product_url', 'image_url', 'store']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = 'N/A'
            cleaned_data = data.apply(lambda row: preprocess_row(row, query), axis=1).tolist()
            all_data.extend(cleaned_data)
        except Exception as e:
            print(f"Error reading or processing {file_name}: {e}")

    combined_df = pd.DataFrame(all_data)
    # Ensure all required columns exist in the combined DataFrame
    required_columns = ['title', 'model', 'brand', 'category', 'price', 'product_url', 'image_url', 'store', 'search_query']
    for col in required_columns:
        if col not in combined_df.columns:
            combined_df[col] = 'N/A'

    # Impute missing values
    imputer = SimpleImputer(strategy='most_frequent')
    combined_df[['title', 'model', 'brand', 'category', 'product_url', 'image_url', 'store', 'search_query']] = imputer.fit_transform(
        combined_df[['title', 'model', 'brand', 'category', 'product_url', 'image_url', 'store', 'search_query']]
    )
    price_imputer = SimpleImputer(strategy='median')
    combined_df[['price']] = price_imputer.fit_transform(combined_df[['price']])
    
    return combined_df

# Main function to process and save data
def process_and_save(query):
    # Ensure database tables are created
    with app.app_context():
        db.create_all()
    
    csv_files = ["BMSproducts.csv", "DiamondStarProducts.csv", "LGVisionProducts.csv", "SmartBuyProducts.csv"]
    cleaned_data = clean_and_combine(csv_files, query)
    
    if not cleaned_data.empty:
        required_columns = ['title', 'model', 'brand', 'category', 'price', 'product_url', 'image_url', 'store', 'search_query']
        cleaned_data = cleaned_data[required_columns]
        output_file = os.path.join(FOLDER_PATH, OUTPUT_FILE_NAME)
        cleaned_data.to_csv(output_file, index=False)
        
        # Save to database
        with app.app_context():
            for _, row in cleaned_data.iterrows():
                product = Product.query.filter_by(product_url=row['product_url']).first()
                if product:
                    product.title = row['title']
                    product.model = row['model']
                    product.brand = row['brand']
                    product.category = row['category']
                    product.price = row['price']
                    product.image_url = row['image_url']
                    product.store = row['store']
                    product.search_query = row['search_query']  # Update search_query field
                else:
                    product = Product(
                        title=row['title'],
                        model=row['model'],
                        brand=row['brand'],
                        category=row['category'],
                        price=row['price'],
                        product_url=row['product_url'],
                        image_url=row['image_url'],
                        store=row['store'],
                        search_query=row['search_query']  # Add search_query field
                    )
                    db.session.add(product)
            db.session.commit()
        print("Cleaned data saved to CSV and database")
    else:
        print("No data to save. Please check the input files.")


