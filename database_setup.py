from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    search_query = db.Column(db.String(255))  # New column for storing search query

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This will create the database and tables
        print("Database and tables created!")
