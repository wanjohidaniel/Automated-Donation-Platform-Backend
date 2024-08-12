from app import app
from models import db, Charity, User, Donation, Story, RecurringDonation, Reminder
from flask_bcrypt import Bcrypt
from datetime import datetime


with app.app_context():
    print("Deleting existing donations,reminders, recurring doantions and stories....")
    Donation.query.delete()
    Reminder.query.delete()
    RecurringDonation.query.delete()
    Story.query.delete()
    
    print("Deleting existing users....")
    User.query.delete()

    print("creating users....")
    demo = User(username='demo', email='demo@example.com')
    demo.password_hash = 'password'

    Admin = User(username='Admin', email='Admin@example.com', role='admin')
    Admin.password_hash = 'password'

    john = User(username='john', email='john@example.com')
    john.password_hash = 'password'

    alexy = User(username='alexy', email='alexy@example.com')
    alexy.password_hash = 'password'
    print("users created....")
    


    print('Deleting existing Charities...')
    Charity.query.delete()

    print('Creating Charity objects...')
    Charities=[
        Charity(name="Save the Children", image="https://images.unsplash.com/photo-1504384308090-c894fdcc538d", description="Save the Children provides education and emergency aid to children in need around the world, including school-going girls in Sub-Saharan Africa.", mission_statement="To help bring out the best in all children.", goals=[], impact='hahsgddysgwhw', status="approved"),
        Charity(name="Plan International", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International test1", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International test1 focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International test2", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International test2 focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Plan International test3", image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmB01XeoEwG6S3ekPfHxBoq2n0YsLRKCJslA&s",description="Plan International test3 focuses on advancing children's rights and equality for girls, with programs in Sub-Saharan Africa to support education and health.", mission_statement="To provide food to the hungry.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="Girls Not Brides", image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnNoMNAJXsi-Z1GFofWGkl0OUu_mwdfIdUwQ&s', description="TGirls Not Brides is dedicated to ending child marriage and supporting girls' education in Sub-Saharan Africa through advocacy and direct support.", mission_statement="To provide shelter to the homeless.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="jofo", image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnNoMNAJXsi-Z1GFofWGkl0OUu_mwdfIdUwQ&s', description="TGirls Not Brides is dedicated to ending child marriage and supporting girls' education in Sub-Saharan Africa through advocacy and direct support.", mission_statement="To provide shelter to the homeless.", goals=[], impact='hahsgddysgwhw', status="pending"),
        Charity(name="sick", image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnNoMNAJXsi-Z1GFofWGkl0OUu_mwdfIdUwQ&s', description="TGirls Not Brides is dedicated to ending child marriage and supporting girls' education in Sub-Saharan Africa through advocacy and direct support.", mission_statement="To provide shelter to the homeless.", goals=[], impact='hahsgddysgwhw', status="pending"),
    ]
    # Add sample users
    db.session.add_all(Charities)
    db.session.add_all([demo, Admin, john, alexy])


    
    

    print("Creating donations....")
    donations = [
        Donation(amount=100.00, user=alexy, charity=Charities[1]),
        Donation(amount=200.00, user=john, charity=Charities[2]),
        Donation(amount=300.00, user=demo, charity=Charities[3]),
        Donation(amount=300.00, user=john, charity=Charities[4]),
        Donation(amount=300.00, user=john, charity=Charities[5]),
        Donation(amount=300.00, user=john, charity=Charities[6]),
        Donation(amount=300.00, user=john, charity=Charities[7]),
        Donation(amount=300.00, user=john, charity=Charities[8]),
        Donation(amount=300.00, user=john, charity=Charities[9]),
        Donation(amount=300.00, user=john, charity=Charities[0]),
        Donation(amount=300.00, user=john, charity=Charities[2]),
        Donation(amount=300.00, user=john, charity=Charities[2]),
        Donation(amount=300.00, user=demo, charity=Charities[2]),

        
        

    ]

    print("Adding donations, charities and users to transaction...")
    #print("Creating recurring donations....")
    recurring_donations = [
        RecurringDonation(amount=50.00, user=alexy, charity=Charities[1], frequency='monthly', start_date=datetime.utcnow(), next_donation_date=datetime.utcnow()),
        RecurringDonation(amount=75.00, user=john, charity=Charities[0], frequency='monthly', start_date=datetime.utcnow(), next_donation_date=datetime.utcnow())
    ]
    
    print("Creating reminders....")
    reminders = [
        Reminder(message="Don't forget to donate this month!", user=alexy, remind_at=datetime.utcnow()),
        Reminder(message="Monthly donation reminder", user=john, remind_at=datetime.utcnow())
    ]

    print("Creating stories....")
    stories = [
        Story(title="Success Story from Save the Children", content="Thanks to Save the Children, many girls in Sub-Saharan Africa have gained access to education and health services.", charity=Charities[0], image_url="https://example.com/image1.jpg"),
        Story(title="Impact of Plan International", content="Plan International's initiatives have transformed the lives of many girls, providing them with opportunities for a brighter future.", charity=Charities[1], image_url="https://example.com/image2.jpg")
    ]

    print("Adding donations, recurring donations, reminders, stories, charities, and users to transaction...")
    db.session.add_all(donations)
    db.session.add_all(recurring_donations)
    db.session.add_all(reminders)
    db.session.add_all(stories)
    

    
    db.session.add_all(donations)
   
    print('Committing transaction...')
    db.session.commit()

    print('Complete.')