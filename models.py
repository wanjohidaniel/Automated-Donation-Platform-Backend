from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class Charity(db.Model, SerializerMixin):
    tablename = 'charities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    mission_statement = db.Column(db.String)

    def repr(self):
        return f'<Charity {self.name} | Description: {self.description} | Mission Statement: {self.mission_statement}>'
