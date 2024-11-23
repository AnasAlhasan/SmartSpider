import pandas as pd
from transformers import pipeline, AutoTokenizer

# Define the folder path containing the CSV files
FOLDER_PATH = r"C:\Users\alhas\Desktop\Smart Web Spider\SmartSpider\Scraped_Data"
OUTPUT_FILE_NAME = "cleaned_data_with_transformers.csv"

# Load the text generation model from Hugging Face
text_generator = pipeline("text-generation", model="gpt2", framework="pt")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

def ai_clean_data(row):
    """
    Use a Hugging Face model to clean and preprocess data.
    """
    # Construct the prompt
    prompt = f"""
    Clean and preprocess this product data row: {row}.
    Fix invalid values, format the price properly, infer missing information, and standardize the output.
    """
    try:
        # Tokenize the prompt and ensure it's within the model's token limit
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Generate a cleaned response
        response = text_generator(prompt, max_new_tokens=100, num_return_sequences=1)
        cleaned_row = response[0]["generated_text"].strip()

        # Ensure the cleaned data is properly structured as a dictionary or list of values
        # Here, we assume the model outputs a single clean row, and we should convert it
        # back to a dictionary matching the original column names
        cleaned_row = cleaned_row.split(",")  # Example: Simple comma-based split, may need adjustment

        # Ensure that the cleaned row matches the original row length
        if len(cleaned_row) != len(row):
            raise ValueError(f"Mismatch in row length: {len(cleaned_row)} != {len(row)}")
        
        # Return the cleaned row as a dictionary matching original column names
        cleaned_row_dict = dict(zip(row.keys(), cleaned_row))
        return cleaned_row_dict

    except Exception as e:
        print(f"Error processing row with AI: {e}")
        return row  # Return original row if something fails

def clean_and_preprocess(file_path):
    """
    Clean and preprocess data from a CSV file.
    """
    try:
        # Load the data
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # Standardize column names
    data.columns = [col.strip().lower().replace(" ", "_") for col in data.columns]

    # Drop duplicates
    data = data.drop_duplicates()

    # Apply AI cleaning row by row
    cleaned_data = []
    for _, row in data.iterrows():
        row_dict = row.to_dict()
        cleaned_row = ai_clean_data(row_dict)
        cleaned_data.append(cleaned_row)

    # Convert cleaned data back to DataFrame
    cleaned_df = pd.DataFrame(cleaned_data, columns=data.columns)
    return cleaned_df

def process_and_save():
    """
    Process multiple CSV files in the specified folder, clean them with AI, and save the result.
    """
    output_file = f"{FOLDER_PATH}\\{OUTPUT_FILE_NAME}"
    
    # List of CSV files in the folder
    csv_files = [
        "BMSproducts.csv", 
        "DiamondStarProducts.csv", 
        "LeadersProducts.csv", 
        "LGVisionProducts.csv", 
        "SmartBuyProducts.csv"
    ]
    
    all_data = []
    
    # Process each file
    for file_name in csv_files:
        file_path = f"{FOLDER_PATH}\\{file_name}"
        print(f"Processing {file_name} with AI...")
        cleaned_data = clean_and_preprocess(file_path)
        if cleaned_data is not None:
            all_data.append(cleaned_data)
    
    # Combine all data
    if all_data:
        final_data = pd.concat(all_data, ignore_index=True)
        final_data.to_csv(output_file, index=False)
        print(f"AI-cleaned data saved to {output_file}")
    else:
        print("No data to save. Please check the input files.")


