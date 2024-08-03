from flask import Flask
import mongoengine as db
from mongoengine.errors import ValidationError
from pymongo.errors import DuplicateKeyError
from encryption import encrypt, validate_password
from bson.objectid import ObjectId
import jwt
from datetime import datetime, timedelta

class User(db.Document):
    email = db.EmailField(required = True)
    password = db.StringField(required = True, min_length  = 8)
    role  = db.StringField()
    name = db.StringField(required = True)
    token = db.StringField(required = True)
    expires_at = db.DateTimeField()
    meta = {
        'collection': 'users_collection'
    }
    
    @classmethod
    def delete_all_users(cls):
        cls.objects().delete()
    
    @classmethod
    def list_users(cls):
        res = []
        users = User.objects
        if users:
            res = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
        return res
    
    @classmethod
    def get_user_by_token(cls, token):
        return User.objects(token = token).first()
    
    
    @classmethod
    def get_user_by_id(cls, id):
        return User.objects(id = id).first()
    
    @classmethod
    def create_user(cls, email, name, password, role):
        if role not in ["user", "admin"]:
            return None, "Role can only be admin or user" 
        existing_user = User.objects(email=email).first()
        if existing_user:
            return None, "User with this email already exists."
        new_user = User(email = email, name = name, password = encrypt(password), role=role)
        new_user.token = jwt.encode({
            'email': email,
            'name': name,
            'password': password,
            'exp': 259200
            },
            "random_secret",
            algorithm='HS256'
        )
        new_user.expires_at = datetime.now() + timedelta(seconds = 259200)
        try: 
            new_user.save()
            return new_user, None
        except ValidationError or DuplicateKeyError as e:
            errors = e.to_dict()
            formatted_errors = []
            for field, message in errors.items():
                formatted_errors.append(f"{field} {message.lower()}")
            formatted_errors = ', '.join(formatted_errors)
            return None, formatted_errors
    
    @classmethod
    def get_user_by_email(cls, email):
        return User.objects(email = email).first()
        
    @classmethod
    def get_user_by_id(cls, id):
        return User.objects(id = ObjectId(id)).first()
    
    @classmethod
    def delete_user(cls, id):
        user = User.objects(id = ObjectId(id)).first()
        if user:
            return user.delete()
        else:
            return "No user found with this ID."
    
    @classmethod
    def update_user(cls, id, change_object):
        user = cls.objects(id = ObjectId(id)).first()
        if user:
            try:
                updated = cls.objects(id = ObjectId(id)).update(**change_object)
                if updated:
                    return True, None
                else:
                    return False, "User was not updated"
            except Exception as e:
                return False, e.to_dict()
        else:
            return False, "User was not found agains the ID"