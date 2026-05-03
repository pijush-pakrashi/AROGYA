# 🏥 Arogya – Hospital Appointment Management System

A full-stack web application for managing hospital appointments, built with **Flask** (backend) and **React** (frontend).

## Features

- **Patient Portal**: Register, search doctors, book/cancel/reschedule appointments
- **Doctor Dashboard**: View schedule, manage availability, mark appointments complete
- **Admin Panel**: Manage doctors & patients, view system stats, monitor appointments
- **Notifications**: Real-time notifications for bookings, cancellations, and reschedules
- **Role-Based Access**: Separate interfaces for patients, doctors, and administrators
- **Secure Auth**: Password hashing (werkzeug), session-based login, CORS protection

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3, Flask, SQLAlchemy       |
| Database  | SQLite                            |
| Frontend  | React 18, React Router, Axios     |
| Auth      | Flask-Login, Werkzeug             |
| Styling   | Custom CSS (templates) + Inline (React) |

## Project Structure

```
AROGYA1/
├── arogya/                   # Flask Backend
│   ├── app.py                # Main app + API routes
│   ├── config.py             # Configuration
│   ├── models.py             # Database models
│   ├── static/style.css      # Template styles
│   └── templates/            # Jinja2 HTML templates
│       ├── login.html
│       ├── dashboard.html
│       ├── doctor_dashboard.html
│       ├── doctors.html
│       ├── patients.html
│       └── add_doctor.html
│
├── frontend/                 # React Frontend
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js            # Routes + Auth + Pages
│   │   ├── index.js
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   └── Login.jsx
│   │   └── components/
│   │       ├── Register.jsx
│   │       └── Register.css
│   └── package.json
│
└── README.md
```

## 🚀 How to Run the Project

### The Easiest Way (Windows)
We've included a convenient batch script that will start both the backend and frontend servers simultaneously for you.

1. Double-click the `start_servers.bat` file in the root `AROGYA1` folder.
2. Two terminal windows will open automatically.
3. The React app will launch in your browser at `http://localhost:3000`.
4. The Flask admin panel is available at `http://localhost:5000/admin/dashboard`.

---

### Manual Setup (Step-by-Step)

If you prefer to run the servers manually or are on Mac/Linux:

#### 1. Backend Setup
Open a terminal and run:
```bash
cd arogya
pip install flask flask-sqlalchemy flask-login flask-cors werkzeug
python app.py
```
The server will start at **http://localhost:5000**.
*(Note: The database and a default admin account will be automatically created when you run `app.py` for the first time).*

#### 2. Frontend Setup
Open a second, separate terminal and run:
```bash
cd frontend
npm install
npm start
```
The React dev server will start at **http://localhost:3000**.

## Default Credentials

| Role   | Email             | Password  |
|--------|-------------------|-----------|
| Admin  | admin@arogya.com  | admin123  |

## API Endpoints

### Authentication
- `POST /api/register` – Register new user
- `POST /api/login` – Login
- `POST /api/logout` – Logout
- `GET /api/me` – Current user info

### Doctors (Public)
- `GET /api/doctors` – List doctors (search: `?q=`, `?department=`)
- `GET /api/doctors/:id/slots?date=` – Available slots

### Appointments (Patient)
- `GET /api/appointments` – My appointments
- `POST /api/appointments` – Book appointment
- `PUT /api/appointments/:id/cancel` – Cancel
- `PUT /api/appointments/:id/reschedule` – Reschedule

### Doctor Schedule
- `GET /api/doctor/schedule` – View schedule
- `PUT /api/doctor/schedule` – Update schedule
- `POST /api/doctor/unavailability` – Mark unavailable dates

### Admin
- `GET /api/admin/dashboard-stats` – System stats
- `GET/POST /api/admin/doctors` – List/Add doctors
- `PUT/DELETE /api/admin/doctors/:id` – Update/Remove doctor
- `GET /api/admin/users` – List users

### Notifications
- `GET /api/notifications` – User notifications
- `PUT /api/notifications/read` – Mark all read

---

## 📸 System Walkthrough & Features

### 1. Patient Portal (React Frontend)
The frontend provides a modern, responsive interface for patients to discover hospitals and book appointments.
- **Hospital Discovery:** Search for hospitals by city (e.g., Bangalore, Delhi, Pune).
- **Doctor Profiles:** View detailed doctor profiles with experience, consultation fees, and real-time availability.
- **Smart Booking:** Book appointments with an intuitive date/time picker.

> *(Add your screenshot here: `![Patient Dashboard](docs/patient-portal.png)`)*

### 2. Premium Admin Dashboard (Flask Backend)
A highly polished, administrative interface built with Jinja2 and custom CSS.
- **Overview Stats:** Instantly view total patients, doctors, hospitals, and appointment metrics.
- **Appointment Control:** Cancel or mark appointments as completed. Filter by status (Pending, Confirmed, Cancelled).
- **Doctor Management:** Add new doctors, view their profiles, and manage their availability status.

> *(Add your screenshot here: `![Admin Dashboard](docs/admin-dashboard.png)`)*

### 3. Doctor Dashboard
Each doctor has their own dedicated portal to manage their daily schedule.
- **My Schedule:** View today's appointments and upcoming confirmed bookings.
- **Patient Notes:** Review patient information before the consultation.

> *(Add your screenshot here: `![Doctor Dashboard](docs/doctor-dashboard.png)`)*

### 4. Advanced Notification System
A robust alerting system keeps patients informed of critical updates.
- **Slot Arranged Notification:** Admins can manually trigger a notification to a patient when a new slot is found.
- **Doctor Unavailability System:** When an admin marks a doctor as unavailable for a specific date, all affected patients receive an automated, empathetic alert letting them know their appointment is paused while a new slot is arranged.
- **System Broadcasts:** Send announcements to all registered patients simultaneously.

**Author**: Pijush Pakrashi – Heritage Institute of Technology  
**Version**: 1.0 | © 2026
