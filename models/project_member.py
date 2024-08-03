from flask import Flask
import mongoengine as db
from mongoengine.errors import ValidationError, NotUniqueError
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from auth.models import User
from projects.models import Project
from utilities import Utilities
import datetime

class ProjectMember(db.Document):
    user = db.ReferenceField(User, required = True)
    project = db.ReferenceField(Project, required = True)
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()
    meta = {
        'collection': 'projects_members_collection',
    }
    
    @classmethod
    def alredy_registered_memeber(cls, project, user):
        project_member = cls.objects(project = project, user = user).first()
        if project_member:
            return True
        else:
            return False
        
    @classmethod
    def create_project_member(cls, project, user, session = None):
        new_project = cls(project = project, user = user, created_at = datetime.datetime.now())
        try: 
            if session:
                new_project.save(session = session)
            else:
                new_project.save()
            return new_project, None
        except (ValidationError, DuplicateKeyError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    @classmethod
    def get_project_members(cls, project):
        project_members = cls.objects(project = project)
        if project_members:
            response_obj = [
                {
                    "id": str(p.id),
                    "user_email": p.user.email,
                    "user_id": str(p.user.id),
                    "project_id": str(p.project.id),
                    "project_name": p.project.name,
                    "project_description": p.project.description,
                    "created_at": p.created_at
                } for p in project_members]
            print("HERE WE ARE", response_obj)
            return response_obj
        else:
            return []
    
    @classmethod
    def delete_project_member(cls, user, project):
        projects = cls.objects(project = project)
        if projects:
            member = projects(user = user).first()
            if member:
                member.delete()
            else:
                return False
        else:
            return False
