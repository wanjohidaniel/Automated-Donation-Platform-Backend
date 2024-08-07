import os
from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource, Api
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt

from models import db, Charity, User, Donation  # Ensure models are imported

app = Flask(__name__)
api = Api(app)

bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

os.environ["DB_EXTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a.oregon-postgres.render.com/p4_db"
os.environ["DB_INTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a/p4_db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if os.getenv('FLASK_ENV') == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_INTERNAL_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_EXTERNAL_URL")

app.config["SECRET_KEY"] = "group6Project"

app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Ensure db.create_all() is within the app context
with app.app_context():
    db.create_all()

class Charities(Resource):
    def get(self, id=None):
        if id is None:
            charities = [charity.to_dict() for charity in Charity.query.all()]
            response = make_response(jsonify(charities), 200)
            return response
        else:
            charity = Charity.query.filter_by(id=id).first().to_dict()
            return make_response(jsonify(charity), 200)

    def patch(self, id):
        data = request.get_json()
        charity = Charity.query.filter_by(id=id).first()
        for attr in data:
            setattr(charity, attr, data[attr])
        db.session.add(charity)
        db.session.commit()
        return make_response(charity.to_dict(), 200)

    def delete(self, id):
        charity = Charity.query.filter_by(id=id).first()
        db.session.delete(charity)
        db.session.commit()
        return make_response('', 204)

    def post(self):
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        mission_statement = data.get('mission_statement')
        goals = data.get('goals')
        impact = data.get('impact')
        image = data.get('image')
        if not all([name, image, description, impact, goals, mission_statement]):
            return {'error': '422 Unprocessable Entity'}, 422
        charity = Charity(name=name, image=image, description=description, impact=impact, goals=goals, mission_statement=mission_statement)
        charity.status = "pending"
        db.session.add(charity)
        db.session.commit()
        return charity.to_dict(), 201

    def put(self, id):
        data = request.get_json()
        charity = Charity.query.get(id)
        if charity is None:
            return {"error": "charity not found"}, 404
        else:
            charity.name = data["name"]
            charity.description = data["description"]
            charity.mission_statement = data["mission_statement"]
            db.session.commit()
            return {"id": charity.id, "name": charity.name, "description": charity.description}

    def delete(self, id):
        charity = Charity.query.get(id)
        if charity is None:
            return {"error": "charity not found"}, 404
        else:
            db.session.delete(charity)
            db.session.commit()
            return {"result": "success"}

class AdminDecision(Resource):
    def get(self, id=None):
        if id is None:
            charities = [charity.to_dict() for charity in Charity.query.filter_by(status='pending').all()]
            response = make_response(jsonify(charities), 200)
            return response

class CharityTotalDonations(Resource):
    def get(self, id):
        charity = Charity.query.filter_by(id=id).first()
        total_donations = charity.totalDonations
        return jsonify({"total_donations": total_donations})

class UserTotalDonations(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        total_donations = user.totalDonations
        return jsonify({"total_donations": total_donations})

class UserDonationHistory(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        donations = user.donationsHistory
        return jsonify({'donation history': donations})

class Approve(Resource):
    def post(self, id):
        charity = Charity.query.get(id)
        charity.approve()
        db.session.commit()
        return make_response(charity.to_dict(), 200)

class Reject(Resource):
    def post(self, id):
        charity = Charity.query.get(id)
        charity.reject()
        db.session.commit()
        return make_response(charity.to_dict(), 200)

class Review(Resource):
    def post(self, id):
        charity = Charity.query.get(id)
        charity.review()
        db.session.commit()

class CreateDonation(Resource):
    def post(self):
        data = request.get_json()
        donation = Donation(amount=data['amount'], donor_id=data['donor_id'], charity_id=data['charity_id'])
        db.session.add(donation)
        db.session.commit()
        return jsonify({'id': donation.id, 'amount': donation.amount, 'donor_id': donation.donor_id, 'charity_id': donation.charity_id})

class Login(Resource):
    def post(self):
        request_json = request.get_json()
        username = request_json.get('username')
        password = request_json.get('password')
        user = User.query.filter(User.username == username).first()
        if user:
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        return {'error': '401 Unauthorized'}, 401

class Signup(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json()
        username = data.get('userName')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')
        if not all([username, email, password, role]):
            return {'error': '422 Unprocessable Entity'}, 422
        user = User(username=username, email=email, role=role)
        user.password_hash = password
        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {"message": "Logged out successfully"}, 200

class Users(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        response = make_response(jsonify(users), 200)
        return response

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {}, 401

api.add_resource(CharityTotalDonations, '/charities/<int:id>/total_donations') 
api.add_resource(AdminDecision, '/charities/<int:id>') 
api.add_resource(CreateDonation, '/donations')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')     
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Charities, "/charities", "/charities/<int:id>")
api.add_resource(Users, '/users', '/users/<int:id>')
api.add_resource(UserDonationHistory, '/users/<int:id>/donations') 
api.add_resource(Approve, '/approve/<int:id>')
api.add_resource(Review, '/review/<int:id>')
api.add_resource(Reject, "/reject/<int:id>")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
