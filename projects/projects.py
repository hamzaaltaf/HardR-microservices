from flask import Flask, Blueprint, jsonify, request, g
from projects.models import Project
from auth.models import User
from db import initialize_db

project_bp = Blueprint('project', __name__)
initialize_db()

# This method will run before each and every API to make sure that user exists against the token
@project_bp.before_request
def check_and_return_user():
    params = request.get_json()
    if 'token' in params:
        print("we are inside the check and return user")
        user = User.get_user_by_id(params['token'])
        if user:
            g.user = user
        else:
            return jsonify({'success': False, 'errors': "Invalid Token"})
    else:
        return jsonify({'success': False, 'errors': "Parameter token is missing"})

@project_bp.route('/users/<string:token>/projects', methods = ['GET'])
def user_projects(token):
    print("here is token", token)
    projects = Project.list_user_projects(g.user)
    return jsonify({'success': True, 'projects': projects})
    
    
@project_bp.route('/users/<string:token>/create_project', methods = ['POST'])
def create_project(token):
    params = request.get_json()
    if 'pid' not in params:
        return jsonify({'success': False, 'errors': 'pid is required'})
    if 'name' not in params:
        return jsonify({'success': False, 'errors': 'name is required'})
    if 'description' not in params:
        return jsonify({'success': False, 'errors': 'description is required'})
    project, errors = Project.create_project(params['pid'], params['name'], params['description'], g.user)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True, 'projects': Project.list_user_projects(g.user)})


@project_bp.route('/users/projects/view_project', methods = ['GET'])
def get_project_details():
    params = request.get_json()
    if 'pid' not in params:
        return jsonify({'success': False, 'errors': 'PID is required'})
    project = Project.project_with_object(params['pid'], g.user)
    return jsonify({'success': True, 'project': project})

@project_bp.route('/users/<string:token>/project/<int:pid>', methods = ['PATCH'])
def update_project(token, pid):
    params = request.to_json()
    change_object = {
        'name': params['name'],
        'description': params['description']
    }
    project, errors = Project.update_project(params['pid'], change_object, g.user)
    if errors:
        return jsonify({'success': False, 'errors': errors})
    return jsonify({'success': True, 'projects': Project.list_user_projects(g.user), 'project': Project.get_project_by_pid(params['pid'])})
    
        
    