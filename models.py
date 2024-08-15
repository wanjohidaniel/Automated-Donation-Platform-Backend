from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData, Column, Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from config import bcrypt
import json

db = SQLAlchemy()



class Charity(db.Model, SerializerMixin):
    tablename = 'charities'

    serialize_only = ("id", "name", "image", "description", "paypal_account", "mission_statement", "impact", "goals", "status")
    serialize_rules = ("-users", "-donations")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image = db.Column(db.String)
    description = db.Column(db.String)
    mission_statement = db.Column(db.String)
    goals = db.Column(db.String(120), nullable=False, default='')
    impact = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String, default="pending")
    # Add PayPal account attribute
    paypal_account = db.Column(String(120), nullable=False)
    
    # Donations received by this charity
    #donations = db.relationship('Donation', back_populates='charity')

    def totalDonations(self):
        total = sum(donation.amount for donation in self.donations)
        return total

    def getDonations(self):
        return [donation.to_dict() for donation in self.donations]  # Ensure donations are returned as a list of dictionaries

    def to_dict(self):
        charity_dict = super().to_dict()
        charity_dict['donations'] = self.getDonations()
        charity_dict['totalDonatedAmount'] = self.totalDonations()
        return charity_dict
    
    #change the status of a charity request to reviewed
    def review(self):
        self.status = 'reviewed'
        db.session.commit()

    #change the status of a charity request to rapproved
    def approve(self):
        self.status = 'approved'
        db.session.commit()

    #change the status of a charity request to rejected
    def reject(self):
        self.status = 'rejected'
        db.session.commit()

    #change the status of a charity request to pending
    def pending(self):
        self.status = 'pending'
        db.session.commit()
    donations = db.relationship('Donation', back_populates='charity', cascade="all, delete-orphan")
    stories = db.relationship('Story', back_populates='charity', cascade="all, delete-orphan")
    recurring_donations = db.relationship('RecurringDonation', back_populates='charity', cascade="all, delete-orphan")
    def repr(self):
        return f'<Charity {self.name}| Paypal account: {self.paypal_account}  | Image: {self.image}  | Description: {self.description} | Mission Statement: {self.mission_statement}| goals: {self.goals} | impact: {self.impact} | status: {self.status}>'


# User Model
class User(db.Model, SerializerMixin):
    tablename = 'users'

    # Serialization rules
    serialize_only = ("id", "username", "email", "role")
    serialize_rules = ("-charities",'-donations','-_password_hash')

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(80), nullable=False, unique=True)
    email = db.Column(String(120), nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    role = db.Column(db.String, default="donor")
   
    

   

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8'))

    
    
    # Charities that the user has donated to
    """  # Relationship with charities
    charities = db.relationship("Charity", secondary="donations", backref="users") """

    # donations = db.relationship('Donation', back_populates='user')

    def totalDonations(self):
        total = sum(donation.amount for donation in self.donations)
        return total
    def get_all_donations_as_json(self):
        # Retrieve all donations related to the user
        donations = self.donations

        # Serialize donations into a dictionary
        donations_dict_list = []
        for donation in donations:
            donation_dict = {
                "id": donation.id,
                "amount": donation.amount,
                "date_time_created": donation.date_time_created.strftime('%Y-%m-%d'),
                "charity_name": donation.charity.name# Add more fields as needed
            }
            donations_dict_list.append(donation_dict)

        # Convert the list of donation dictionaries to JSON
        donations_json = json.dumps(donations_dict_list, indent=2)
        
        return donations_json
    
    def to_dict(self):
        user_dict = super().to_dict()
        user_dict['donations'] = self.get_all_donations_as_json()
        user_dict['totalDonatedAmount'] = self.totalDonations()
        return user_dict

   
    donations = db.relationship('Donation', back_populates='user', cascade="all, delete-orphan")
    recurring_donations = db.relationship('RecurringDonation', back_populates='user', cascade="all, delete-orphan")
    reminders = db.relationship('Reminder', back_populates='user', cascade="all, delete-orphan")
    @property
    def donationsHistory(self):
        donations = [{'amount': donation.amount, 'date_time_created': donation.date_time_created, 'charity_name': donation.charity.name} for donation in self.donations]
        return donations
    def __repr__(self):
        return f'User {self.username} | PayPal: {self.paypal_account} created succesfully'
    

#a donation can be made with a user, to a charity, so we require user_id and charity_id as foreign keys
class Donation(db.Model, SerializerMixin):
    tablename = 'donations'
    id = db.Column(db.Integer, primary_key=True)

    # Serialization rules
    serialize_only = ("id", "amount", "date_time_created", "user_id", "charity_id")
    serialize_rules = ("-users",'-charities')
    
    amount = db.Column(db.Float, nullable=False)
     # Date and time when the donation was created
    date_time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign key for the charity that received the donation
    charity_id = db.Column(db.Integer(), db.ForeignKey('charity.id'), nullable=False)
    # Foreign key for the user who made the donation
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='donations')
    charity = db.relationship('Charity', back_populates='donations')

    

    
    def repr(self):
        return '<Donation %r>' % self.id
    
class RecurringDonation(db.Model, SerializerMixin):
    _tablename_ = 'recurring_donations'

    serialize_only = ("id", "amount", "user_id", "charity_id", "frequency", "start_date", "next_donation_date")
    serialize_rules = ("-user", "-charity")

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    charity_id = db.Column(db.Integer(), db.ForeignKey('charity.id'), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # e.g., 'monthly', 'yearly'
    start_date = db.Column(db.DateTime, nullable=False)
    next_donation_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='recurring_donations')
    charity = db.relationship('Charity', back_populates='recurring_donations')

    def _repr_(self):
        return f'<RecurringDonation {self.id}>'

class Reminder(db.Model, SerializerMixin):
    _tablename_ = 'reminders'

    serialize_only = ("id", "message", "user_id", "remind_at")
    serialize_rules = ("-user",)

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    
    remind_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='reminders')

    def _repr_(self):
        return f'<Reminder {self.id}>'

class Story(db.Model, SerializerMixin):
    _tablename_ = 'stories'

    serialize_only = ("id", "title", "content", "charity_id", "image_url")
    serialize_rules = ("-charity",)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    charity_id = db.Column(db.Integer(), db.ForeignKey('charity.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    charity = db.relationship('Charity', back_populates='stories')

    def _repr_(self):
        return f'<Story {self.title}>'
class Beneficiary(db.Model):
     id = db.Column(db.Integer, primary_key=True) 
     name = db.Column(db.String(80), nullable=False)
     description = db.Column(db.String(200), nullable=False)
     inventory_needs = db.Column(db.JSON, nullable=True)
     charity_id =db.Column(db.Integer, db.ForeignKey('charity.id'), nullable=False)
     beneficiary_stories = db.relationship('BeneficiaryStory',backref='beneficiary', lazy=True, cascade='all, delete-orphan')
     def to_dict(self): 
        return { "id": self.id, "name": self.name, "description": self.description, "inventory_needs": self.inventory_needs, "charity_id": self.charity_id } 
class BeneficiaryStory(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    beneficiary_id = db.Column(db.Integer,db.ForeignKey('beneficiary.id'), nullable=False) 
    title = db.Column(db.String(100), nullable=False) 
    content = db.Column(db.Text, nullable=False) 
    image_url = db.Column(db.String(255), nullable=True)
    
    def to_dict(self): 
        return { "id": self.id, "beneficiary_id": self.beneficiary_id, "title": self.title, "content": self.content, "image_url": self.image_url }