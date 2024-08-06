from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, Blueprint
from auth.models import User
from db import initialize_db
from encryption import encrypt, validate_password


auth_bp = Blueprint('auth', __name__)
client = initialize_db()

@auth_bp.route('/users/', methods = ['GET'])
def list_users():
    params = request.json
    return jsonify({'users': User.list_users()})

@auth_bp.route('/users/sign_in', methods = ['POST'])
def sign_in():
    params = request.json # reading the user sent parameters here
    if not params["email"]:
        return jsonify({"success": False, "errors": "Please send the valid parameters"})
    if "password" not in params:
            return jsonify({"success": False, "errors": "Password cannot be blank"})
    user = User.get_user_by_email(params["email"])
    if user:
        print("here is encrypted", encrypt(params["password"]))
        is_valid = validate_password(user.password, params["password"])
        if is_valid:
            return jsonify({"success": True, "id": str(user.id), "token": user.token, 'name': user.name.upper(), 'email': user.email })
        else:
            return jsonify({"success": False, "errors": "Incorrect email or password"})
    else:
        return jsonify({"success": False, "errors": "Incorrect email or password"})    


@auth_bp.route('/users/sign_up', methods = ['GET', 'POST'])
def sign_up():
    params = request.json
    if params:
        if not params["email"]:
            return jsonify({"success": False, "errors": "Please send the valid parameters"})
        if "name" not in params:
            return jsonify({"success": False, "errors": "Name cannot be blank"})
        if "password" not in params:
            return jsonify({"success": False, "errors": "Password cannot be blank"})
        if "confirm_password" not in params:
            return jsonify({"success": False, "errors": "Confirm Password cannot be blank"})
        if params["confirm_password"] != params["password"]:
            return jsonify({"success": False, "errors": "Password confirmation must match the entered password"})
        user, errors = User.create_user(params["email"], params["name"].lower(), params["password"], "user")
        if user:
            return jsonify({"success": True, "id": str(user.id), "token": user.token, 'name': user.name.upper(), 'email': user.email })
        else:
            return jsonify({"errors": errors})
    else:
        return jsonify({"success": False, "errors": "Please pass all the params"})