import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (user) {
    navigate('/');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={wrapper}>
      <div style={card}>
        <h1 style={title}>🏥 Arogya</h1>
        <p style={subtitle}>Sign in to your account</p>

        {error && <div style={errorBox}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={formGroup}>
            <label style={label}>Email Address</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="Enter your email" required style={input} />
          </div>
          <div style={formGroup}>
            <label style={label}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="Enter your password" required style={input} />
          </div>
          <button type="submit" disabled={loading} style={btn}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={footerText}>
          Don't have an account? <Link to="/register" style={{color:'#764ba2', fontWeight:600}}>Sign Up</Link>
        </p>
      </div>
    </div>
  );
}

const wrapper = { minHeight:'calc(100vh - 60px)', display:'flex', alignItems:'center', justifyContent:'center', background:'linear-gradient(135deg,#667eea 0%,#764ba2 100%)', padding:'2rem' };
const card = { background:'#fff', borderRadius:'16px', boxShadow:'0 20px 60px rgba(0,0,0,.3)', padding:'3rem 2.5rem', maxWidth:'420px', width:'100%', textAlign:'center' };
const title = { fontSize:'2rem', background:'linear-gradient(135deg,#667eea,#764ba2)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', marginBottom:'0.25rem' };
const subtitle = { color:'#6c757d', fontSize:'0.9rem', marginBottom:'2rem' };
const formGroup = { marginBottom:'1.25rem', textAlign:'left' };
const label = { display:'block', marginBottom:'0.4rem', fontWeight:600, fontSize:'0.9rem', color:'#495057' };
const input = { width:'100%', padding:'0.7rem 0.9rem', border:'2px solid #dee2e6', borderRadius:'8px', fontSize:'0.95rem', fontFamily:'inherit', outline:'none', boxSizing:'border-box' };
const btn = { width:'100%', padding:'0.8rem', background:'linear-gradient(135deg,#667eea,#764ba2)', color:'#fff', border:'none', borderRadius:'8px', fontSize:'1rem', fontWeight:700, cursor:'pointer', fontFamily:'inherit' };
const errorBox = { background:'#f8d7da', color:'#842029', padding:'0.75rem', borderRadius:'8px', marginBottom:'1rem', fontSize:'0.9rem' };
const footerText = { marginTop:'1.5rem', fontSize:'0.85rem', color:'#6c757d' };
