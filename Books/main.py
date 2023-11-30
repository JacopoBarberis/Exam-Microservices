from flask import Flask, jsonify, request
import psycopg2
import pika
import logging
import time
import sys

log_file_path = 'app.log'

logging.basicConfig(filename=log_file_path, level=logging.DEBUG)
logger = logging.getLogger(__name__)

conn = psycopg2.connect(
    database="library",
    host="db-books",
    user="postgres_user",
    password="12345",
    port=5432
)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
cur = conn.cursor()


def log_execution_time(start_time, operation_name):
    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f'{operation_name} executed. Execution time: {execution_time:.4f} seconds')


@app.route('/', methods=['GET'])
def index():
    start_time = time.time()
    cur.execute('SELECT * FROM book')
    data = cur.fetchall()
    log_execution_time(start_time, 'index')
    return jsonify(data)


@app.route('/get/<id>', methods=['GET'])
def get_book(id):
    start_time = time.time()
    cur.execute('SELECT * FROM book WHERE ID = %s', (id,))
    data = cur.fetchone()

    if data:
        end_time = time.time()
        log_execution_time(start_time, f'get_book for ID {id}')
        return jsonify(data), 200
    else:
        end_time = time.time()
        log_execution_time(start_time, f'get_book for ID {id}')
        return jsonify({"message": f"No book found with ID {id}"}), 404


@app.route('/check_availability/<book_id>', methods=['GET'])
def check_availability(book_id):
    start_time = time.time()
    cur.execute('SELECT * FROM item WHERE book_id = %s AND isDisponibile = True;', (book_id,))
    data = cur.fetchone()

    if data:
        log_execution_time(start_time, f'check_availability for book_id {book_id}')
        return jsonify(data)
    else:
        log_execution_time(start_time, f'check_availability for book_id {book_id}')
        return jsonify({"message": f"No available items for book with ID {book_id}"})


@app.route('/items', methods=['GET'])
def get_items():
    start_time = time.time()
    cur.execute('SELECT * FROM item')
    data = cur.fetchall()
    log_execution_time(start_time, 'get_items')
    return jsonify(data)


@app.route('/create', methods=['POST'])
def create_book():
    start_time = time.time()
    data = request.get_json()

    required_fields = ['ISBN', 'Titolo', 'Autore', 'Genere', 'Anno']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"Errore": f"Il campo '{field}' è obbligatorio e non può essere vuoto."}), 400

    isbn, titolo, autore, genere, anno = (data[field] for field in required_fields)

    cur.execute(
        'INSERT INTO book(ISBN, Titolo, Autore, Genere, Anno) VALUES (%s, %s, %s, %s, %s);',
        (isbn, titolo, autore, genere, anno)
    )
    conn.commit()

    log_execution_time(start_time, 'create_book')
    return jsonify({"Messaggio": "Dati inseriti correttamente"}, 201)


@app.route('/create_item', methods=['POST'])
def create_item():
    start_time = time.time()
    data = request.get_json()
    required_fields = ['book_id']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"Errore": f"Il campo '{field}' è obbligatorio e non può essere vuoto."}), 400

    book_id = data['book_id']

    cur.execute('SELECT 1 FROM book WHERE id = %s;', (book_id,))
    if not cur.fetchone():
        return jsonify({"Errore": f"ID del libro '{book_id}' non trovato nella tabella book."}), 404

    cur.execute('INSERT INTO item(book_id) VALUES (%s);', (book_id,))
    conn.commit()

    log_execution_time(start_time, 'create_item')
    return jsonify({"Messaggio": "Dati inseriti correttamente"}, 201)


@app.route('/delete/<id>', methods=['DELETE'])
def delete_book(id):
    start_time = time.time()
    cur.execute('DELETE FROM book WHERE id = %s;', (id,))
    conn.commit()

    log_execution_time(start_time, f'delete_book for ID {id}')
    if cur.rowcount > 0:
        return jsonify({'message': f'Book with the ID {id} deleted successfully'}, 200)
    else:
        return jsonify({'messagge': f'Book with ID {id} not found'}, 404)


@app.route('/delete-item/<id>', methods=['DELETE'])
def delete_item(id):
    start_time = time.time()
    cur.execute('DELETE FROM item WHERE id = %s;', (id,))
    conn.commit()

    log_execution_time(start_time, f'delete_item for ID {id}')
    if cur.rowcount > 0:
        return jsonify({'message': f'Item with the ID {id} deleted successfully'}, 200)
    else:
        return jsonify({'messagge': f'Item with ID {id} not found'}, 404)


@app.route('/update/<id>', methods=['PUT'])
def update_book(id):
    start_time = time.time()
    up_data = request.get_json()
    up_Isbn, up_Titolo, up_Autore, up_Genere, up_Anno = (
        up_data['ISBN'], up_data['Titolo'], up_data['Autore'], up_data['Genere'], up_data['Anno']
    )

    cur.execute(
        f'UPDATE book SET ISBN = %s, Titolo = %s, Autore = %s, Genere = %s, Anno = %s WHERE id ={id};',
        (up_Isbn, up_Titolo, up_Autore, up_Genere, up_Anno)
    )
    conn.commit()

    log_execution_time(start_time, f'update_book for ID {id}')
    if cur.rowcount > 0:
        return jsonify({'messagge': f'Book with ID {id} updated successfully'})
    else:
        return jsonify({'messagge': f'Book with ID {id} not found'})


@app.route('/set_availability/<item_id>', methods=['PUT'])
def set_availability_true(item_id):
    start_time = time.time()
    cur.execute('UPDATE item SET isDisponibile = NOT isDisponibile WHERE id = %s', item_id)
    conn.commit()

    log_execution_time(start_time, f'set_availability for item_id {item_id}')
    return 'Disponibilità cambiata con successo', 200


@app.route('/update-item/<id>', methods=['PUT'])
def update_item(id):
    start_time = time.time()
    up_data = request.get_json()
    up_book_id, up_status_libro = up_data['book_id'], up_data['stato_libro']

    cur.execute(
        f'UPDATE item SET book_id=%s, stato_libro=%s WHERE id ={id};',
        (up_book_id, up_status_libro)
    )
    conn.commit()

    log_execution_time(start_time, f'update_item for ID {id}')
    if cur.rowcount > 0:
        return jsonify({'messagge': f'Item with ID {id} updated successfully'})
    else:
        return jsonify({'messagge': f'Item with ID {id} not found'})


if __name__ == '__main__':
    with conn.cursor() as cursor:
        cursor.execute(open('database/books.sql', 'r').read())
        conn.commit()
    with conn.cursor() as cursor:
        cursor.execute(open('database/insert.sql', 'r').read())
        conn.commit()

    app.run(host='0.0.0.0', port=5000, debug=True)
