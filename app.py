import os
from flask import Flask, request, jsonify, make_response, session
from flask_restful import Resource, Api
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
import paypalrestsdk
import stripe
from datetime import datetime

from models import db, Charity, User, Donation  # Ensure models are imported

app = Flask(__name__)
api = Api(app)

bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

<<<<<<< HEAD
os.environ["DB_EXTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a.oregon-postgres.render.com/charities_donations_db3"
os.environ["DB_INTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a/charities_donations_db3"

# Configure SQLAlchemy database URI based on environment variables
=======
os.environ["DB_EXTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a.oregon-postgres.render.com/p4_db"
os.environ["DB_INTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a/p4_db"

>>>>>>> refs/remotes/origin/master
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if os.getenv('FLASK_ENV') == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_INTERNAL_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_EXTERNAL_URL")

app.config["SECRET_KEY"] = "group6Project"

app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

<<<<<<< HEAD
# PayPal SDK configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba",
    "client_secret": "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba"
})
=======
# Ensure db.create_all() is within the app context
with app.app_context():
    db.create_all()
>>>>>>> refs/remotes/origin/master

# Stripe SDK configuration
stripe.api_key = "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba"


class CharityById(Resource):
    def get(self, id):
        charity = Charity.query.filter_by(id=id).first()
        if charity:
            return make_response(jsonify(charity.to_dict()))
        else:
<<<<<<< HEAD
            return make_response(jsonify({"error": "Charity not found"}), 404)
class UserById(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify(user.to_dict()))
        else:
            return make_response(jsonify({"error": "user not found"}), 404)
class Charities(Resource):
    def get(self):
            charities = Charity.query.all()
            return [charity.to_dict() for charity in charities], 200
    #update a charity
=======
            charity = Charity.query.filter_by(id=id).first().to_dict()
            return make_response(jsonify(charity), 200)

>>>>>>> refs/remotes/origin/master
    def patch(self, id):
        data = request.get_json()
        charity = Charity.query.filter_by(id=id).first()
        for attr in data:
            setattr(charity, attr, data[attr])
        db.session.add(charity)
        db.session.commit()
        return make_response(charity.to_dict(), 200)

<<<<<<< HEAD
   
    #add a new charity
=======
    def delete(self, id):
        charity = Charity.query.filter_by(id=id).first()
        db.session.delete(charity)
        db.session.commit()
        return make_response('', 204)

>>>>>>> refs/remotes/origin/master
    def post(self):
        data = request.get_json()
<<<<<<< HEAD
        
        name=data.get('name'),
        paypal_account=data.get('paypal_account'),
        description=data.get('description'),
        mission_statement = data.get('mission_statement'),
        goals = data.get('goals'),
        impact = data.get('impact'),
        image = data.get('image')

        
        if not all([name, image, description, impact, goals, mission_statement, paypal_account]):
            return {'error': '422 Unprocessable Entity'}, 422
        charity = Charity(name=name, paypal_account=paypal_account, image=image, description=description, impact=impact, goals=goals, mission_statement=mission_statement)
        
=======
        name = data.get('name')
        description = data.get('description')
        mission_statement = data.get('mission_statement')
        goals = data.get('goals')
        impact = data.get('impact')
        image = data.get('image')
        if not all([name, image, description, impact, goals, mission_statement]):
            return {'error': '422 Unprocessable Entity'}, 422
        charity = Charity(name=name, image=image, description=description, impact=impact, goals=goals, mission_statement=mission_statement)
>>>>>>> refs/remotes/origin/master
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

<<<<<<< HEAD
    
        
class AdminDecision(Resource):
=======
    def delete(self, id):
        charity = Charity.query.get(id)
        if charity is None:
            return {"error": "charity not found"}, 404
        else:
            db.session.delete(charity)
            db.session.commit()
            return {"result": "success"}
>>>>>>> refs/remotes/origin/master

class AdminDecision(Resource):
    def get(self, id=None):
        if id is None:
            charities = [charity.to_dict() for charity in Charity.query.filter_by(status='pending').all()]
            response = make_response(jsonify(charities), 200)
            return response
<<<<<<< HEAD
#fetch total donation for a charity
class Total(Resource):
=======

class CharityTotalDonations(Resource):
>>>>>>> refs/remotes/origin/master
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

<<<<<<< HEAD

          
 #allow an admin to decide
class Delete(Resource):
    def delete(self, id):
        charity = Charity.query.get(id)
        if charity:
            db.session.delete(charity)
            db.session.commit()
            return True
        return False
=======
>>>>>>> refs/remotes/origin/master
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
        donation = Donation(amount=data['amount'], user_id=data['user_id'], charity_id=data['charity_id'])
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
class PayPalPayment(Resource):
    def post(self):
        data = request.get_json()
        amount = data.get('amount')
        charity_id = data.get('charity_id')
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://localhost:5000/paypal-return",
                "cancel_url": "http://localhost:5000/paypal-cancel"
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": "USD"
                },
                "description": "Donation to charity ID {}".format(charity_id)
            }]
        })

        if payment.create():
            return jsonify({"payment_id": payment.id, "approval_url": payment.links[1].href})
        else:
            return jsonify({"error": payment.error}), 500


class PayPalReturn(Resource):
    def get(self):
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            return jsonify({"message": "Payment completed successfully"})
        else:
            return jsonify({"error": payment.error}), 500


class PayPalCancel(Resource):
    def get(self):
        return jsonify({"message": "Payment was cancelled"})


class StripePayment(Resource):
    def post(self):
        data = request.get_json()
        amount = int(data.get('amount')) * 100  
        currency = data.get('currency', 'usd')
        charity_id = data.get('charity_id')
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                description="Donation to charity ID {}".format(charity_id),
                payment_method_types=['card'],
            )
            return jsonify({
                "client_secret": payment_intent['client_secret'],
                "payment_intent_id": payment_intent['id']
            }), 200
        except stripe.error.StripeError as e:
            return jsonify({"error": str(e)}), 500

#try this payment api 
api.add_resource(PayPalPayment, '/paypal-payment')
api.add_resource(PayPalReturn, '/paypal-return')
api.add_resource(PayPalCancel, '/paypal-cancel')
api.add_resource(StripePayment, '/stripe-payment')


api.add_resource(Total, '/total/<int:id>') 

<<<<<<< HEAD
api.add_resource(Donation, '/donations')
=======
api.add_resource(CharityTotalDonations, '/charities/<int:id>/total_donations') 
api.add_resource(AdminDecision, '/charities/<int:id>') 
api.add_resource(CreateDonation, '/donations')
>>>>>>> refs/remotes/origin/master
api.add_resource(CheckSession, '/check_session', endpoint='check_session')     
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(Charities, "/charities")
api.add_resource(CharityById, "/charities/<int:id>")
api.add_resource(UserById, "/users/<int:id>")
api.add_resource(Users, '/users')
api.add_resource(UserDonationHistory, '/donations/<int:id>') 
api.add_resource(Approve, '/approve/<int:id>')
api.add_resource(Review, '/review/<int:id>')
<<<<<<< HEAD
api.add_resource(Reject, '/reject/<int:id>')
api.add_resource(Delete, '/delete/<int:id>')

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
=======
api.add_resource(Reject, "/reject/<int:id>")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
>>>>>>> refs/remotes/origin/master
