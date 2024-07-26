from flask import Flask, Blueprint
from projects import projects

app = Flask(__name__)

project_app = app.register_blueprint(projects.project_bp)

