import unittest
from app import app


class test_status_code(unittest.TestCase):
    # testing response
    def test_registration(self):
        test = app.test_client(self)
        response = test.get('/registration/')
        self.assertEqual(response.status_code, 404)

    def test_add_product(self):
        test = app.test_client(self)
        response = test.get('/add-product/')
        self.assertEqual(response.status_code, 404)

    def test_show_products(self):
        test = app.test_client(self)
        response = test.get('/show-products/')
        self.assertEqual(response.status_code, 200)

    def test_view_product(self):
        test = app.test_client(self)
        response = test.get('/view-product/1')
        self.assertEqual(response['status_code'], 200)


if __name__ == '__main__':
    unittest.main()
