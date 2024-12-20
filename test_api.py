import unittest
from app import app

class FlaskAPITest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_scrape(self):
        response = self.app.post(
            '/api/scrape',
            json={"query": "laptop"}
        )
        self.assertEqual(response.status_code, 200)
        print(response.json)

    def test_get_products(self):
        response = self.app.get('/api/products?query=laptop')
        self.assertEqual(response.status_code, 200)
        print(response.json)

    def test_get_product(self):
        response = self.app.get('/api/product/1')
        self.assertEqual(response.status_code, 200)
        print(response.json)

if __name__ == '__main__':
    unittest.main(verbosity=2)
