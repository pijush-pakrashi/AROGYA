from app import app
from models import db, Hospital, Doctor

with app.app_context():
    # Mumbai Hospitals
    h1 = Hospital(name="Lilavati Hospital", type="Private", city="Mumbai", address="Bandra West", contact_number="022-2642-1111", rating=4.8)
    h2 = Hospital(name="KEM Hospital", type="Government", city="Mumbai", address="Parel", contact_number="022-2410-7000", rating=4.2)
    
    # Rajasthan Hospitals
    h3 = Hospital(name="SMS Medical College Hospital", type="Government", city="Jaipur", address="JLN Marg", contact_number="0141-256-0291", rating=4.3)
    h4 = Hospital(name="Fortis Escorts Hospital", type="Private", city="Jaipur", address="Malviya Nagar", contact_number="0141-254-7000", rating=4.7)

    db.session.add_all([h1, h2, h3, h4])
    db.session.commit()
    
    print("Added hospitals for Mumbai and Jaipur!")
