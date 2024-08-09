from flask import Flask
import mongoengine as db
from mongoengine.errors import ValidationError, NotUniqueError
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from utilities import Utilities
from auth.models import User
import datetime

class Transaction(db.Document):
    CHECKIN = 1
    CHECKOUT = 2
    EVENT_TYPES = {
        CHECKIN: 'checkin',
        CHECKOUT: 'checkout'
    }

    event_type = db.IntField(required=True, choices=EVENT_TYPES.keys())
    requested_qty = db.IntField(required=True)
    approved_qty = db.IntField(required=True)
    owner = db.GenericReferenceField()
    requester = db.GenericReferenceField()
    user = db.ReferenceField(User)
    created_at = db.DateTimeField(default = datetime.datetime.now())
    updated_at = db.DateTimeField(default = datetime.datetime.now())
    meta = {
        'collection': 'transactions_collection',
    }
    
    @classmethod
    def get_transactions_for_hardware_set(cls, set):
        return cls.objects(owner = set)
    
    @classmethod
    def create_checkout_transaction(cls, requested_qty, user, hardware_set, requester):
        approved_qty = requested_qty
        if requested_qty > hardware_set.availability:
            approved_qty = hardware_set.availability
            hardware_set.availability = 0
        else:
            approved_qty = requested_qty
        # create the transaction
        new_set = cls(requested_qty = requested_qty,
                    approved_qty = approved_qty,
                    user = user,
                    owner = hardware_set,
                    requester = requester,
                    event_type = cls.CHECKOUT
                )
        try:
            print("here is the total checkout", hardware_set.availability)
            new_checked_out = requester.total_checked_out + approved_qty
            new_availability = hardware_set.availability - approved_qty
            if new_availability < 0:
                new_availability = 0
            print("here is the NEW AVAILABILIUTY", new_availability)
            new_set.save()
            hardware_set.update(availability = new_availability)
            requester.update(total_checked_out = new_checked_out)
            return new_set, None
        except (ValidationError, DuplicateKeyError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    @classmethod
    def create_checkin_transaction(cls, requested_qty, user, hardware_set, requester):
        approved_qty = requested_qty
        
        # current_pending_qty = (requester.total_checked_out or 0) - (requester.total_checked_in or 0)
        current_pending_qty = Transaction.get_project_and_hardware_checkouts(hardware_set, requester)
        print("Thi is current quantity", current_pending_qty)
        print("Thi is requested quantityt", requested_qty)
        # if requested_qty > hardware_set.capacity:
        #     return None, "You cannot check in more than capacity."
        if current_pending_qty == 0:
            return None, "You have no pending items to check in. Please check out items first."
        if requested_qty > current_pending_qty:
            return None, "You cannot return more than what you checked out"
        # project_checked_out = 
        new_set = cls(requested_qty = requested_qty,
                    approved_qty = approved_qty,
                    user = user,
                    owner = hardware_set,
                    requester = requester,
                    event_type = cls.CHECKIN)
        try:
            new_set.save()
            new_checked_in = requester.total_checked_in + approved_qty
            new_availability = hardware_set.availability + approved_qty
            requester.update(total_checked_in = new_checked_in)
            hardware_set.update(availability = new_availability)
            return new_set, None
        except (ValidationError, DuplicateKeyError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    @classmethod
    def get_project_transactions_objects(cls, project):
        transactions = cls.objects(requester = project)
        if transactions:
            response_obj = [
                {
                    "event_type": cls.EVENT_TYPES.get(s.event_type, "unknown"),
                    "requested_qty": s.requested_qty,
                    "approved_qty": s.approved_qty,
                    "user_email": s.user.email,
                    "project_id": s.requester.pid,
                    "project_name": s.requester.name,
                    "project_desc": s.requester.description,
                    "created_at": s.created_at
                } for s in transactions]
            print("HERE WE ARE", response_obj)
            return response_obj
        else:
            return []
    
    @classmethod
    def get_user_transactions_objects(cls, user):
        transactions = cls.objects(user = user)
        if transactions:
            response_obj = [
                {
                    "event_type": s.event_type,
                    "requested_qty": s.requested_qty,
                    "approved_qty": s.approved_qty,
                    "user_email": s.user.email,
                    "project_id": s.requester.id,
                    "project_name": s.requester.name,
                    "project_desc": s.requester.description,
                    "created_at": s.created_at
                } for s in transactions]
            print("HERE WE ARE", response_obj)
            return response_obj
        else:
            return []
    
    @classmethod
    def get_hardware_checkouts(cls, hardware_set):
        ck_out_records = cls.objects(owner = hardware_set, event_type = cls.CHECKOUT)
        ck_in_records = cls.objects(owner = hardware_set, event_type = cls.CHECKIN)
        ck_out = sum(record['approved_qty'] for record in ck_out_records) or 0
        ck_in = sum(record['approved_qty'] for record in ck_in_records) or 0
        result = ck_out - ck_in
        if result < 0: 
            result = 0
        return result

    @classmethod
    def get_hardware_checkins(cls, hardware_set):
        records = cls.objects(owner = hardware_set, event_type = cls.CHECKIN)
        return  sum(record['approved_qty'] for record in records) or 0
    
    @classmethod
    def get_project_and_hardware_checkouts(cls, hardware_set, project):
        records = cls.objects(owner = hardware_set, event_type = cls.CHECKOUT, requester = project)
        projects_total_checkouts = sum(record['approved_qty'] for record in records) or 0
        return projects_total_checkouts
    
    
    @classmethod
    def get_hardware_transactions_objects(cls, hardware_set):
        transactions = cls.objects(owner = hardware_set)
        if transactions:
            response_obj = [
                {
                    "event_type": s.event_type,
                    "requested_qty": s.requested_qty,
                    "approved_qty": s.approved_qty,
                    "user_email": s.user.email,
                    "project_id": s.requester.id,
                    "project_name": s.requester.name,
                    "project_desc": s.requester.description,
                    "created_at": s.created_at
                } for s in transactions]
            print("HERE WE ARE", response_obj)
            return response_obj
        else:
            return []