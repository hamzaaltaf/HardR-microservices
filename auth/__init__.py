from flask import Flask, Blueprint
from auth import auth

app = Flask(__name__)

auth_app = app.register_blueprint(auth.auth_bp)

