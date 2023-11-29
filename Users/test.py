import unittest
import requests

class TestUserAPI(unittest.TestCase):

    def test_get_users(self):
        response = requests.get('http://localhost:9898/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_user(self):
        response = requests.get('http://localhost:9898/users/username')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_create_user(self):
        response = requests.post('http://localhost:9898/register', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Please provide a valid JSON")

        response = requests.post('http://localhost:9898/register', json={'Nome': 'John', 'Cognome': 'Doe', 'Username': 'johndoe', 'Email': 'john@example.com', 'Password': 'password', 'DataNascita': '1990-01-01'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "User John Doe created successfully")

    def test_delete_user(self):
        response = requests.delete('http://localhost:9898/delete/username')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'User with User username not found')

    def test_update_user(self):
        response = requests.put('http://localhost:9898/update/username', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Please provide a valid JSON")

        response = requests.put('http://localhost:9898/update/username', json={'Nome': 'Updated', 'Cognome': 'User', 'Email': 'updated@example.com', 'Password': 'updatedpassword', 'DataNascita': '1995-01-01'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "User Updated User updated successfully")

if __name__ == '__main__':
    unittest.main()
