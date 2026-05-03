from app import app
from models import db, User, Doctor, Hospital

def seed():
    with app.app_context():
        # db.drop_all() # optional if starting fresh, we deleted the db file
        db.create_all()

        if Hospital.query.count() == 0:
            hospitals = [
                # Private Hospitals
                Hospital(name="Apollo Gleneagles Hospital", type="Private", city="Kolkata", address="58 Canal Circular Road, Kolkata", contact_number="1860-500-1066", rating=4.8, opening_hours="24/7", map_url="https://maps.example.com/apollo"),
                Hospital(name="Fortis Hospital", type="Private", city="Kolkata", address="730 Anandapur, E.M. Bypass Road, Kolkata", contact_number="1860-200-0011", rating=4.7, opening_hours="24/7", map_url="https://maps.example.com/fortis"),
                Hospital(name="AMRI Hospitals", type="Private", city="Kolkata", address="Salt Lake, Kolkata", contact_number="033-6680-0000", rating=4.5, opening_hours="24/7", map_url="https://maps.example.com/amri"),
                Hospital(name="Woodlands Hospital", type="Private", city="Kolkata", address="Alipore, Kolkata", contact_number="033-2456-7075", rating=4.6, opening_hours="24/7", map_url="https://maps.example.com/woodlands"),
                Hospital(name="Ruby General Hospital", type="Private", city="Kolkata", address="Kasba Golpark, EM Bypass, Kolkata", contact_number="033-3987-1800", rating=4.4, opening_hours="24/7", map_url="https://maps.example.com/ruby"),
                
                # Govt Hospitals
                Hospital(name="SSKM Hospital", type="Government", city="Kolkata", address="244 AJC Bose Road, Kolkata", contact_number="033-2223-1589", rating=4.2, opening_hours="24/7", map_url="https://maps.example.com/sskm"),
                Hospital(name="Calcutta Medical College", type="Government", city="Kolkata", address="88 College St, Kolkata", contact_number="033-2212-3796", rating=4.3, opening_hours="24/7", map_url="https://maps.example.com/cmc"),
                Hospital(name="NRS Medical College and Hospital", type="Government", city="Kolkata", address="138 AJC Bose Road, Sealdah, Kolkata", contact_number="033-2286-0033", rating=4.1, opening_hours="24/7", map_url="https://maps.example.com/nrs"),
                Hospital(name="R.G. Kar Medical College", type="Government", city="Kolkata", address="1 Khudiram Bose Sarani, Kolkata", contact_number="033-2555-7656", rating=4.0, opening_hours="24/7", map_url="https://maps.example.com/rgkar"),
                Hospital(name="National Medical College", type="Government", city="Kolkata", address="32 Gorachand Road, Beniapukur, Kolkata", contact_number="033-2284-4834", rating=4.1, opening_hours="24/7", map_url="https://maps.example.com/national"),
            ]
            db.session.bulk_save_objects(hospitals)
            db.session.commit()
            print("Seeded hospitals")

        if User.query.filter_by(role='admin').count() == 0:
            admin = User(name='Admin', email='admin@arogya.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Seeded admin")
        
        if Doctor.query.count() == 0:
            hospitals = Hospital.query.all()
            doc_idx = 1
            for h in hospitals:
                for i in range(2): # 2 doctors per hospital
                    email = f"doc{doc_idx}@arogya.com"
                    u = User(name=f"Doctor {doc_idx}", email=email, role='doctor', phone=f"9876543{doc_idx:03d}")
                    u.set_password("Doctor@123")
                    db.session.add(u)
                    db.session.flush()

                    d = Doctor(
                        user_id=u.id,
                        hospital_id=h.id,
                        specialization="General Physician" if i == 0 else "Cardiologist",
                        department="General" if i == 0 else "Cardiology",
                        experience=5 + doc_idx,
                    )
                    db.session.add(d)
                    doc_idx += 1
            db.session.commit()
            print("Seeded doctors")

if __name__ == '__main__':
    seed()
