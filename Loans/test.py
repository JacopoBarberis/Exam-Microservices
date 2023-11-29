import unittest
import requests

class TestLoanAPI(unittest.TestCase):

    def test_create_loan(self):
        response = requests.post('http://localhost:7778/create', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json={'book_id': 23})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json={'username': '23'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json={'book_id': -1, 'username': 'hsrthdfhsf'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Libro non trovato')

        response = requests.post('http://localhost:7778/create', json={'book_id': 1, 'username': 'hsrthdfhsf'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Utente non trovato')

        response = requests.post('http://localhost:7778/create', json={'book_id': 1, 'username': 'Mario'})
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json(), dict)

    def test_get_loan_by_id(self):
        response = requests.get('http://localhost:7778/loan/123456789')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Prestito non trovato')

        response = requests.get('http://localhost:7778/loan/1')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_return_book(self):
        response = requests.put('http://localhost:7778/return/20')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Prestito non trovato')

        response = requests.put('http://localhost:7778/return/1')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_delete_loan(self):
        response = requests.delete('http://localhost:7778/delete/123')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Prestito non trovato')

        response = requests.delete('http://localhost:7778/delete/1')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)


if __name__ == '__main__':
    unittest.main()
