from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import MetaData, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from config import bcrypt

db = SQLAlchemy()


class Charity(db.Model, SerializerMixin):
    tablename = 'charities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    mission_statement = db.Column(db.String)

    def repr(self):
        return f'<Charity {self.name} | Description: {self.description} | Mission Statement: {self.mission_statement}>'

# User Model
class User(db.Model, SerializerMixin):
    tablename = 'users'

    # Serialization rules
    serialize_only = ("id", "username", "email")
    serialize_rules = ("-charities",'-_password_hash')

    # Define columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(80), nullable=False, unique=True)
    email = db.Column(String(120), nullable=False, unique=True)
    _password_hash = db.Column(db.String)


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
      
    
    # Relationships between user and charities will go here
    # Association too
    
   
    
    def repr(self):
        return f'User {self.username} is created successfully'
    