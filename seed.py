from app import app
from models import db, Charity, User
from flask_bcrypt import Bcrypt


with app.app_context():
    print("Deleting existing users....")
    User.query.delete()

    print("creating users....")
    demo = User(username='demo', email='demo@example.com')
    demo.password_hash = 'password'

    john = User(username='john', email='john@example.com')
    john.password_hash = 'password'
    print("users created....")


    print('Deleting existing Charities...')
    Charity.query.delete()

    print('Creating Charity objects...')
    Charities=[
        Charity(name="Charity 1", description="This is charity 1.", mission_statement="To help people in need."),
        Charity(name="Charity 2", description="This is charity 2.", mission_statement="To provide food to the hungry."),
        Charity(name="Charity 3", description="This is charity 3.", mission_statement="To provide shelter to the homeless.")
    ]
    # Add sample users


    print('Adding Charity objects to transaction...')
    db.session.add_all(Charities)
    db.session.add_all([demo, john])
   
    print('Committing transaction...')
    db.session.commit()

    print('Complete.')