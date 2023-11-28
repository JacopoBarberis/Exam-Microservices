import unittest
import requests

class Tests(unittest.TestCase):

    def check_customer_existing(self):

        response = requests.post('http://localhost:7778/create', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json = {'book_id':23})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json = {'username':'23'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Devi compilare tutti i campi')

        response = requests.post('http://localhost:7778/create', json = {'book_id':-1,'username':'hsrthdfhsf'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Libro non trovato')

        response = requests.post('http://localhost:7778/create', json = {'book_id':1,'username':'hsrthdfhsf'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, 'Utente non trovato')

        response = requests.post('http://localhost:7778/create', json = {'book_id':1,'username':'Mario'})
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json(), list)

        


