from mongoengine import connect, disconnect
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def initialize_db():
    uri = "mongodb+srv://mhamzaaltaf28:sJs9wZhtH1sdGhtI@apadproject.bqoewsr.mongodb.net/flask_db?retryWrites=true&w=majority&appName=apadproject"
    # Disconnect any existing connection
    disconnect(alias='default')
    # MongoDB Atlas URI should include the database name (flask_db in this case)
    return connect(host=uri, alias='default', server_api=ServerApi('1'))
