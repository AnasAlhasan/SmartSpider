import pandas as pd
import re
import os
from difflib import get_close_matches
from sklearn.impute import SimpleImputer
from sklearn.ensemble import IsolationForest
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from sklearn.cluster import KMeans

# Define the folder path containing the CSV files
FOLDER_PATH = r"C:\Users\alhas\Desktop\Smart Web Spider\SmartSpider\Scraped_Data"
OUTPUT_FILE_NAME = "cleaned_combined_data.csv"

# Predefined list of known brands for normalization
KNOWN_BRANDS = ['Samsung', 'LG', 'Sony', 'Panasonic', 'Toshiba', 'Philips', 'Hisense', 'Sharp']

def clean_text(text):
    """Clean and preprocess text by removing unwanted characters and handling empty values."""
    return text.strip().title() if pd.notna(text) and text != '' else ''

def correct_brand(brand):
    """Correct brand names based on a predefined list of known brands."""
    brand = clean_text(brand)
    if brand:
        matches = get_close_matches(brand, KNOWN_BRANDS, n=1, cutoff=0.7)
        return matches[0] if matches else brand
    return ''

def clean_price(price):
    """Clean and normalize the price by removing non-numeric characters."""
    try:
        return float(re.sub(r'[^0-9.]', '', str(price))) if pd.notna(price) and price != '' else float('nan')
    except ValueError:
        return float('nan')

def clean_url(url):
    """Clean and validate the product URL and image URL by removing unwanted characters or spaces."""
    return url.strip() if pd.notna(url) and url != '' else ''

def infer_missing_category(title):
    """Infer category from the title if the category is missing."""
    title_lower = title.lower()
    if 'tv' in title_lower:
        return 'Television'
    elif any(term in title_lower for term in ['fridge', 'refrigerator']):
        return 'Refrigerator'
    elif any(term in title_lower for term in ['washer', 'washing machine']):
        return 'Washing Machine'
    else:
        return 'Other'

def correct_common_errors(text):
    """Correct common typos and errors in text fields."""
    corrections = {'lG': 'LG', 'Sonyy': 'Sony'}
    return corrections.get(text, text)

def sentiment_analysis(text):
    """Perform sentiment analysis on text data."""
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def outlier_detection(df, column):
    """Detect and handle outliers in the price column using Isolation Forest."""
    iso = IsolationForest(contamination=0.1)
    yhat = iso.fit_predict(df[[column]])
    mask = yhat != -1
    df = df[mask]
    return df

def feature_engineering(df):
    """Create new features from existing data."""
    df['price_log'] = np.log1p(df['price'])
    return df

def clustering(df):
    """Perform KMeans clustering to group similar products."""
    kmeans = KMeans(n_clusters=3)
    df['cluster'] = kmeans.fit_predict(df[['price', 'price_log']])
    return df

def preprocess_row(row):
    """Preprocess a single row by cleaning all columns as needed."""
    title = clean_text(row.get('title', ''))
    model = clean_text(row.get('model', ''))
    brand = correct_brand(row.get('brand', ''))
    category = clean_text(row.get('category', '')) or infer_missing_category(title)
    price = clean_price(row.get('price', ''))
    product_url = clean_url(row.get('product_url', ''))
    image_url = clean_url(row.get('image_url', ''))
    store = clean_text(row.get('store', ''))

    # Apply common error corrections
    title = correct_common_errors(title)
    brand = correct_common_errors(brand)

    # Perform sentiment analysis on the title
    sentiment = sentiment_analysis(title)

    return {
        'title': title,
        'model': model,
        'brand': brand,
        'category': category,
        'price': price,
        'product_url': product_url,
        'image_url': image_url,
        'store': store,
        'sentiment': sentiment
    }

def clean_and_combine(files):
    """Read and combine data from multiple CSV files, then clean the data."""
    all_data = []

    for file_name in files:
        file_path = os.path.join(FOLDER_PATH, file_name)
        print(f"Processing file: {file_name}...")

        try:
            # Load the data
            data = pd.read_csv(file_path)

            # Standardize column names
            data.columns = [col.strip().lower().replace(" ", "_") for col in data.columns]

            # Drop duplicates
            data.drop_duplicates(inplace=True)

            # Apply preprocessing to each row
            cleaned_data = data.apply(preprocess_row, axis=1).tolist()
            all_data.extend(cleaned_data)

        except Exception as e:
            print(f"Error reading or processing {file_name}: {e}")

    combined_df = pd.DataFrame(all_data)

    # Handle missing values with imputer
    imputer = SimpleImputer(strategy='most_frequent')
    combined_df[['title', 'model', 'brand', 'category', 'product_url', 'image_url', 'store']] = imputer.fit_transform(combined_df[['title', 'model', 'brand', 'category', 'product_url', 'image_url', 'store']])
    price_imputer = SimpleImputer(strategy='median')
    combined_df[['price']] = price_imputer.fit_transform(combined_df[['price']])

    # Outlier detection in the price column
    combined_df = outlier_detection(combined_df, 'price')

    # Feature engineering
    combined_df = feature_engineering(combined_df)

    # Clustering
    combined_df = clustering(combined_df)

    # Data profiling
    print(f"Total records: {len(combined_df)}")
    print(f"Missing values:\n{combined_df.isna().sum()}")

    # Visualizations
    sns.histplot(combined_df['price'].dropna(), kde=True)
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(FOLDER_PATH, 'price_distribution.png'))
    plt.show()

    sns.countplot(data=combined_df, x='category')
    plt.title('Category Distribution')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(FOLDER_PATH, 'category_distribution.png'))
    plt.show()

    sns.scatterplot(data=combined_df, x='price', y='price_log', hue='cluster', palette='viridis')
    plt.title('Price Clusters')
    plt.xlabel('Price')
    plt.ylabel('Log of Price')
    plt.savefig(os.path.join(FOLDER_PATH, 'price_clusters.png'))
    plt.show()

    return combined_df

def process_and_save():
    """Process multiple CSV files in the folder, clean them, and save the combined result."""
    output_file = os.path.join(FOLDER_PATH, OUTPUT_FILE_NAME)

    # List of CSV files in the folder to be processed
    csv_files = [
        "BMSproducts.csv",
        "DiamondStarProducts.csv",
        "LGVisionProducts.csv",
        "SmartBuyProducts.csv"
    ]

    cleaned_data = clean_and_combine(csv_files)

    if not cleaned_data.empty:
        # Ensure all required columns are present and in the correct order
        required_columns = ['title', 'model', 'brand', 'category', 'price', 'price_log', 'image_url', 'product_url', 'store', 'sentiment', 'cluster']
        for col in required_columns:
            if col not in cleaned_data.columns:
                cleaned_data[col] = ''

        cleaned_data = cleaned_data[required_columns]

        cleaned_data.to_csv(output_file, index=False)
        print(f"Cleaned data saved to {output_file}")
    else:
        print("No data to save. Please check the input files.")

