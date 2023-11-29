    
from flask import Flask, jsonify, request
import psycopg2
import pika

conn = psycopg2.connect(
    database = "library",
    host = "db-books",
    user = "postgres_user",
    password = "12345",
    port = 5432
)

app = Flask(__name__)

cur = conn.cursor()


@app.route('/', methods =['GET'])
def index():
    cur.execute('SELECT * FROM book')
    data = cur.fetchall()
    return jsonify(data)

@app.route('/get/<int:id>', methods=['GET'])
def get_book(id):
    cur.execute('SELECT * FROM book WHERE ID = %s', (id,))
    data = cur.fetchone()

    if data:

        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.queue_declare(queue='hello')

        channel.basic_publish(exchange='',
                            routing_key='hello',
                            body='Aggiunto libro con successo!!')
        connection.close()
        return jsonify(data), 200
    else:
        return jsonify({"message": f"No book found with ID {id}"}), 404

@app.route('/check_availability/<book_id>', methods=['GET'])
def check_availability(book_id):
    cur.execute('SELECT * FROM item WHERE book_id = %s AND isDisponibile = True;', (book_id,))
    data = cur.fetchone()
    if data is not None:
        return jsonify(data)
    else:
        return jsonify({"message": f"Nessun item disponibile per il libro con ID {book_id}"})

   

@app.route('/items', methods =['GET'])
def get_items():
    cur.execute('SELECT * FROM item')
    data = cur.fetchall()
    return jsonify(data)

@app.route('/create', methods=['POST'])
def create_book():
    # Ottieni i dati JSON dalla richiesta
    data = request.get_json()

    # Verifica se tutti i campi sono presenti e non vuoti
    required_fields = ['ISBN', 'Titolo', 'Autore', 'Genere', 'Anno']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"Errore": f"Il campo '{field}' è obbligatorio e non può essere vuoto."}), 400

    # Estrai i dati
    isbn = data['ISBN']
    Titolo = data['Titolo']
    Autore = data['Autore']
    Genere = data['Genere']
    Anno = data['Anno']

    # Esegui l'inserimento nel database
    cur.execute('INSERT INTO book(ISBN, Titolo, Autore, Genere, Anno) VALUES (%s, %s, %s, %s, %s);', (isbn, Titolo, Autore, Genere, Anno))
    conn.commit()

    # Restituisci una risposta di successo
    return jsonify({"Messaggio": "Dati inseriti correttamente"}, 201)


@app.route('/create_item', methods=['POST'])
def create_item():
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
    return jsonify({"Messaggio": "Dati inseriti correttamente"}, 201)


@app.route('/delete/<id>', methods=['DELETE'])
def delete_book(id):
    cur.execute('DELETE FROM book WHERE id = %s;', (id,))
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({'message': f'Book with the ID {id} deleted successfully'}, 200)
    else:
        return jsonify({'messagge': f'Book with ID {id} not found'}, 404)
    
@app.route('/delete-item/<id>', methods=['DELETE'])
def delete_item(id):
    cur.execute('DELETE FROM item WHERE id = %s;', (id,))
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({'message': f'Item with the ID {id} deleted successfully'}, 200)
    else:
        return jsonify({'messagge': f'Item with ID {id} not found'}, 404)
    
@app.route('/update/<id>', methods=['PUT'])
def update_book(id):
    up_data = request.get_json()
    up_Isbn = up_data['ISBN']
    up_Titolo = up_data['Titolo']
    up_Autore = up_data['Autore']
    up_Genere = up_data['Genere']
    up_Anno = up_data['Anno']

    cur.execute(f'UPDATE book SET ISBN = %s, Titolo = %s, Autore = %s, Genere = %s, Anno = %s WHERE id ={id};',(up_Isbn,up_Titolo,up_Autore,up_Genere,up_Anno))
    if cur.rowcount > 0:
        return jsonify({'messagge': f'Book with ID {id} updated successfully'})
    else:
        return jsonify({'messagge':f'Book with ID {id} not found'})
    
@app.route('/set_availability/<item_id>', methods=['PUT'])
def set_availability_true(item_id):
    cur.execute('UPDATE item SET isDisponibile = NOT isDisponibile WHERE id = %s', item_id)
    conn.commit()
    return 'Disponibilità cambiata con successo', 200

@app.route('/update-item/<id>', methods=['PUT'])
def update_item(id):
    up_data = request.get_json()
    up_book_id = up_data['book_id']
    up_status_libro = up_data['stato_libro']

    cur.execute(f'UPDATE item SET book_id=%s, stato_libro=%s WHERE id ={id};',(up_book_id,up_status_libro,))
    if cur.rowcount > 0:
        return jsonify({'messagge': f'Item with ID {id} updated successfully'})
    else:
        return jsonify({'messagge':f'Item with ID {id} not found'})

if __name__ == '__main__':
    with conn.cursor() as cursor:
        cursor.execute(open('database/books.sql', 'r').read())
        conn.commit()
    with conn.cursor() as cursor:
        cursor.execute(open('database/insert.sql', 'r').read())
        conn.commit()

app.run(host = '0.0.0.0', port = 5000, debug = True)
    