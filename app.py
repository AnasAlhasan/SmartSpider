from flask import Flask, request, jsonify
from run_spiders import RunSpiders
from data_processing import process_and_save
from database_setup import db, Product
import os
from sqlalchemy import or_, func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def clear_database():
    try:
        num_rows_deleted = db.session.query(Product).delete()
        db.session.commit()
        print(f"Deleted {num_rows_deleted} rows from the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to clear database: {e}")

@app.route('/api/scrape', methods=['POST'])
def run_scraper():
    if request.method == 'POST':
        query = request.json.get('query', '').strip()
        if not query:
            return jsonify({"status": "error", "message": "No query provided."}), 400

        try:
            clear_database()  # Clear the database before scraping
            RunSpiders(query)
            process_and_save(query)
            return jsonify({"status": "success", "message": "Scraping and processing completed."})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error during scraping: {str(e)}"}), 500
    else:
        return jsonify({"status": "error", "message": "Invalid request method."}), 405

@app.route('/api/products', methods=['GET'])
def get_products():
    query = request.args.get('query', '').strip().lower()
    print(f"Query received: {query}")  # Debugging
    products_query = Product.query
    if query:
        products_query = products_query.filter(
            func.lower(Product.search_query).contains(query)
        )
    products = products_query.all()
    print(f"Products fetched: {len(products)}")  # Debugging
    for product in products:
        print(f"Fetched Product: {product.title} from {product.store}")  # Debugging
    results = [
        {
            "id": product.id,
            "title": product.title,
            "model": product.model,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "product_url": product.product_url,
            "image_url": product.image_url,
            "store": product.store
        }
        for product in products
    ]
    return jsonify(results)

@app.route('/api/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    result = {
        "id": product.id,
        "title": product.title,
        "model": product.model,
        "brand": product.brand,
        "category": product.category,
        "price": product.price,
        "product_url": product.product_url,
        "image_url": product.image_url,
        "store": product.store
    }
    return jsonify(result)

if __name__ == '__main__':
    if os.path.exists('products.db'):
        os.remove('products.db')
    
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
