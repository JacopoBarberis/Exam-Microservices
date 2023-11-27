from flask import Flask, jsonify, request
import psycopg2
import requests
from datetime import datetime

app = Flask(__name__)

conn = psycopg2.connect(
    database="library-loans",
    host="db-loans",
    user="postgres_user",
    password="12345",
    port=5432
)

cur = conn.cursor()

@app.route('/', methods=['GET'])
def index():
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM loan')
        data = cur.fetchall()
    return jsonify(data)

@app.route('/loan/<id>', methods=['GET'])   
def get_loan(id):
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM loan WHERE id = %s', id)
        data = cur.fetchall()
    return jsonify(data)

@app.route('/create', methods=['POST'])
def create_loan():
    data = request.get_json()
    book_id = data['book_id']
    user_id = data['username']

    book = requests
    book = requests.get(f'http://api-books:5000//check_availability/{book_id}')
    if book.status_code == 404:
        return 'Libro non trovato', 404
    user = requests.get(f'http://api-users:9898/users/{user_id}')
    if user.status_code == 404:
        return 'Utente non trovato', 404
    
    cur.execute('INSERT INTO loan(book_id,user_id) VALUES (%s,%s);', (book_id,user_id))
    requests.put(f'http://api-books:5000/set_availability/{book_id}')
    #cur.execute(f'UPDATE item SET isDisponibile = False WHERE id = {book_id} ')
    conn.commit()
    return jsonify({"Messagge":"Dati inseriti correttamente"}, 201)

@app.route('/return/<loan_id>', methods=['PUT'])
def return_book(loan_id):
    cur.execute('SELECT * FROM loan WHERE id = %s', loan_id)
    loan = cur.fetchone()
    cur.execute('SELECT book_id FROM loan WHERE id = %s', loan_id)
    book_id = cur.fetchone()
    if loan is None:
        return 'Prestito non trovato', 404
    cur.execute('UPDATE loan SET data_restituzione = %s where id = %s', (datetime.now(),loan_id))
    requests.put(f'http://api-books:5000/set_availability/{book_id}')
    conn.commit()

    return jsonify({"Message": "Riconsegna effettuata correttamente"})


if __name__ == '__main__':
    with conn.cursor() as cursor:
        cursor.execute(open('database/loans.sql', 'r').read())
    conn.commit()
    with conn.cursor() as cursor:
        cursor.execute(open('database/insert.sql', 'r').read())
    conn.commit()

    app.run(host='0.0.0.0', port=7778, debug=True)
