from app import app
from models import db, Charity, User, Donation
from flask_bcrypt import Bcrypt


with app.app_context():
    print("Deleting existing donations....")
    Donation.query.delete()
    
    print("Deleting existing users....")
    User.query.delete()

    print("creating users....")
    demo = User(username='demo', email='demo@example.com')
    demo.password_hash = 'password'

    john = User(username='john', email='john@example.com')
    john.password_hash = 'password'

    alexy = User(username='alexy', email='alexy@example.com')
    alexy.password_hash = 'password'
    print("users created....")
    


    print('Deleting existing Charities...')
    Charity.query.delete()

    print('Creating Charity objects...')
    Charities=[
        Charity(name="Charity 1", description="This is charity 1.", mission_statement="To help people in need.", goals=[], impact='hahsgddysgwhw', status="approved"),
        Charity(name="Charity 2", description="This is charity 2.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="approved"),
        Charity(name="Charity 3", description="This is charity 3.", mission_statement="To provide shelter to the homeless.", goals=[], impact='hahsgddysgwhw', status="approved")
    ]
    # Add sample users
    db.session.add_all(Charities)
    db.session.add_all([demo, john, alexy])


    
    

    print("Creating donations....")
    donations = [
        Donation(amount=100.00, user=alexy, charity=Charities[1]),
        Donation(amount=200.00, user=john, charity=Charities[0]),
        Donation(amount=300.00, user=demo, charity=Charities[2]),
    ]

    print("Adding donations, charities and users to transaction...")
    
    
    db.session.add_all(donations)
   
    print('Committing transaction...')
    db.session.commit()

    print('Complete.')