from flask import Flask
import mongoengine as db
from mongoengine.errors import ValidationError, NotUniqueError
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from auth.models import User
from utilities import Utilities
import datetime

class Project(db.Document):
    pid = db.StringField(required = True, min_length = 5, unique = True)
    name = db.StringField(required = True)
    description = db.StringField(required = True)
    user = db.ReferenceField(User, required = True)
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()
    meta = {
        'collection': 'projects_collection',
        'indexes': [
            'pid'
        ]
    }
    
    @classmethod
    def create_project(cls, pid, name, description, user):
        new_project = cls(pid = pid, name = name, description = description, user = user, created_at = datetime.datetime.now())
        try: 
            new_project.save()
            return new_project, None
        except (ValidationError, DuplicateKeyError, NotUniqueError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    @classmethod
    def get_project_by_pid(cls, pid):
        return cls.objects(pid = pid).first()
    
    @classmethod
    def get_user_projects(cls, user):
        return Project.objects(user = user)
    
    @classmethod
    def update_project(cls, pid, change_object, user):
        user_projects = cls.get_user_projects(user)
        project = user_projects(pid = pid).first()
        if project:
            try:
                update = project.objects(pid = pid).update(**change_object) # fetching object again in order to avoid the race condition
                return user_projects(pid = pid).first(), None # need to read the updated object therefore calling it again
            except ValidationError as e:
                errors = Utilities.error_formatter(e.to_dict())
                return None, errors
        else:
            return None, "Invalid PID"
        
    @classmethod
    def delete_project(cls, pid, user):
        user_projects = cls.get_user_projects(user)
        if user_projects:
            project = user_projects(pid = pid).first()
            if project:
                project.delete()
            else:
                return False
        else:
            return False
    
    @classmethod
    def list_user_projects(cls, user):
        projects = cls.get_user_projects(user)
        if projects:
            response_obj = [{"id": str(p.id), "pid": p.pid, "name": p.name, "description": p.description} for p in projects]
            return response_obj
        else:
            return []
    
    @classmethod
    def project_with_object(cls, pid, user):
        projects = cls.get_user_projects(user)
        if projects:
            project = projects(pid = pid).first()
            if project:
                response_obj = {"id": str(project.id), "pid": project.pid, "name": project.name, "description": project.description}
                return response_obj
            else: 
                return None
        else:
            return None
        
        
