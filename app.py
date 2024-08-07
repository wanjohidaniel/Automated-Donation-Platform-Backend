import os
from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource, Api
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt

from models import db, Charity, User, Donation


app = Flask(__name__)
api = Api(app)

bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

os.environ["DB_EXTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a.oregon-postgres.render.com/charities_donations_db"
os.environ["DB_INTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a/charities_donations_db"

# Configure SQLAlchemy database URI based on environment variables
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up database URI based on environment (use DB_EXTERNAL_URL by default)
if os.getenv('FLASK_ENV') == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_INTERNAL_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_EXTERNAL_URL")

# Set the Flask app secret key from environment variable
app.config["SECRET_KEY"] = "group6Project"
    
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


class Charities(Resource):
    def get(self, id=None):
        if id is None:
            charities = [charity.to_dict() for charity in Charity.query.all()]
            response = make_response(jsonify(charities), 200)
            return response
        else:
            charity = Charity.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(charity), 200)
    #update a charity
    def patch(self, id):
        data = request.get_json()

        charity = Charity.query.filter_by(id=id).first()

        for attr in data:
            setattr(charity, attr, data[attr])

        db.session.add(charity)
        db.session.commit()

        return make_response(charity.to_dict(), 200)

   
    #add a new charity
    def post(self):
        
        data = request.get_json()
        
        name=data.get('name'),
        description=data.get('description'),
        mission_statement = data.get('mission_statement'),
        goals = data.get('goals'),
        impact = data.get('impact'),
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

    
        
class AdminDecision(Resource):

    #get all pending charity requests
    def get(self, id=None):
        if id is None:
            charities = [charity.to_dict() for charity in Charity.query.filter_by(status='pending').all()]
            response = make_response(jsonify(charities), 200)
            return response
#fetch total donation for a charity
class Total(Resource):
    def get(self, id):
        # Get the charity by its id
        charity = Charity.query.filter_by(id=id).first()

        # Get the total donations for the charity
        total_donations = charity.totalDonations

        # Return the total donations as a JSON response
        return jsonify({"total_donations": total_donations})

#fetch total donation for a charity
class UserTotalDonations(Resource):
    def get(self, id):
        # Get the user by its id
        user = User.query.filter_by(id=id).first()

        # Get the total donations for the charity
        total_donations = user.totalDonations

        # Return the total donations as a JSON response
        return jsonify({"total_donations": total_donations})

class UserDonationHistory(Resource):
    def get(self, id):
        # Get the user by his id
        user = User.query.filter_by(id=id).first()
        #get donations history
        donations = user.donationsHistory
        #return donations as a json response
        return jsonify({'donation history': donations})


          
 #allow an admin to decide
class Delete(Resource):
    def delete_charity_by_id(self, id):
        charity = Charity.query.get(id)
        if charity:
            db.session.delete(charity)
            db.session.commit()
            return True
        return False
class Approve(Resource):
    def post(self, id):
        # Approve the charity
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
        # Review the charity
        charity = Charity.query.get(id)
        charity.review()
        db.session.commit()
  
#api to create a donation
class Donation(Resource):
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
    
    def post(self):
        data = request.get_json()
        username = data.get('userName')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')
        if not all([username, email, password, role]):
            return {'error': '422 Unprocessable Entity'}, 422
        user = User(username=username, email=email, role=role)
        
         # the password setter will encrypt this
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

#check session to see if there exists a user logged in

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {}, 401

api.add_resource(Total, '/total/<int:id>') 
api.add_resource(AdminDecision, '/charities/<int:id>') 
api.add_resource(Donation, '/donations')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')     
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Charities, "/charities")
api.add_resource(Users, '/users', '/users/<int:id>')
api.add_resource(UserDonationHistory, '/donations/<int:id>') 
api.add_resource(Approve, '/approve/<int:id>')
api.add_resource(Review, '/review/<int:id>')
api.add_resource(Reject, '/reject/<int:id>')
api.add_resource(Delete, '/delete/<int:id>')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)