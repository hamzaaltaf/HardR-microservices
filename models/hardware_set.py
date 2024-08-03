from flask import Flask
import mongoengine as db
from mongoengine.errors import ValidationError, NotUniqueError
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from utilities import Utilities
from auth.models import User
from models.transactions import Transaction
import datetime

class HardwareSet(db.Document):
    name = db.StringField(required = True)
    capacity = db.IntField(required=True, min_value=0, max_value=100000)
    availability = db.IntField(required=True, min_value=0, max_value=100000)
    user = db.ReferenceField(User)
    created_at = db.DateTimeField(default = datetime.datetime.now())
    updated_at = db.DateTimeField(default = datetime.datetime.now())
    meta = {
        'collection': 'hardware_collection',
    }
    
    @classmethod
    def get_hardware_set(cls, id):
        return cls.objects(id = id).first()
    
    @classmethod
    def create_hardware_set(cls, capacity, name, user = None):
        # if user and user.role != 'admin':
        #     return None, "Only admins can create hardware set"
        if capacity < 1:
            return None, "Capacity cannot be less than 1."
        new_set = cls(name =  name, capacity = capacity, availability = capacity, user = user, created_at = datetime.datetime.now())
        try: 
            new_set.save()
            return new_set, None
        except (ValidationError, DuplicateKeyError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    
    @classmethod
    def get_all_hardware_set_objects(cls):
        sets = cls.objects()
        if sets:
            response_obj = [
                {
                    "id": str(s.id),
                    "capacity": s.capacity,
                    "availability": s.availability,
                    "name": s.name,
                    'checked_out': Transaction.get_hardware_checkouts(s),
                    'checked_in': Transaction.get_hardware_checkins(s)
                } for s in sets]
            print("HERE WE ARE", response_obj)
            return response_obj
        else:
            return []
    
    @classmethod
    def update_capacity(cls, hardware_set, capacity):
        hardware_set = cls.objects(id = hardware_set.id).first()
        if hardware_set:
            updated = hardware_set.update(capacity = capacity, availability = hardware_set.availability + capacity)
            if updated:
                return True
            else:
                return False
        else:
            return False
    
    def update_availability(self, availability):
        updated = self.update(availability =  availability)
        if updated:
            return True
        else:
            return False
