from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, Blueprint, g
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
from auth import auth
# from projects import projects
from auth.models import User
from db import initialize_db
from projects.models import Project
from auth.models import User



app = Flask(__name__)
# CORS(app, resources={r'/*': {'origins': '*'}})
app.config['SECRET_KEY'] = "adskbajnbkabk7821"
client = initialize_db()
CORS(app)




auth_app = app.register_blueprint(auth.auth_bp, url_prefix = '/auth/v1')
# project_app = app.register_blueprint(projects.project_bp)


@app.route('/')
def delete_all():
    c = User.delete_all_users
    print("here is size", c)
    if c:
        return {'success': True}
    else:
     return {'success': False}

@app.route('/users/list_projects', methods = ['POST', 'OPTIONS'])
@cross_origin()
def user_projects():
    user = ""
    params = request.get_json()
    print(params)
    if 'user_id' in params:
        user = User.get_user_by_id(params['user_id'])
        if user:
            g.user = user
            projects = Project.list_user_projects(user)
            return jsonify({'success': True, 'projects': projects})
        else:
            return jsonify({'success': False, 'errors': "Invalid Token"})
    else:
        return jsonify({'success': False, 'errors': "Parameter token is missing"})


@app.route('/users/create_project', methods = ['POST'])
def create_project():
    params = request.get_json()
    user = ""
    if 'user_id' in params:
        user = User.get_user_by_id(params['user_id'])
        print("here is user", user)
        if user:
            g.user = user
        else:
            return jsonify({'success': False, 'errors': 'User not found'})
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'pid is required'})
    if 'name' not in params:
        return jsonify({'success': False, 'errors': 'name is required'})
    if 'description' not in params:
        return jsonify({'success': False, 'errors': 'description is required'})
    project, errors = Project.create_project(params['project_id'], params['name'], params['description'], user)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True, 'projects': Project.list_user_projects(user)})


# @app.route('/users/<string:token>/list_projects', methods=['POST', 'GET'])
# @cross_origin()
# def list_projects(token):
# 	return jsonify({'success': True, 'projects': []})


if __name__ == '__main__':
	app.run(debug=True)
