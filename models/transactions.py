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
            requester.total_checked_out += approved_qty
        else:
            hardware_set.availability -= requested_qty
            requester.total_checked_out += requested_qty
        new_set = cls(requested_qty = requested_qty, approved_qty = approved_qty, user = user, owner = hardware_set, requester = requester, event_type = cls.CHECKOUT)
        try:
            new_set.save()
            requester.update(total_checked_out = requester.total_checked_out + approved_qty)
            return new_set, None
        except (ValidationError, DuplicateKeyError) as e:
            errors = Utilities.error_formatter(e)
            return None, errors
    
    @classmethod
    def create_checkin_transaction(cls, requested_qty, user, hardware_set, requester):
        approved_qty = requested_qty
        current_pending_qty = (requester.total_checked_out or 0) - (requester.total_checked_in or 0)
        if current_pending_qty == 0:
            return None, "You have no pending items to check in. Please check out items first."
        if requested_qty > current_pending_qty:
            return None, "You cannot return more than what you checked out"
        new_set = cls(requested_qty = requested_qty, approved_qty = approved_qty, user = user, owner = hardware_set, requester = requester, event_type = cls.CHECKIN)
        try:
            new_set.save()
            requester.update(total_checked_in = requester.total_checked_in + approved_qty)
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
        return cls.objects(owner = hardware_set, event_type = cls.CHECKOUT).count()

    @classmethod
    def get_hardware_checkins(cls, hardware_set):
        return cls.objects(owner = hardware_set, event_type = cls.CHECKIN).count()
    
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