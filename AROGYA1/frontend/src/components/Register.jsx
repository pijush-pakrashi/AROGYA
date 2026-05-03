import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import './Register.css';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '', email: '', password: '', confirmPassword: '',
    role: 'patient', phone: '', age: '', city: '', address: '', specialization: '', department: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className="register-wrapper">
      <div className="register-card">
        <h1 className="register-title">🏥 Create Account</h1>
        <p className="register-subtitle">Join Arogya and manage your health appointments</p>

        {error && <div className="register-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="register-form-row">
            <div className="register-form-group">
              <label>Full Name *</label>
              <input type="text" value={form.name} onChange={update('name')} placeholder="John Doe" required />
            </div>
            <div className="register-form-group">
              <label>Email Address *</label>
              <input type="email" value={form.email} onChange={update('email')} placeholder="you@email.com" required />
            </div>
          </div>

          <div className="register-form-row">
            <div className="register-form-group">
              <label>Password *</label>
              <input type="password" value={form.password} onChange={update('password')} placeholder="Min 8 characters" required />
            </div>
            <div className="register-form-group">
              <label>Confirm Password *</label>
              <input type="password" value={form.confirmPassword} onChange={update('confirmPassword')} placeholder="Re-enter password" required />
            </div>
          </div>

          <div className="register-form-row">
            <div className="register-form-group">
              <label>Phone</label>
              <input type="tel" value={form.phone} onChange={update('phone')} placeholder="+91 9876543210" />
            </div>
            <div className="register-form-group">
              <label>Age</label>
              <input type="number" value={form.age} onChange={update('age')} placeholder="e.g. 25" min="1" max="120" />
            </div>
          </div>

          <div className="register-form-row">
            <div className="register-form-group">
              <label>Register as *</label>
              <select value={form.role} onChange={update('role')}>
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
              </select>
            </div>
            <div className="register-form-group" style={{visibility: 'hidden'}}>
              {/* Layout placeholder */}
            </div>
          </div>

          <div className="register-form-row">
            <div className="register-form-group">
              <label>City *</label>
              <input type="text" value={form.city} onChange={update('city')} placeholder="Mumbai, Jaipur, etc." required />
            </div>
            <div className="register-form-group">
              <label>Address *</label>
              <input type="text" value={form.address} onChange={update('address')} placeholder="123 Main St" required />
            </div>
          </div>

          {form.role === 'doctor' && (
            <div className="register-form-row">
              <div className="register-form-group">
                <label>Specialization *</label>
                <select value={form.specialization} onChange={update('specialization')} required>
                  <option value="">Select</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Dermatology">Dermatology</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Orthopedics">Orthopedics</option>
                  <option value="Pediatrics">Pediatrics</option>
                  <option value="Gynecology">Gynecology</option>
                  <option value="General Medicine">General Medicine</option>
                  <option value="ENT">ENT</option>
                  <option value="Ophthalmology">Ophthalmology</option>
                  <option value="Dentistry">Dentistry</option>
                </select>
              </div>
              <div className="register-form-group">
                <label>Department *</label>
                <select value={form.department} onChange={update('department')} required>
                  <option value="">Select</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Dermatology">Dermatology</option>
                  <option value="Neurology">Neurology</option>
                  <option value="Orthopedics">Orthopedics</option>
                  <option value="Pediatrics">Pediatrics</option>
                  <option value="General Medicine">General Medicine</option>
                  <option value="ENT">ENT</option>
                </select>
              </div>
            </div>
          )}

          <button type="submit" className="register-btn" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="register-footer">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}
