from datetime import datetime
from functools import wraps

from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, flash, session
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from flask_cors import CORS

from config import Config
from models import db, User, Doctor, DoctorUnavailability, Appointment, Notification, Hospital, OTPVerification

# App factory

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:3001"])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Unauthorized'}), 401
    return redirect(url_for('login_page', next=request.path))


# Helpers

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return f(*args, **kwargs)
    return decorated


def create_notification(user_id, message, notif_type='info'):
    n = Notification(user_id=user_id, message=message, type=notif_type)
    db.session.add(n)
    db.session.commit()


def seed_admin():
    """Create default admin account if none exists."""
    if not User.query.filter_by(role='admin').first():
        admin = User(name='Admin', email='admin@arogya.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(' * Default admin created -> admin@arogya.com / admin123')


# ===================================================================
#  API  –  AUTHENTICATION & OTP
# ===================================================================
import random
from datetime import datetime, timedelta

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'patient')
    phone = data.get('phone', '').strip()
    city = data.get('city', '').strip()
    address = data.get('address', '').strip()
    age = data.get('age')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if role not in ('patient', 'doctor'):
        return jsonify({'error': 'Invalid role'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=name, email=email, role=role, phone=phone, city=city, address=address, age=age)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # auto-create doctor profile
    if role == 'doctor':
        specialization = data.get('specialization', 'General')
        qualification = data.get('qualification', '')
        department = data.get('department', 'General')
        doctor = Doctor(
            user_id=user.id,
            specialization=specialization,
            qualification=qualification,
            department=department,
        )
        db.session.add(doctor)

    db.session.commit()
    create_notification(user.id, f'Welcome to Arogya, {name}!', 'system')
    login_user(user, remember=True)
    return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    if not user.is_active_user:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    login_user(user, remember=True)
    return jsonify({'message': 'Login successful', 'user': user.to_dict()})


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logged out'})


@app.route('/api/me')
@login_required
def api_me():
    data = current_user.to_dict()
    if current_user.role == 'doctor' and current_user.doctor_profile:
        data['doctor_profile'] = current_user.doctor_profile.to_dict()
    return jsonify(data)


# ===================================================================
#  API  –  HOSPITALS & DOCTORS
# ===================================================================

@app.route('/api/hospitals', methods=['GET'])
def api_hospitals_list():
    location = request.args.get('location', '').strip()
    
    query = Hospital.query
    if location:
        query = query.filter(db.or_(
            Hospital.city.ilike(f'%{location}%'),
            Hospital.address.ilike(f'%{location}%')
        ))
    
    hospitals = query.all()
    
    # Auto-generate mock hospitals if none exist for this city, to make the app feel "real-world"
    if not hospitals and location:
        import random
        # Create 2 private and 2 government hospitals dynamically
        h1 = Hospital(name=f"{location.capitalize()} City Care", type="Private", city=location.capitalize(), address="Central Avenue", contact_number="1800-00-1111", rating=round(random.uniform(4.0, 4.9), 1))
        h2 = Hospital(name=f"Apollo {location.capitalize()}", type="Private", city=location.capitalize(), address="Main Tech Park", contact_number="1800-00-2222", rating=round(random.uniform(4.5, 4.9), 1))
        h3 = Hospital(name=f"Govt General Hospital, {location.capitalize()}", type="Government", city=location.capitalize(), address="District HQ", contact_number="1800-00-3333", rating=round(random.uniform(3.5, 4.5), 1))
        h4 = Hospital(name=f"{location.capitalize()} Civil Hospital", type="Government", city=location.capitalize(), address="Old City", contact_number="1800-00-4444", rating=round(random.uniform(3.8, 4.3), 1))
        
        db.session.add_all([h1, h2, h3, h4])
        db.session.commit()
        hospitals = [h1, h2, h3, h4]

    # Ensure all returned hospitals have at least some doctors for demo purposes
    import random
    import string
    added_docs = False
    for h in hospitals:
        if not h.doctors:
            docs_to_add = []
            for dept in ['Cardiology', 'Neurology', 'General Medicine', 'Orthopedics']:
                if random.choice([True, False, True]): # 66% chance to add
                    # random string to ensure unique email
                    rs = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                    dummy_user = User(name=f"Dr. {dept} Expert", email=f"dr_{dept.lower().replace(' ', '_')}_{h.id}_{rs}@arogya.com", role="doctor")
                    dummy_user.set_password('password')
                    db.session.add(dummy_user)
                    db.session.flush() # get id
                    d = Doctor(user_id=dummy_user.id, hospital_id=h.id, specialization=dept, department=dept, experience=random.randint(5, 20))
                    docs_to_add.append(d)
            if docs_to_add:
                db.session.add_all(docs_to_add)
                added_docs = True

    if added_docs:
        db.session.commit()

    return jsonify([h.to_dict() for h in hospitals])


@app.route('/api/hospitals/<int:hospital_id>', methods=['GET'])
def api_hospital_detail(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    data = hospital.to_dict()
    data['doctors'] = [d.to_dict() for d in hospital.doctors if d.is_available]
    return jsonify(data)


@app.route('/api/doctors')
def api_doctors_list():
    q = request.args.get('q', '').strip()
    dept = request.args.get('department', '').strip()

    query = Doctor.query.join(User).filter(User.is_active_user == True, Doctor.is_available == True)
    if q:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{q}%'),
                Doctor.specialization.ilike(f'%{q}%'),
            )
        )
    if dept:
        query = query.filter(Doctor.department.ilike(f'%{dept}%'))

    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors])


@app.route('/api/doctors/<int:doctor_id>')
def api_doctor_detail(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify(doctor.to_dict())


@app.route('/api/doctors/<int:doctor_id>/slots')
def api_doctor_slots(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    date_str = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    slots = doctor.get_available_slots(date_str)
    return jsonify({'doctor_id': doctor_id, 'date': date_str, 'slots': slots})


# ===================================================================
#  API  –  APPOINTMENTS (patient)
# ===================================================================

@app.route('/api/appointments', methods=['GET'])
@login_required
def api_appointments():
    if current_user.role == 'patient':
        appts = Appointment.query.filter_by(patient_id=current_user.id)\
            .order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    elif current_user.role == 'doctor':
        doc = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doc:
            return jsonify([])
        appts = Appointment.query.filter_by(doctor_id=doc.id)\
            .order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    else:
        appts = Appointment.query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appts])


@app.route('/api/appointments', methods=['POST'])
@login_required
def api_book_appointment():
    if current_user.role != 'patient':
        return jsonify({'error': 'Only patients can book appointments'}), 403

    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time_slot = data.get('time_slot')
    notes = data.get('notes', '')

    if not doctor_id or not date or not time_slot:
        return jsonify({'error': 'Doctor, date, and time slot are required'}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    # Check unavailability
    unavailable = DoctorUnavailability.query.filter_by(doctor_id=doctor_id, date=date).first()
    if unavailable:
        return jsonify({'error': 'Doctor is not available on this date'}), 400

    # Prevent double booking (same doctor, same slot)
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time_slot=time_slot
    ).filter(Appointment.status != 'cancelled').first()
    if existing:
        return jsonify({'error': 'This time slot is not available. Please select another slot.'}), 409

    # Prevent patient double booking at same time
    patient_conflict = Appointment.query.filter_by(
        patient_id=current_user.id, date=date, time_slot=time_slot
    ).filter(Appointment.status != 'cancelled').first()
    if patient_conflict:
        return jsonify({'error': 'You already have an appointment at this time'}), 409

    appt = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        date=date,
        time_slot=time_slot,
        notes=notes,
        status='confirmed',
    )
    db.session.add(appt)
    db.session.commit()

    # Notifications
    doc_name = doctor.user.name if doctor.user else 'Doctor'
    create_notification(
        current_user.id,
        f'Appointment confirmed with Dr. {doc_name} on {date} at {time_slot}.',
        'booking'
    )
    create_notification(
        doctor.user_id,
        f'New appointment with {current_user.name} on {date} at {time_slot}.',
        'booking'
    )

    return jsonify({'message': 'Appointment booked successfully', 'appointment': appt.to_dict()}), 201


@app.route('/api/appointments/<int:appt_id>/cancel', methods=['PUT'])
@login_required
def api_cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if current_user.role == 'patient' and appt.patient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if appt.status == 'cancelled':
        return jsonify({'error': 'Already cancelled'}), 400

    appt.status = 'cancelled'
    db.session.commit()

    create_notification(appt.patient_id, f'Appointment on {appt.date} at {appt.time_slot} has been cancelled.', 'cancellation')
    create_notification(appt.doctor.user_id, f'Appointment with {appt.patient.name} on {appt.date} at {appt.time_slot} was cancelled.', 'cancellation')

    return jsonify({'message': 'Appointment cancelled', 'appointment': appt.to_dict()})


@app.route('/api/appointments/<int:appt_id>/reschedule', methods=['PUT'])
@login_required
def api_reschedule_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if current_user.role == 'patient' and appt.patient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    new_date = data.get('date')
    new_time = data.get('time_slot')
    if not new_date or not new_time:
        return jsonify({'error': 'New date and time slot are required'}), 400

    # Check slot availability
    existing = Appointment.query.filter_by(
        doctor_id=appt.doctor_id, date=new_date, time_slot=new_time
    ).filter(Appointment.status != 'cancelled').first()
    if existing:
        return jsonify({'error': 'This time slot is not available'}), 409

    old_date, old_time = appt.date, appt.time_slot
    appt.date = new_date
    appt.time_slot = new_time
    db.session.commit()

    create_notification(
        appt.patient_id,
        f'Appointment rescheduled from {old_date} {old_time} to {new_date} {new_time}.',
        'reschedule'
    )
    create_notification(
        appt.doctor.user_id,
        f'{appt.patient.name} rescheduled appointment to {new_date} at {new_time}.',
        'reschedule'
    )

    return jsonify({'message': 'Appointment rescheduled', 'appointment': appt.to_dict()})


@app.route('/api/appointments/<int:appt_id>/complete', methods=['PUT'])
@login_required
def api_complete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if current_user.role not in ('doctor', 'admin'):
        return jsonify({'error': 'Unauthorized'}), 403
    appt.status = 'completed'
    db.session.commit()
    create_notification(appt.patient_id, f'Your appointment on {appt.date} has been marked as completed.', 'system')
    return jsonify({'message': 'Marked as completed', 'appointment': appt.to_dict()})


# ===================================================================
#  API  –  DOCTOR SCHEDULE
# ===================================================================

@app.route('/api/doctor/schedule', methods=['GET'])
@login_required
@doctor_required
def api_doctor_schedule():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doc:
        return jsonify({'error': 'Doctor profile not found'}), 404
    return jsonify(doc.to_dict())


@app.route('/api/doctor/schedule', methods=['PUT'])
@login_required
@doctor_required
def api_update_doctor_schedule():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doc:
        return jsonify({'error': 'Doctor profile not found'}), 404

    data = request.get_json()
    if 'working_hours_start' in data:
        doc.working_hours_start = data['working_hours_start']
    if 'working_hours_end' in data:
        doc.working_hours_end = data['working_hours_end']
    if 'slot_duration' in data:
        doc.slot_duration = int(data['slot_duration'])
    if 'is_available' in data:
        doc.is_available = bool(data['is_available'])

    db.session.commit()
    return jsonify({'message': 'Schedule updated', 'doctor': doc.to_dict()})


@app.route('/api/doctor/unavailability', methods=['POST'])
@login_required
@doctor_required
def api_set_unavailability():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()
    date_str = data.get('date')
    reason = data.get('reason', 'Leave')

    if not date_str:
        return jsonify({'error': 'Date is required'}), 400

    existing = DoctorUnavailability.query.filter_by(doctor_id=doc.id, date=date_str).first()
    if existing:
        return jsonify({'error': 'Already marked unavailable'}), 409

    entry = DoctorUnavailability(doctor_id=doc.id, date=date_str, reason=reason)
    db.session.add(entry)

    # Notify all patients with appointments on that date
    affected = Appointment.query.filter_by(
        doctor_id=doc.id, date=date_str
    ).filter(Appointment.status.in_(['confirmed', 'pending'])).all()

    for appt in affected:
        # Change to pending_reschedule instead of outright cancel
        appt.status = 'cancelled'

        # Send a professional, empathetic notification to the patient
        patient_msg = (
            f"⚠️ Important Notice: Dr. {current_user.name} will not be available on {date_str}. "
            f"Your appointment (originally at {appt.time_slot}) has been cancelled. "
            f"Please don't worry — we are arranging the next available slot for you. "
            f"We will notify you as soon as a new appointment is confirmed. Thank you for your patience."
        )
        create_notification(appt.patient_id, patient_msg, 'warning')

        # Also notify the doctor themselves for record
        create_notification(
            doc.user_id,
            f"You are marked unavailable on {date_str}. {appt.patient.name}'s appointment has been cancelled and they've been notified.",
            'info'
        )

    db.session.commit()
    return jsonify({
        'message': f'Marked unavailable on {date_str}. {len(affected)} patient(s) notified.',
        'affected_count': len(affected)
    })


@app.route('/api/doctor/unavailability', methods=['GET'])
@login_required
@doctor_required
def api_get_unavailability():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    entries = DoctorUnavailability.query.filter_by(doctor_id=doc.id).all()
    return jsonify([{'id': e.id, 'date': e.date, 'reason': e.reason} for e in entries])


@app.route('/api/doctor/notify-slot-arranged', methods=['POST'])
@login_required
@doctor_required
def api_notify_slot_arranged():
    """Doctor notifies a patient that a new appointment slot has been arranged."""
    data = request.get_json()
    patient_id = data.get('patient_id')
    new_date = data.get('new_date')
    new_time = data.get('new_time')

    if not patient_id or not new_date or not new_time:
        return jsonify({'error': 'patient_id, new_date, and new_time are required'}), 400

    patient = User.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    msg = (
        f"✅ Good news! Dr. {current_user.name} has arranged your next available appointment slot. "
        f"Your new appointment is scheduled for {new_date} at {new_time}. "
        f"Please confirm or contact the hospital if you need to reschedule. We look forward to seeing you!"
    )
    create_notification(patient_id, msg, 'success')

    return jsonify({'message': f'Patient {patient.name} has been notified about the new slot.'})



@app.route('/api/doctor/appointments', methods=['GET'])
@login_required
@doctor_required
def api_doctor_appointments():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    date_filter = request.args.get('date')
    query = Appointment.query.filter_by(doctor_id=doc.id)
    if date_filter:
        query = query.filter_by(date=date_filter)
    appts = query.order_by(Appointment.date, Appointment.time_slot).all()
    return jsonify([a.to_dict() for a in appts])


# ===================================================================
#  API  –  ADMIN
# ===================================================================

@app.route('/api/admin/dashboard-stats')
@login_required
@admin_required
def api_admin_stats():
    return jsonify({
        'total_patients': User.query.filter_by(role='patient').count(),
        'total_doctors': Doctor.query.count(),
        'total_appointments': Appointment.query.count(),
        'confirmed_appointments': Appointment.query.filter_by(status='confirmed').count(),
        'cancelled_appointments': Appointment.query.filter_by(status='cancelled').count(),
        'completed_appointments': Appointment.query.filter_by(status='completed').count(),
    })


@app.route('/api/admin/doctors', methods=['GET'])
@login_required
@admin_required
def api_admin_doctors():
    doctors = Doctor.query.join(User).all()
    return jsonify([d.to_dict() for d in doctors])


@app.route('/api/admin/doctors', methods=['POST'])
@login_required
@admin_required
def api_admin_add_doctor():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', 'Doctor@123')
    phone = data.get('phone', '')
    specialization = data.get('specialization', '')
    qualification = data.get('qualification', '')
    experience = data.get('experience', 0)
    department = data.get('department', '')
    slot_duration = data.get('slot_duration', 30)
    working_start = data.get('working_hours_start', '09:00')
    working_end = data.get('working_hours_end', '17:00')

    if not name or not email or not specialization:
        return jsonify({'error': 'Name, email and specialization are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=name, email=email, role='doctor', phone=phone)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(
        user_id=user.id,
        specialization=specialization,
        qualification=qualification,
        experience=int(experience),
        department=department,
        slot_duration=int(slot_duration),
        working_hours_start=working_start,
        working_hours_end=working_end,
    )
    db.session.add(doctor)
    db.session.commit()

    create_notification(user.id, f'Welcome to Arogya, Dr. {name}!', 'system')
    return jsonify({'message': 'Doctor added successfully', 'doctor': doctor.to_dict()}), 201


@app.route('/api/admin/doctors/<int:doctor_id>', methods=['PUT'])
@login_required
@admin_required
def api_admin_update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()

    if 'name' in data:
        doctor.user.name = data['name']
    if 'phone' in data:
        doctor.user.phone = data['phone']
    if 'specialization' in data:
        doctor.specialization = data['specialization']
    if 'qualification' in data:
        doctor.qualification = data['qualification']
    if 'experience' in data:
        doctor.experience = int(data['experience'])
    if 'department' in data:
        doctor.department = data['department']
    if 'slot_duration' in data:
        doctor.slot_duration = int(data['slot_duration'])
    if 'working_hours_start' in data:
        doctor.working_hours_start = data['working_hours_start']
    if 'working_hours_end' in data:
        doctor.working_hours_end = data['working_hours_end']

    db.session.commit()
    return jsonify({'message': 'Doctor updated', 'doctor': doctor.to_dict()})


@app.route('/api/admin/doctors/<int:doctor_id>', methods=['DELETE'])
@login_required
@admin_required
def api_admin_delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    # Cancel future appointments & notify patients
    future_appts = Appointment.query.filter_by(doctor_id=doctor_id)\
        .filter(Appointment.status == 'confirmed').all()
    for appt in future_appts:
        appt.status = 'cancelled'
        create_notification(
            appt.patient_id,
            f'Your appointment with Dr. {doctor.user.name} on {appt.date} has been cancelled (doctor removed).',
            'cancellation'
        )

    user = doctor.user
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Doctor removed successfully'})


@app.route('/api/admin/users', methods=['GET'])
@login_required
@admin_required
def api_admin_users():
    role_filter = request.args.get('role')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])


@app.route('/api/admin/users/<int:user_id>/toggle', methods=['PUT'])
@login_required
@admin_required
def api_admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active_user = not user.is_active_user
    db.session.commit()
    status = 'activated' if user.is_active_user else 'deactivated'
    return jsonify({'message': f'User {status}', 'user': user.to_dict()})


@app.route('/api/admin/appointments', methods=['GET'])
@login_required
@admin_required
def api_admin_appointments():
    status_filter = request.args.get('status')
    query = Appointment.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    appts = query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appts])


# ===================================================================
#  API  –  NOTIFICATIONS
# ===================================================================

@app.route('/api/notifications')
@login_required
def api_notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifs])


@app.route('/api/notifications/read', methods=['PUT'])
@login_required
def api_mark_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'})


# ===================================================================
#  TEMPLATE ROUTES  –  Server-side pages
# ===================================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard_page'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active_user:
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard_page'))
            return redirect(url_for('login_page'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('login_page'))


@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    stats = {
        'total_patients': User.query.filter_by(role='patient').count(),
        'total_doctors': Doctor.query.count(),
        'total_hospitals': Hospital.query.count(),
        'total_appointments': Appointment.query.count(),
        'confirmed': Appointment.query.filter_by(status='confirmed').count(),
        'cancelled': Appointment.query.filter_by(status='cancelled').count(),
        'completed': Appointment.query.filter_by(status='completed').count(),
    }
    recent_appts = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    all_doctors = Doctor.query.join(User).all()
    unavailable_entries = DoctorUnavailability.query.order_by(DoctorUnavailability.date.desc()).limit(20).all()
    return render_template('dashboard.html', stats=stats, appointments=recent_appts,
                           all_doctors=all_doctors, unavailable_entries=unavailable_entries, today=today)


@app.route('/admin/doctors')
@login_required
@admin_required
def doctors_page():
    doctors = Doctor.query.join(User).all()
    return render_template('doctors.html', doctors=doctors)


@app.route('/admin/doctors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor_page():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', 'Doctor@123')
        phone = request.form.get('phone', '')
        specialization = request.form.get('specialization', '')
        qualification = request.form.get('qualification', '')
        experience = request.form.get('experience', 0)
        department = request.form.get('department', '')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('add_doctor_page'))

        user = User(name=name, email=email, role='doctor', phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        doctor = Doctor(
            user_id=user.id, specialization=specialization,
            qualification=qualification, experience=int(experience),
            department=department,
        )
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctors_page'))

    return render_template('add_doctor.html')


@app.route('/admin/patients')
@login_required
@admin_required
def patients_page():
    patients = User.query.filter_by(role='patient').order_by(User.created_at.desc()).all()
    return render_template('patients.html', patients=patients)


@app.route('/admin/hospitals')
@login_required
@admin_required
def admin_hospitals_page():
    hospitals = Hospital.query.order_by(Hospital.city, Hospital.name).all()
    return render_template('admin_hospitals.html', hospitals=hospitals)


@app.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments_page():
    all_appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
    all_doctors = Doctor.query.join(User).all()
    patients = User.query.filter_by(role='patient').all()
    return render_template('admin_appointments.html', appointments=all_appts, all_doctors=all_doctors, patients=patients)


@app.route('/admin/notify')
@login_required
@admin_required
def admin_notify_page():
    patients = User.query.filter_by(role='patient').order_by(User.name).all()
    all_doctors = Doctor.query.join(User).all()
    return render_template('admin_notify.html', patients=patients, all_doctors=all_doctors)


# ── Admin API endpoints ─────────────────────────────────────────────

@app.route('/api/admin/doctor/<int:doctor_id>/unavailability', methods=['POST'])
@login_required
@admin_required
def api_admin_set_unavailability(doctor_id):
    """Admin marks a doctor unavailable and notifies affected patients."""
    doc = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    date_str = data.get('date')
    reason = data.get('reason', 'Leave')

    if not date_str:
        return jsonify({'error': 'Date is required'}), 400

    existing = DoctorUnavailability.query.filter_by(doctor_id=doc.id, date=date_str).first()
    if existing:
        return jsonify({'error': 'Already marked unavailable for this date'}), 409

    entry = DoctorUnavailability(doctor_id=doc.id, date=date_str, reason=reason)
    db.session.add(entry)

    # Notify all affected patients
    affected = Appointment.query.filter_by(
        doctor_id=doc.id, date=date_str
    ).filter(Appointment.status.in_(['confirmed', 'pending'])).all()

    for appt in affected:
        appt.status = 'cancelled'
        patient_msg = (
            f"Important Notice: Dr. {doc.user.name} will not be available on {date_str}. "
            f"Your appointment (originally at {appt.time_slot}) has been cancelled. "
            f"Please don't worry - we are arranging the next available slot for you. "
            f"We will notify you as soon as a new appointment is confirmed. Thank you for your patience."
        )
        create_notification(appt.patient_id, patient_msg, 'warning')

    db.session.commit()
    return jsonify({'message': f'Marked unavailable on {date_str}. {len(affected)} patient(s) notified.', 'affected': len(affected)})


@app.route('/api/admin/unavailability/<int:entry_id>', methods=['DELETE'])
@login_required
@admin_required
def api_admin_remove_unavailability(entry_id):
    entry = DoctorUnavailability.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Unavailability entry removed'})


@app.route('/api/admin/notify-patient', methods=['POST'])
@login_required
@admin_required
def api_admin_notify_patient():
    """Admin sends a 'slot arranged' notification to a patient."""
    data = request.get_json()
    patient_id = data.get('patient_id')
    new_date = data.get('new_date')
    new_time = data.get('new_time')
    custom_msg = data.get('message', '')

    if not patient_id:
        return jsonify({'error': 'patient_id is required'}), 400

    patient = User.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    if custom_msg:
        msg = custom_msg
    elif new_date and new_time:
        msg = (
            f"Good news! The hospital has arranged your next available appointment slot. "
            f"Your new appointment is scheduled for {new_date} at {new_time}. "
            f"Please confirm or contact the hospital if you need to reschedule. We look forward to seeing you!"
        )
    else:
        return jsonify({'error': 'Provide new_date + new_time or a custom message'}), 400

    create_notification(patient_id, msg, 'success')
    return jsonify({'message': f'Notification sent to {patient.name} successfully.'})


@app.route('/api/admin/broadcast', methods=['POST'])
@login_required
@admin_required
def api_admin_broadcast():
    """Admin sends a notification to ALL patients."""
    data = request.get_json()
    message = data.get('message', '').strip()
    notif_type = data.get('type', 'info')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    patients = User.query.filter_by(role='patient').all()
    for p in patients:
        create_notification(p.id, message, notif_type)
    return jsonify({'message': f'Broadcast sent to {len(patients)} patient(s) successfully.'})


@app.route('/doctor/dashboard')
@login_required
@doctor_required
def doctor_dashboard_page():
    doc = Doctor.query.filter_by(user_id=current_user.id).first()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    today_appts = Appointment.query.filter_by(doctor_id=doc.id, date=today)\
        .order_by(Appointment.time_slot).all() if doc else []
    all_appts = Appointment.query.filter_by(doctor_id=doc.id)\
        .filter(Appointment.status == 'confirmed')\
        .order_by(Appointment.date, Appointment.time_slot).all() if doc else []
    return render_template('doctor_dashboard.html', doctor=doc, today_appointments=today_appts, appointments=all_appts)



#  MAIN

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True, port=5000)
