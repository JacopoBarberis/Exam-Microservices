from flask import Flask, jsonify, request
import psycopg2
import requests
from datetime import datetime
import logging
import sys
import time
import pika

log_file_path = 'app.log'

logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

conn = psycopg2.connect(
    database="library-loans",
    host="db-loans",
    user="postgres_user",
    password="12345",
    port=5432
)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
cur = conn.cursor()

def log_execution_time(start_time, operation_name):
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f'{operation_name} executed. Execution time: {execution_time:.4f} seconds')

@app.route('/', methods=['GET'])
def index():
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM loan')
        data = cur.fetchall()
    return jsonify(data)

from flask import abort

@app.route('/loan/<id>', methods=['GET'])   
def get_loan(id):
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM loan WHERE id = %s', id)
        data = cur.fetchall()
        
        if not data:
            # Se non ci sono dati, restituisci un errore 404 Not Found
            return f"Prestito non trovato", 404
    
    return jsonify(data)


@app.route('/create', methods=['POST'])
def create_loan():
    start_time = time.time()
    data = request.get_json()
    required_fields = ['book_id','username']
    for field in required_fields:
        if field not in data:
            return 'Devi compilare tutti i campi', 400
    book_id = data['book_id']
    user_id = data['username']

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
    log_execution_time(start_time, 'create_loan')
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
        routing_key='hello',
        body=f'Prestito creato correttamente!!')
    connection.close()
    return jsonify({"Messagge":"Dati inseriti correttamente"}, 201)

@app.route('/return/<loan_id>', methods=['PUT'])
def return_book(loan_id):
    start_time = time.time()
    cur.execute('SELECT * FROM loan WHERE id = %s', loan_id)
    loan = cur.fetchone()
    cur.execute('SELECT book_id FROM loan WHERE id = %s', loan_id)
    book_id = cur.fetchone()
    if loan is None:
        return 'Prestito non trovato', 404
    cur.execute('UPDATE loan SET data_restituzione = %s where id = %s', (datetime.now(),loan_id))
    requests.put(f'http://api-books:5000/set_availability/{book_id}')
    conn.commit()
    log_execution_time(start_time, 'update_loan')
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
        routing_key='hello',
        body=f'Libro con ID {book_id} riconsegnato correttamente!!')
    connection.close()
    return jsonify({"Message": "Riconsegna effettuata correttamente"})

@app.route('/delete/<id>', methods=['DELETE'])
def delete_loan(id):

    with conn.cursor() as cur:
        # Verifica se il prestito esiste
        cur.execute('SELECT * FROM loan WHERE id = %s', id)
        existing_loan = cur.fetchone()

        if existing_loan is None:
            return 'Prestito non trovato', 404

        # Effettua la cancellazione del prestito
        cur.execute('DELETE FROM loan WHERE id = %s', id)

        # Aggiorna lo stato di disponibilità del libro
        cur.execute('SELECT book_id FROM loan WHERE id = %s', id)
        book_id = cur.fetchone()

        requests.put(f'http://api-books:5000/set_availability/{book_id}')

        conn.commit()

    return jsonify({"Message": "Prestito cancellato correttamente"})


if __name__ == '__main__':
    with conn.cursor() as cursor:
        cursor.execute(open('database/loans.sql', 'r').read())
    conn.commit()
    with conn.cursor() as cursor:
        cursor.execute(open('database/insert.sql', 'r').read())
    conn.commit()

    app.run(host='0.0.0.0', port=7778, debug=True)
