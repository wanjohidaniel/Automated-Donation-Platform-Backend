import os
from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_migrate import Migrate


from models import db, Charity

#DATABASE_URI = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a.oregon-postgres.render.com/asset_db"
DATABASE_URI = os.environ.get("postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a.oregon-postgres.render.com/asset_db")
app = Flask(__name__)
api = Api(app)

os.environ["DB_EXTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a.oregon-postgres.render.com/asset_db"
os.environ["DB_INTERNAL_URL"] = "postgresql://backend_1fsr_user:5Ipy3vtPoazu0UtLmACn4Bo166WjWwCs@dpg-cqjrrotds78s73f486bg-a/asset_db"
# Configure SQLAlchemy database URI based on environment variables
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Set up database URI based on environment (use DB_EXTERNAL_URL by default)
if os.getenv('FLASK_ENV') == 'production':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_INTERNAL_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_EXTERNAL_URL")
    
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

class Charities(Resource):
    def get(self):
        charities = [charity.to_dict() for charity in Charity.query.all()]
        response = make_response(jsonify(charities), 200)
        return response

    def post(self):
        data = request.get_json()
        new_charity = Charity(
            name=data['name'],
            description=data.get('description'),
            mission_statement = data.get('mission_statement'),
            )
        db.session.add(new_charity)
        db.session.commit()
        return jsonify(new_charity.to_dict()), 201
    def put(self, charity_id):
        data = request.get_json()
        charity = Charity.query.get(charity_id)
        if charity is None:
            return {"error": "charity not found"}, 404
        else:
            charity.name = data["name"]
            charity.description = data["description"]
            charity.mission_statement = data["mission_statement"]
            db.session.commit()
            return {"id": charity.id, "name": charity.name, "description": charity.description}

    def delete(self, charity_id):
        charity = Charity.query.get(charity_id)
        if charity is None:
            return {"error": "charity not found"}, 404
        else:
            db.session.delete(charity)
            db.session.commit()
            return {"result": "success"}

api.add_resource(Charities, "/charities", "/charities/<int:charity_id>")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
