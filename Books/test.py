import unittest
import requests

class TestBookAPI(unittest.TestCase):

    def test_create_book(self):
        response = requests.post('http://localhost:5000/create', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'ISBN' è obbligatorio e non può essere vuoto.")

        response = requests.post('http://localhost:5000/create', json={'ISBN': '123'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'Titolo' è obbligatorio e non può essere vuoto.")

        response = requests.post('http://localhost:5000/create', json={'ISBN': '123', 'Titolo': 'Book Title'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'Autore' è obbligatorio e non può essere vuoto.")

        response = requests.post('http://localhost:5000/create', json={'ISBN': '123', 'Titolo': 'Book Title', 'Autore': 'Author'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'Genere' è obbligatorio e non può essere vuoto.")

        response = requests.post('http://localhost:5000/create', json={'ISBN': '123', 'Titolo': 'Book Title', 'Autore': 'Author', 'Genere': 'Genre'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'Anno' è obbligatorio e non può essere vuoto.")

    def test_delete_book(self):
        response = requests.delete('http://localhost:5000/delete/123')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['messagge'], 'Book with ID 123 not found')

        response = requests.delete('http://localhost:5000/delete/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Book with the ID 1 deleted successfully')

    def test_update_book(self):
        response = requests.put('http://localhost:5000/update/123', json={})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['messagge'], 'Book with ID 123 not found')

        response = requests.put('http://localhost:5000/update/1', json={'ISBN': '456', 'Titolo': 'Updated Title', 'Autore': 'Updated Author', 'Genere': 'Updated Genre', 'Anno': 2023})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['messagge'], 'Book with ID 1 updated successfully')

    def test_create_item(self):
        response = requests.post('http://localhost:5000/create_item', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["Errore"], "Il campo 'book_id' è obbligatorio e non può essere vuoto.")

        response = requests.post('http://localhost:5000/create_item', json={'book_id': 1})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["Errore"], "ID del libro '1' non trovato nella tabella book.")

        response = requests.post('http://localhost:5000/create_item', json={'book_id': 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["Messaggio"], "Dati inseriti correttamente")

    def test_delete_item(self):
        response = requests.delete('http://localhost:5000/delete-item/123')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['messagge'], 'Item with ID 123 not found')

        response = requests.delete('http://localhost:5000/delete-item/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'Item with the ID 1 deleted successfully')

    def test_update_item(self):
        response = requests.put('http://localhost:5000/update-item/123', json={})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['messagge'], 'Item with ID 123 not found')

        response = requests.put('http://localhost:5000/update-item/1', json={'book_id': 2, 'stato_libro': 'Updated Status'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['messagge'], 'Item with ID 1 updated successfully')

    def test_set_availability(self):
        response = requests.put('http://localhost:5000/set_availability/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'Disponibilità cambiata con successo')

        response = requests.put('http://localhost:5000/set_availability/123')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
