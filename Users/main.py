from flask import Flask,request,jsonify
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os
from bson import json_util
from pymongo.server_api import ServerApi
import pika

load_dotenv()
app = Flask(__name__)

uri = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_URL')}/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))

@app.route('/')
def get_users():
    collections = client.Library.users
    users = collections.find()
    users = json_util.dumps(users)
    users = json_util.loads(users)
    for user in users:
        user.pop('_id')
    return jsonify(users)

@app.route('/users/<username>', methods =['GET'])
def get_user(username):
    collections = client.Library.users
    user = collections.find_one({"Username":username})
    user.pop('_id')
    return user



@app.route('/register', methods =['POST'])
def create_user():
    collections = client.Library.users
    if not request.is_json:
        return jsonify({"message": "Please provide a valid JSON"}), 400
    user = request.get_json()

    required_fields = ['Nome', 'Cognome', 'Username', 'Email', 'Password', 'DataNascita']

    for field in required_fields:
        if not user.get(field):
            return jsonify({"message": f"{field} is a required field"}), 400
        
    Nome = user['Nome']
    Cognome = user['Cognome']
    Username = collections.find_one({'Username': user['Username']})
    if Username:
        return jsonify({"message": f"User {Username} already exists"}), 400
    Email = user['Email']
    Password = user['Password']
    DataNascita = user['DataNascita']

    collections.insert_one(user)
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    channel.basic_publish(exchange='',
        routing_key='hello',
        body=f'Benvenuto {Nome}!!')
    connection.close()

    return jsonify({"message": f"User {Nome} {Cognome} created successfully"}), 201

@app.route('/delete/<username>', methods =['DELETE'])
def delete_user(username):
    collections = client.Library.users
    if not username:
        return "Username cannot be empty", 400
    user = collections.find_one({'Username': username})
    if user is None:
        return jsonify({"message": f"User with User {username} not found"}), 404
    collections.delete_one({'Username': username})
    return jsonify({"message": f"User with User {username} deleted successfully"}), 200

@app.route('/update/<username>', methods =['PUT'])
def update_user(username):
    collections = client.Library.users
    if not request.is_json:
        return jsonify({"message": "Please provide a valid JSON"}), 400
    user = request.get_json()
    user = collections.find_one({'Username': username})
    required_fields = ['Nome', 'Cognome', 'Email', 'Password', 'DataNascita']

    for field in required_fields:
        if not user.get(field):
            return jsonify({"message": f"{field} is a required field"}), 400
        
    Nome = user['Nome']
    Cognome = user['Cognome']
    Email = user['Email']
    Password = user['Password']
    DataNascita = user['DataNascita']
    collections.update_one({'Username': username}, {'$set': user})
    return jsonify({"message": f"User {Nome} {Cognome} updated successfully"}), 200
app.run(host = '0.0.0.0', port = 9898, debug = True)

    