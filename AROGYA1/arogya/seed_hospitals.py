from app import app
from models import db, Hospital

HOSPITALS = [
    # Delhi
    {"name": "All India Institute of Medical Sciences (AIIMS)", "type": "Government", "city": "Delhi", "address": "Sri Aurobindo Marg, Ansari Nagar", "contact_number": "011-2658-8500", "rating": 4.9},
    {"name": "Apollo Hospital Delhi", "type": "Private", "city": "Delhi", "address": "Sarita Vihar, Mathura Road", "contact_number": "011-7179-1090", "rating": 4.7},
    {"name": "Safdarjung Hospital", "type": "Government", "city": "Delhi", "address": "Sri Aurobindo Marg, Ansari Nagar West", "contact_number": "011-2673-0000", "rating": 4.3},
    {"name": "Fortis Escorts Heart Institute", "type": "Private", "city": "Delhi", "address": "Okhla Road, Sukhdev Vihar", "contact_number": "011-4713-5000", "rating": 4.6},
    {"name": "Maulana Azad Medical College", "type": "Government", "city": "Delhi", "address": "Bahadur Shah Zafar Marg", "contact_number": "011-2323-2400", "rating": 4.2},

    # Bangalore
    {"name": "Manipal Hospital Bangalore", "type": "Private", "city": "Bangalore", "address": "98, HAL Airport Road", "contact_number": "080-2502-4444", "rating": 4.8},
    {"name": "Bowring and Lady Curzon Hospital", "type": "Government", "city": "Bangalore", "address": "Shivaji Nagar", "contact_number": "080-2286-6000", "rating": 4.1},
    {"name": "Victoria Hospital", "type": "Government", "city": "Bangalore", "address": "Kalasipalya, K.R. Market", "contact_number": "080-2670-1150", "rating": 4.0},
    {"name": "Narayana Health City", "type": "Private", "city": "Bangalore", "address": "258/A, Bommasandra Industrial Area", "contact_number": "080-7122-2222", "rating": 4.7},

    # Chennai
    {"name": "Government General Hospital", "type": "Government", "city": "Chennai", "address": "Park Town", "contact_number": "044-2530-5000", "rating": 4.3},
    {"name": "Apollo Hospitals Chennai", "type": "Private", "city": "Chennai", "address": "21, Greams Lane, Off Greams Road", "contact_number": "044-2829-0200", "rating": 4.8},
    {"name": "Rajiv Gandhi Government General Hospital", "type": "Government", "city": "Chennai", "address": "Park Town", "contact_number": "044-2530-5000", "rating": 4.2},
    {"name": "MIOT International Hospital", "type": "Private", "city": "Chennai", "address": "4/112, Mount Poonamallee Road, Manapakkam", "contact_number": "044-2249-2288", "rating": 4.6},

    # Kolkata
    {"name": "SSKM Hospital (PG Hospital)", "type": "Government", "city": "Kolkata", "address": "244 AJC Bose Road", "contact_number": "033-2223-3230", "rating": 4.2},
    {"name": "Medica Superspecialty Hospital", "type": "Private", "city": "Kolkata", "address": "127 Mukundapur, Eastern Metropolitan Bypass", "contact_number": "033-6652-0000", "rating": 4.7},
    {"name": "Calcutta Medical College", "type": "Government", "city": "Kolkata", "address": "88, College Street", "contact_number": "033-2241-6640", "rating": 4.1},
    {"name": "Apollo Gleneagles Hospital", "type": "Private", "city": "Kolkata", "address": "58 Canal Circular Road", "contact_number": "033-2320-3040", "rating": 4.6},

    # Hyderabad
    {"name": "Yashoda Hospitals", "type": "Private", "city": "Hyderabad", "address": "Behind Hari Hara Kala Bhavan, SP Road, Secunderabad", "contact_number": "040-4567-4567", "rating": 4.7},
    {"name": "Gandhi Hospital", "type": "Government", "city": "Hyderabad", "address": "Ministers Road, Secunderabad", "contact_number": "040-2754-0000", "rating": 4.0},
    {"name": "Care Hospitals", "type": "Private", "city": "Hyderabad", "address": "Exhibition Road, Nampally", "contact_number": "040-3041-8888", "rating": 4.5},

    # Pune
    {"name": "Sassoon General Hospital", "type": "Government", "city": "Pune", "address": "Jai Prakash Narayan Road, Sangamwadi", "contact_number": "020-2661-2000", "rating": 4.0},
    {"name": "Ruby Hall Clinic", "type": "Private", "city": "Pune", "address": "40, Sassoon Road", "contact_number": "020-6645-5000", "rating": 4.7},
    {"name": "Jehangir Hospital", "type": "Private", "city": "Pune", "address": "32, Sassoon Road", "contact_number": "020-6681-5000", "rating": 4.6},

    # Ahmedabad
    {"name": "Civil Hospital Ahmedabad", "type": "Government", "city": "Ahmedabad", "address": "Asarwa", "contact_number": "079-2268-6000", "rating": 4.1},
    {"name": "Sterling Hospital", "type": "Private", "city": "Ahmedabad", "address": "Gurukul Road, Memnagar", "contact_number": "079-4000-4000", "rating": 4.6},

    # Lucknow
    {"name": "King George's Medical University (KGMU)", "type": "Government", "city": "Lucknow", "address": "Shah Mina Road, Chowk", "contact_number": "0522-225-7540", "rating": 4.5},
    {"name": "Sahara Hospital", "type": "Private", "city": "Lucknow", "address": "Viraj Khand, Gomti Nagar", "contact_number": "0522-675-0000", "rating": 4.5},
]

with app.app_context():
    added = 0
    for h in HOSPITALS:
        exists = Hospital.query.filter_by(name=h["name"], city=h["city"]).first()
        if not exists:
            hosp = Hospital(**h)
            db.session.add(hosp)
            added += 1
    db.session.commit()
    print(f"Added {added} real-world hospitals across major Indian cities!")
