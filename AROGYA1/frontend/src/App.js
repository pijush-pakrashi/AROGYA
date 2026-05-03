import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './components/Register';
import HospitalDetail from './pages/HospitalDetail';

/* ── Axios defaults ─────────────────────────────────────────── */
axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.withCredentials = true;

/* ── Auth Context ───────────────────────────────────────────── */
const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUser = useCallback(async () => {
    try {
      const res = await axios.get('/api/me');
      setUser(res.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchUnread = useCallback(async () => {
    try {
      const res = await axios.get('/api/notifications');
      setUnreadCount(res.data.filter(n => !n.is_read).length);
    } catch {
      setUnreadCount(0);
    }
  }, []);

  useEffect(() => { fetchUser(); }, [fetchUser]);

  // Poll for new notifications every 3s when logged in for real-time feel
  useEffect(() => {
    if (!user) return;
    fetchUnread();
    const interval = setInterval(fetchUnread, 3000);
    return () => clearInterval(interval);
  }, [user, fetchUnread]);

  const login = async (email, password) => {
    const res = await axios.post('/api/login', { email, password });
    setUser(res.data.user);
    return res.data;
  };

  const register = async (data) => {
    const res = await axios.post('/api/register', data);
    setUser(res.data.user);
    return res.data;
  };

  const logout = async () => {
    await axios.post('/api/logout');
    setUser(null);
    setUnreadCount(0);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, fetchUser, unreadCount, setUnreadCount }}>
      {children}
    </AuthContext.Provider>
  );
}

/* ── Protected Route ────────────────────────────────────────── */
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{ textAlign: 'center', padding: '4rem', color: '#6c757d' }}>Loading...</div>;
  if (!user) return <Navigate to="/register" />;
  return children;
}

/* ── Navbar ─────────────────────────────────────────────────── */
function Navbar() {
  const { user, logout, unreadCount } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav style={styles.nav}>
      <Link to={user ? '/' : '/login'} style={styles.brand}>🏥 Arogya</Link>
      <div style={styles.navLinks}>
        {user ? (
          <>
            <Link to="/" style={styles.navLink}>🏠 Home</Link>
            <Link to="/appointments" style={styles.navLink}>📅 My Appointments</Link>
            <Link to="/notifications" style={{ ...styles.navLink, position: 'relative' }}>
              🔔 Notifications
              {unreadCount > 0 && (
                <span style={styles.notifBadge}>{unreadCount > 9 ? '9+' : unreadCount}</span>
              )}
            </Link>
            <Link to="/profile" style={{...styles.navUser, textDecoration: 'none', cursor: 'pointer'}}>👤 {user.name}</Link>
            <button onClick={handleLogout} style={styles.navBtn}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" style={styles.navLink}>Login</Link>
            <Link to="/register" style={styles.navLinkHighlight}>Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

/* ── Profile Page ───────────────────────────────────────────── */
function ProfilePage() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <div style={{ background: '#f8f9fa', minHeight: '100vh', padding: '3rem 0' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', background: '#fff', borderRadius: '16px', padding: '2rem', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '1.5rem', color: '#1A1D27' }}>👤 My Profile</h1>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={styles.profileRow}><strong>Name:</strong> <span>{user.name}</span></div>
          <div style={styles.profileRow}><strong>Email:</strong> <span>{user.email}</span></div>
          <div style={styles.profileRow}><strong>Role:</strong> <span style={{textTransform: 'capitalize'}}>{user.role}</span></div>
          <div style={styles.profileRow}><strong>Phone:</strong> <span>{user.phone || 'Not provided'}</span></div>
          <div style={styles.profileRow}><strong>Age:</strong> <span>{user.age || 'Not provided'}</span></div>
          <div style={styles.profileRow}><strong>City:</strong> <span>{user.city || 'Not provided'}</span></div>
          <div style={styles.profileRow}><strong>Address:</strong> <span>{user.address || 'Not provided'}</span></div>
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #eaeaea', textAlign: 'center', color: '#6c757d', fontSize: '0.9rem' }}>
            Account Created: {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Appointments Page ──────────────────────────────────────── */
function AppointmentsPage() {
  const [appointments, setAppointments] = useState([]);
  const [message, setMessage] = useState('');
  const [reschedule, setReschedule] = useState(null);
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');

  const fetchAppts = useCallback(async () => {
    try {
      const r = await axios.get('/api/appointments');
      setAppointments(r.data);
    } catch {}
  }, []);

  useEffect(() => { fetchAppts(); }, [fetchAppts]);

  const cancelAppt = async (id) => {
    if (!window.confirm('Cancel this appointment?')) return;
    try {
      await axios.put(`/api/appointments/${id}/cancel`);
      setMessage('✅ Appointment cancelled.');
      fetchAppts();
    } catch (e) { setMessage('❌ ' + (e.response?.data?.error || 'Cancel failed')); }
  };

  const doReschedule = async (id) => {
    try {
      await axios.put(`/api/appointments/${id}/reschedule`, { date: newDate, time_slot: newTime });
      setMessage('✅ Appointment rescheduled.');
      setReschedule(null);
      fetchAppts();
    } catch (e) { setMessage('❌ ' + (e.response?.data?.error || 'Reschedule failed')); }
  };

  return (
    <div style={{ background: '#f8f9fa', minHeight: '100vh', padding: '2rem 0' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '0 1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '1.5rem', color: '#1A1D27' }}>📅 My Appointments</h1>

        {message && (
          <div style={{ padding: '1rem', borderRadius: '10px', marginBottom: '1.5rem', fontWeight: 500,
            background: message.startsWith('✅') ? '#d1fae5' : '#fee2e2',
            color: message.startsWith('✅') ? '#065f46' : '#991b1b' }}>
            {message}
          </div>
        )}

        {appointments.length === 0 ? (
          <div style={{ background: '#fff', borderRadius: '16px', padding: '4rem', textAlign: 'center', color: '#6c757d', boxShadow: '0 2px 12px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
            <h3 style={{ margin: 0 }}>No Appointments Yet</h3>
            <p>Find a hospital on the Home page and book your first appointment.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {appointments.map(a => (
              <div key={a.id} style={{ background: '#fff', borderRadius: '16px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', padding: '1.5rem', borderLeft: `4px solid ${a.status === 'confirmed' ? '#2D68FE' : a.status === 'cancelled' ? '#dc3545' : '#2E7D32'}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <h3 style={{ margin: 0, color: '#1A1D27' }}>Dr. {a.doctor_name}</h3>
                  <span style={{ padding: '0.3rem 0.85rem', borderRadius: '50px', fontSize: '0.78rem', fontWeight: 700, textTransform: 'uppercase',
                    background: a.status === 'confirmed' ? '#E6F0FF' : a.status === 'cancelled' ? '#FFF0F0' : '#F0F8F0',
                    color: a.status === 'confirmed' ? '#2D68FE' : a.status === 'cancelled' ? '#dc3545' : '#2E7D32' }}>
                    {a.status}
                  </span>
                </div>
                {a.hospital_name && <p style={{ color: '#6c757d', margin: '0.2rem 0', fontSize: '0.9rem' }}>🏥 {a.hospital_name}</p>}
                <p style={{ color: '#6c757d', margin: '0.2rem 0', fontSize: '0.9rem' }}>{a.specialization} • {a.department}</p>
                <p style={{ margin: '0.5rem 0', fontWeight: 600 }}>📅 {a.date} at {a.time_slot}</p>
                {a.notes && <p style={{ color: '#6c757d', fontSize: '0.85rem', margin: 0 }}>📝 {a.notes}</p>}

                {a.status === 'confirmed' && (
                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                    <button onClick={() => cancelAppt(a.id)} style={styles.btnDanger}>Cancel</button>
                    <button onClick={() => { setReschedule(a.id); setNewDate(a.date); setNewTime(a.time_slot); }} style={styles.btnOutline}>Reschedule</button>
                  </div>
                )}

                {reschedule === a.id && (
                  <div style={{ marginTop: '1rem', padding: '1.25rem', background: '#f8f9fa', borderRadius: '12px' }}>
                    <label style={styles.label}>New Date</label>
                    <input type="date" value={newDate} onChange={e => setNewDate(e.target.value)} style={styles.input} min={new Date().toISOString().split('T')[0]} />
                    <label style={{ ...styles.label, marginTop: '0.75rem' }}>New Time Slot</label>
                    <input type="time" value={newTime} onChange={e => setNewTime(e.target.value)} style={styles.input} />
                    <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
                      <button onClick={() => doReschedule(a.id)} style={styles.btnPrimary}>Confirm</button>
                      <button onClick={() => setReschedule(null)} style={styles.btnOutline}>Cancel</button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Notifications Page ─────────────────────────────────────── */
function NotificationsPage() {
  const { setUnreadCount } = useAuth();
  const [notifs, setNotifs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('/api/notifications')
      .then(r => setNotifs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
    axios.put('/api/notifications/read')
      .then(() => setUnreadCount(0))
      .catch(() => {});
  }, [setUnreadCount]);

  const typeConfig = {
    booking:      { icon: '📅', bg: '#EFF6FF', border: '#2D68FE', text: '#1e40af', label: 'Appointment Booked' },
    cancellation: { icon: '❌', bg: '#FFF1F2', border: '#dc3545', text: '#9f1239', label: 'Appointment Cancelled' },
    reschedule:   { icon: '🔄', bg: '#FFF7ED', border: '#f57c00', text: '#c2410c', label: 'Rescheduled' },
    warning:      { icon: '⚠️', bg: '#FFFBEB', border: '#d97706', text: '#92400e', label: 'Important Notice' },
    success:      { icon: '✅', bg: '#ECFDF5', border: '#059669', text: '#065f46', label: 'Good News' },
    system:       { icon: 'ℹ️', bg: '#F0FDF4', border: '#2E7D32', text: '#166534', label: 'System Update' },
    info:         { icon: 'ℹ️', bg: '#F0F9FF', border: '#0284c7', text: '#075985', label: 'Information' },
  };

  const getConfig = (type) => typeConfig[type] || typeConfig.info;

  return (
    <div style={{ background: 'linear-gradient(135deg, #f0f4ff 0%, #f8f9fa 100%)', minHeight: '100vh', padding: '2.5rem 0' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '0 1.5rem' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '1.9rem', fontWeight: 800, color: '#1A1D27', margin: 0 }}>🔔 Notifications</h1>
            <p style={{ color: '#6c757d', margin: '0.3rem 0 0', fontSize: '0.95rem' }}>
              {notifs.filter(n => !n.is_read).length > 0
                ? `${notifs.filter(n => !n.is_read).length} unread notification(s)`
                : 'All caught up!'}
            </p>
          </div>
          <div style={{
            background: '#2D68FE', color: '#fff', borderRadius: '50%',
            width: '48px', height: '48px', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: '1.4rem', boxShadow: '0 4px 14px rgba(45,104,254,0.35)'
          }}>
            🔔
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: '#6c757d' }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem', animation: 'pulse 1s infinite' }}>⏳</div>
            Loading notifications...
          </div>
        ) : notifs.length === 0 ? (
          <div style={{ background: '#fff', borderRadius: '20px', padding: '5rem 2rem', textAlign: 'center', color: '#6c757d', boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1.2rem' }}>🔕</div>
            <h3 style={{ margin: '0 0 0.5rem', color: '#1A1D27', fontSize: '1.3rem' }}>No Notifications Yet</h3>
            <p style={{ margin: 0 }}>Notifications about your appointments and important updates will appear here.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {notifs.map(n => {
              const cfg = getConfig(n.type);
              return (
                <div key={n.id} style={{
                  background: n.is_read ? '#fff' : cfg.bg,
                  borderRadius: '16px',
                  padding: '0',
                  boxShadow: n.is_read ? '0 1px 6px rgba(0,0,0,0.04)' : '0 4px 20px rgba(0,0,0,0.08)',
                  borderLeft: `5px solid ${cfg.border}`,
                  overflow: 'hidden',
                  transition: 'all 0.2s',
                  opacity: n.is_read ? 0.82 : 1,
                }}>
                  {/* Type label bar */}
                  <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '0.6rem 1.25rem',
                    background: cfg.bg,
                    borderBottom: `1px solid ${cfg.border}22`,
                  }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: cfg.text, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {cfg.icon} {cfg.label}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {!n.is_read && (
                        <span style={{
                          background: cfg.border, color: '#fff', borderRadius: '50px',
                          padding: '0.15rem 0.6rem', fontSize: '0.65rem', fontWeight: 800,
                        }}>NEW</span>
                      )}
                      <span style={{ color: '#adb5bd', fontSize: '0.78rem' }}>
                        {new Date(n.created_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>

                  {/* Message body */}
                  <div style={{ padding: '1rem 1.25rem' }}>
                    <p style={{
                      margin: 0,
                      fontSize: '0.97rem',
                      color: n.is_read ? '#495057' : '#1A1D27',
                      fontWeight: n.is_read ? 400 : 500,
                      lineHeight: '1.65'
                    }}>
                      {n.message}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


/* ── App Root ───────────────────────────────────────────────── */
export default function App() {
  return (
    <AuthProvider>
      <div style={{ minHeight: '100vh', background: '#f8f9fa', fontFamily: "'Inter', system-ui, sans-serif" }}>
        <Navbar />
        <Routes>
          {/* Public routes — no login needed */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes — redirects to /login if not authenticated */}
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/hospital/:id" element={<ProtectedRoute><HospitalDetail /></ProtectedRoute>} />
          <Route path="/appointments" element={<ProtectedRoute><AppointmentsPage /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}

/* ── Inline Styles ──────────────────────────────────────────── */
const styles = {
  nav: { background: '#fff', padding: '0.9rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 2px 10px rgba(0,0,0,.06)', position: 'sticky', top: 0, zIndex: 100 },
  brand: { color: '#2D68FE', fontSize: '1.5rem', fontWeight: 800, textDecoration: 'none', letterSpacing: '-0.5px' },
  navLinks: { display: 'flex', alignItems: 'center', gap: '0.25rem' },
  navLink: { color: '#495057', padding: '0.5rem 0.75rem', borderRadius: '8px', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem', transition: 'all .2s' },
  navLinkHighlight: { color: '#fff', padding: '0.55rem 1.25rem', borderRadius: '25px', textDecoration: 'none', fontWeight: 700, fontSize: '0.9rem', background: '#2D68FE', boxShadow: '0 4px 10px rgba(45,104,254,0.3)' },
  navBtn: { color: '#dc3545', padding: '0.5rem 0.75rem', borderRadius: '8px', fontWeight: 600, fontSize: '0.9rem', background: 'transparent', border: 'none', cursor: 'pointer', fontFamily: 'inherit' },
  navUser: { color: '#495057', fontSize: '0.88rem', fontWeight: 600, padding: '0 0.5rem', borderLeft: '1px solid #dee2e6', marginLeft: '0.25rem' },
  notifBadge: { position: 'absolute', top: '-5px', right: '-5px', background: '#dc3545', color: '#fff', borderRadius: '50%', width: '18px', height: '18px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.62rem', fontWeight: 800, lineHeight: 1 },

  profileRow: { display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid #f1f3f5', fontSize: '1rem', color: '#495057' },

  label: { display: 'block', fontWeight: 600, fontSize: '0.9rem', color: '#495057', marginBottom: '0.4rem' },
  input: { width: '100%', padding: '0.65rem 0.9rem', border: '2px solid #dee2e6', borderRadius: '8px', fontSize: '0.95rem', fontFamily: 'inherit', outline: 'none', boxSizing: 'border-box' },

  btnPrimary: { padding: '0.55rem 1.25rem', background: '#2D68FE', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.9rem' },
  btnDanger: { padding: '0.55rem 1.25rem', background: '#dc3545', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.9rem' },
  btnOutline: { padding: '0.55rem 1.25rem', background: 'transparent', color: '#2D68FE', border: '2px solid #2D68FE', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.9rem' },
};
