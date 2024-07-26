from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, Blueprint
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
# import custom files in order to make project modular
from auth import auth
from projects import projects
from auth.models import User
from db import initialize_db



app = Flask(__name__)
app.config['SECRET_KEY'] = "adskbajnbkabk7821"
client = initialize_db()
CORS(app)


auth_app = app.register_blueprint(auth.auth_bp, url_prefix = '/auth/v1')
project_app = app.register_blueprint(projects.project_bp)


if __name__ == '__main__':
	app.run(debug=True)
