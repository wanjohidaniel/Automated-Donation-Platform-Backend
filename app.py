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

from models import db, Charity, User, Donation, Beneficiary, BeneficiaryStory


app = Flask(__name__)
api = Api(app)

bcrypt = Bcrypt(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

os.environ["DB_EXTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a.oregon-postgres.render.com/charities_donations_db3"
os.environ["DB_INTERNAL_URL"] = "postgresql://postgresql_w2pt_user:C2Vgxw8OmTgcpWPC3VHnG8qYPpOWwnVW@dpg-cqpsak56l47c73ajpk3g-a/charities_donations_db3"

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

# PayPal SDK configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba",
    "client_secret": "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba"
})

# Stripe SDK configuration
stripe.api_key = "sk_test_51PmjikRu6PCl2qiPx5Pr8yKaJzFfVgaHnfsi3mnHL7twXepIMX0GbN54MMqKcdJvG9IqgkfGRRLQJdVkZDgqQGJh00O9U0KPba"


class CharityById(Resource):
    def get(self, id):
        charity = Charity.query.filter_by(id=id).first()
        if charity:
            return make_response(jsonify(charity.to_dict()))
        else:
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
        paypal_account=data.get('paypal_account'),
        description=data.get('description'),
        mission_statement = data.get('mission_statement'),
        goals = data.get('goals'),
        impact = data.get('impact'),
        image = data.get('image')

        
        if not all([name, image, description, impact, goals, mission_statement, paypal_account]):
            return {'error': '422 Unprocessable Entity'}, 422
        charity = Charity(name=name, paypal_account=paypal_account, image=image, description=description, impact=impact, goals=goals, mission_statement=mission_statement)
        
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
    def delete(self, id):
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
        
# Beneficiary Resources 
class BeneficiaryById(Resource): 
    def get(self,id):
        beneficiary = Beneficiary.query.filter_by(id=id).first()
        return make_response(jsonify(beneficiary.to_dict())) 
class Beneficiaries(Resource):
    def get(self): 
        beneficiaries = Beneficiary.query.all() 
        return [beneficiary.to_dict() for beneficiary in beneficiaries], 200 
    def post(self): 
        data = request.get_json() 
        name = data.get('name') 
        description = data.get('description')
        inventory_needs = data.get('inventory_needs') 
        charity_id = data.get('charity_id') 
        
        if not all([name, description, charity_id]):
            return {'error': '422 Unprocessable Entity'}, 422 
        beneficiary = Beneficiary(name=name, description=description, inventory_needs=inventory_needs, charity_id=charity_id)
        db.session.add(beneficiary)
        db.session.commit() 
        return beneficiary.to_dict(), 201 
    def put(self, id):
        data = request.get_json()
        beneficiary = Beneficiary.query.get(id)
        if beneficiary is None: 
            return {"error": "beneficiary not found"}, 404
        else:
            beneficiary.name = data.get("name", beneficiary.name)
        beneficiary.description = data.get("description", beneficiary.description)
        beneficiary.inventory_needs = data.get("inventory_needs", beneficiary.inventory_needs)
        db.session.commit() 
        return {"id": beneficiary.id, "name": beneficiary.name, "description": beneficiary.description} 
class DeleteBeneficiary(Resource): 
    def delete(self, id): 
        beneficiary = Beneficiary.query.get(id)
        
        if beneficiary:
            db.session.delete(beneficiary)
            db.session.commit()
            return True 
        return  False # BeneficiaryStory Resources 
class BeneficiaryStoryById(Resource): 
    def get(self, id): 
        story = BeneficiaryStory.query.filter_by(id=id).first()
        return make_response(jsonify(story.to_dict())) 
class BeneficiaryStories(Resource):
    def get(self):
        stories = BeneficiaryStory.query.all()
        return [story.to_dict() for story in stories], 200 
    def post(self):
        data = request.get_json()
        beneficiary_id = data.get('beneficiary_id') 
        title = data.get('title') 
        content = data.get('content') 
        image_url = data.get('image_url') 
        if not all([beneficiary_id, title, content]): 
            return {'error': '422, Unprocessable Entity'}, 422 
        story = BeneficiaryStory(beneficiary_id=beneficiary_id, title=title, content=content, image_url=image_url) 
        db.session.add(story)
        db.session.commit() 
        return story.to_dict(), 201 
    def put(self, id):
        data = request.get_json() 
        story = BeneficiaryStory.query.get(id) 
        if story is None: 
            return {"error": "story not found"}, 404 
        else:
            story.title = data.get("title", story.title)
            story.content = data.get("content", story.content)
            story.image_url = data.get("image_url", story.image_url) 
            db.session.commit() 
        return{"id": story.id, "title": story.title, "content": story.content, "image_url": story.image_url} 
    def delete(self, id): 
        story = BeneficiaryStory.query.get(id)
        if story:
            db.session.delete(story)
            db.session.commit() 
            return True 
        return False
    
api.add_resource(BeneficiaryById, '/beneficiaries/<int:id>')
api.add_resource(Beneficiaries, '/beneficiaries')
api.add_resource(DeleteBeneficiary, '/beneficiaries/<int:id>/delete')
api.add_resource(BeneficiaryStoryById, '/beneficiary_stories/<int:id>') 
api.add_resource(BeneficiaryStories, '/beneficiary_stories')

#try this payment api 
api.add_resource(PayPalPayment, '/paypal-payment')
api.add_resource(PayPalReturn, '/paypal-return')
api.add_resource(PayPalCancel, '/paypal-cancel')
api.add_resource(StripePayment, '/stripe-payment')


api.add_resource(Total, '/total/<int:id>') 

api.add_resource(Donation, '/donations')
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
api.add_resource(Reject, '/reject/<int:id>')
api.add_resource(Delete, '/delete/<int:id>')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
