from flask import Flask, request, jsonify
from run_spiders import RunSpiders
from data_processing import process_and_save
from database_setup import db, Product
import os
from sqlalchemy import func, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def clear_database():
    try:
        # Delete products where saved is False or saved is null
        rows_to_delete = db.session.query(Product).filter(
            or_(Product.saved == False, Product.saved == None)
        )
        num_rows_deleted = rows_to_delete.delete(synchronize_session=False)  # Optimized deletion
        db.session.commit()
        print(f"Deleted {num_rows_deleted} rows from the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to clear database: {e}")


@app.route('/api/scrape', methods=['POST'])
def run_scraper():
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

@app.route('/api/products', methods=['GET'])
def get_products():
    query = request.args.get('query', '').strip().lower()
    products_query = Product.query
    if query:
        products_query = products_query.filter(
            func.lower(Product.search_query).contains(query)
        )
    products = products_query.all()
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

@app.route('/api/saved_products', methods=['GET'])
def get_saved_products():
    saved_products = Product.query.filter_by(saved=True).order_by(Product.timestamp.desc()).all()
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
            "store": product.store,
            "timestamp": product.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
        }
        for product in saved_products
    ]
    return jsonify(results)

@app.route('/api/save_product', methods=['POST'])
def save_product():
    data = request.json
    product = Product.query.get(data.get('id'))
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    try:
        product.saved = True
        db.session.commit()
        return jsonify({"status": "success", "message": "Product saved successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete_saved_product/<int:product_id>', methods=['DELETE'])
def delete_saved_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    try:
        product.saved = False
        db.session.commit()
        return jsonify({"status": "success", "message": "Product unsaved successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    if os.path.exists('products.db'):
        os.remove('products.db')
    
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
