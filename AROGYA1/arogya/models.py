from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # patient, doctor, admin
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(100), default='')
    address = db.Column(db.Text, default='')
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    appointments_as_patient = db.relationship(
        'Appointment', backref='patient', foreign_keys='Appointment.patient_id', cascade='all, delete-orphan'
    )
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'age': self.age,
            'city': self.city,
            'address': self.address,
            'is_active': self.is_active_user,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }




class Hospital(db.Model):
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'Private', 'Government'
    city = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20))
    rating = db.Column(db.Float, default=4.0)
    opening_hours = db.Column(db.String(100), default="24/7")
    map_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    doctors = db.relationship('Doctor', backref='hospital', cascade='all, delete-orphan')

    def to_dict(self):
        import urllib.parse
        map_link = self.map_url
        if not map_link:
            query = urllib.parse.quote(f"{self.name} {self.city}")
            map_link = f"https://maps.google.com/?q={query}"
            
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'city': self.city,
            'address': self.address,
            'contact_number': self.contact_number,
            'rating': self.rating,
            'opening_hours': self.opening_hours,
            'map_url': map_link,
            'doctors_count': len(self.doctors)
        }


class OTPVerification(db.Model):
    __tablename__ = 'otp_verifications'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(200))
    experience = db.Column(db.Integer, default=0)
    department = db.Column(db.String(100))
    slot_duration = db.Column(db.Integer, default=30)  # minutes
    working_hours_start = db.Column(db.String(10), default='09:00')
    working_hours_end = db.Column(db.String(10), default='17:00')
    is_available = db.Column(db.Boolean, default=True)

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', cascade='all, delete-orphan')
    unavailable_dates = db.relationship('DoctorUnavailability', backref='doctor', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hospital_id': self.hospital_id,
            'hospital_name': self.hospital.name if self.hospital else None,
            'name': self.user.name if self.user else '',
            'email': self.user.email if self.user else '',
            'phone': self.user.phone if self.user else '',
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience': self.experience,
            'department': self.department,
            'slot_duration': self.slot_duration,
            'working_hours_start': self.working_hours_start,
            'working_hours_end': self.working_hours_end,
            'is_available': self.is_available,
        }

    def get_available_slots(self, date_str):
        """Generate available time slots for a given date."""
        from datetime import datetime, timedelta

        start = datetime.strptime(self.working_hours_start, '%H:%M')
        end = datetime.strptime(self.working_hours_end, '%H:%M')
        delta = timedelta(minutes=self.slot_duration)

        # Check if date is marked unavailable
        unavailable = DoctorUnavailability.query.filter_by(
            doctor_id=self.id, date=date_str
        ).first()
        if unavailable:
            return []

        # Get booked slots for this date
        booked = Appointment.query.filter_by(
            doctor_id=self.id, date=date_str
        ).filter(Appointment.status != 'cancelled').all()
        booked_times = {a.time_slot for a in booked}

        slots = []
        current = start
        while current + delta <= end:
            slot_str = current.strftime('%H:%M')
            slots.append({
                'time': slot_str,
                'available': slot_str not in booked_times
            })
            current += delta

        return slots


class DoctorUnavailability(db.Model):
    __tablename__ = 'doctor_unavailability'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    reason = db.Column(db.String(200))


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    time_slot = db.Column(db.String(10), nullable=False)  # HH:MM
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else '',
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.user.name if self.doctor and self.doctor.user else '',
            'specialization': self.doctor.specialization if self.doctor else '',
            'department': self.doctor.department if self.doctor else '',
            'date': self.date,
            'time_slot': self.time_slot,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')  # booking, cancellation, reschedule, system
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }
