from mongoengine import connect

MONGO_SETTINGS = {
    'db': 'flask_db',
    'host': 'localhost',
    'port': 27017
}

def initialize_db():
    connect(**MONGO_SETTINGS)