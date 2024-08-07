from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, Blueprint, g
from pymongo import MongoClient
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId
from auth import auth
from db import initialize_db
from auth.models import User
from projects.models import Project
from models.project_member import ProjectMember
from models.hardware_set import HardwareSet
from models.transactions import Transaction



app = Flask(__name__)
# CORS(app, resources={r'/*': {'origins': '*'}})
app.config['SECRET_KEY'] = "adskbajnbkabk7821"
client = initialize_db()
CORS(app)




auth_app = app.register_blueprint(auth.auth_bp, url_prefix = '/auth/v1')
# project_app = app.register_blueprint(projects.project_bp)


@app.route('/delete_all_users')
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
            # projects = Project.list_user_projects(user)
            projects = ProjectMember.get_projects_list(user)
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
    session = client.start_session()
    with session.start_transaction():
        project, errors = Project.create_project(params['project_id'], params['name'], params['description'], user, session)
        if errors:
            return jsonify({'success': False, 'errors': errors})
        member, member_errors = ProjectMember.create_project_member(project, user, session)
        if errors:
            return jsonify({'success': False, 'errors': member_errors})
        return jsonify({'success': True, 'projects': Project.list_user_projects(user)})
        


@app.route('/projects/join_project', methods = ['POST'])
def join_project():
    params = request.get_json()
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    # check of the user_id is sent along the request, if not send back the error
    if 'user_id' not in params:
        return jsonify({'success': False, 'errors': 'User ID is required'})
    user = User.get_user_by_id(params['user_id'])
    if not user:
        return jsonify({'success': False, 'errors': 'Invalid user id'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    if ProjectMember.alredy_registered_memeber(project, user):
        return jsonify({'success': False, 'errors': 'Already member of this project'})
    member, errors = ProjectMember.create_project_member(project, user, None)
    if not errors:
        return jsonify({'success': True, 'members': ProjectMember.get_project_members(project)})
    # return errors in case you don't find errors
    return jsonify({'success': False, 'errors': errors})

# This API is responsible for listing down the members
@app.route('/projects/members', methods = ['POST'])
def list_project_members():
    params = request.get_json()
    # check of the project_id is sent along the request, if not send back the error
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    project_obj = Project.project_details(project)
    members = ProjectMember.get_project_members(project)
    print("responding with success TRUE", members)
    return jsonify({'success': True, 'project': project_obj, 'members': ProjectMember.get_project_members(project)})
	
# APIs for hardware set
@app.route('/list_sets', methods = ["GET"])
def list_hardware():
    return jsonify({'success': True, 'sets': HardwareSet.get_all_hardware_set_objects()})

@app.route('/create_hardware', methods = ["POST"])
def create_hardware():
    params = request.get_json()
    if 'name' not in params:
        return jsonify({'success': False, 'errors': 'Name is required'})
    if 'capacity' not in params:
        return jsonify({'success': False, 'errors': 'Capacity is required'})
    if 'user_id' not in params:
        return jsonify({'success': False, 'errors': 'User ID is required'})
    user = User.get_user_by_id(params['user_id'])
    if not user:
        return jsonify({'success': False, 'errors': 'Invalid user id'})
    hardware, errors = HardwareSet.create_hardware_set(int(params['capacity']), params['name'], user)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True, 'sets': HardwareSet.get_all_hardware_set_objects()})

@app.route('/sets/checkout', methods = ["POST"])
def check_out():
    params = request.get_json()
    # check of the project_id is sent along the request, if not send back the error
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    if 'hardware_id' not in params:
        return jsonify({'success': False, 'errors': 'Hardware ID is required'})
    if 'quantity' not in params:
        return jsonify({'success': False, 'errors': 'Quantity is required'})
    if int(params['quantity']) < 1:
        return jsonify({'success': False, 'errors': 'Quantity must be greater than 0'})
    hardware_set = HardwareSet.get_hardware_set(params['hardware_id'])
    if not hardware_set:
        return jsonify({'success': False, 'errors': 'Invalid hardware id'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    if 'user_id' not in params:
        return jsonify({'success': False, 'errors': 'User ID is required'})
    user = User.get_user_by_id(params['user_id'])
    if not user:
        return jsonify({'success': False, 'errors': 'Invalid user id'})
    if hardware_set.availability == 0:
        return jsonify({'success': False, 'errors': 'This set does not have availability'})
    transaction, errors = Transaction.create_checkout_transaction(int(params['quantity']), user, hardware_set, project)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True})

@app.route('/sets/checkin', methods = ["POST"])
def check_in():
    params = request.get_json()
    # check of the project_id is sent along the request, if not send back the error
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    if 'hardware_id' not in params or 'hardware_id' == "":
        return jsonify({'success': False, 'errors': 'Hardware ID is required'})
    if 'quantity' not in params:
        return jsonify({'success': False, 'errors': 'Quantity is required'})
    if int(params['quantity']) < 1:
        return jsonify({'success': False, 'errors': 'Quantity must be greater than 0'})
    hardware_set = HardwareSet.get_hardware_set(params['hardware_id'])
    if not hardware_set:
        return jsonify({'success': False, 'errors': 'Invalid hardware id'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    if 'user_id' not in params:
        return jsonify({'success': False, 'errors': 'User ID is required'})
    user = User.get_user_by_id(params['user_id'])
    if not user:
        return jsonify({'success': False, 'errors': 'Invalid user id'})
    transaction, errors = Transaction.create_checkin_transaction(int(params['quantity']), user, hardware_set, project)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True})

@app.route('/sets/list_transactions', methods = ["POST"])
def list_transactions():
    params = request.get_json()
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    return jsonify({'success': True, 'transactions': Transaction.get_project_transactions_objects(project)})

# Private Methods
""" Private Methods to get rid of repetition of code in the APIs"""
def _get_user():
    params = request.get_json()
    if 'user_id' not in params:
        return jsonify({'success': False, 'errors': 'User ID is required'})
    user = User.get_user_by_id(params['user_id'])
    if not user:
        return jsonify({'success': False, 'errors': 'Invalid user id'})
    user
    
def _get_project():
    params = request.get_json()
    if 'project_id' not in params:
        return jsonify({'success': False, 'errors': 'Project ID is required'})
    project = Project.get_project_by_pid(params['project_id'])
    if not project:
        return jsonify({'success': False, 'errors': 'Invalid project id'})
    project

if __name__ == '__main__':
	app.run(debug=True, port=8000)
