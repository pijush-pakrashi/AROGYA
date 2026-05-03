import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../App';

export default function HospitalDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [hospital, setHospital] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Booking state
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [slots, setSlots] = useState([]);
  const [notes, setNotes] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchHospital();
  }, [id]);

  const fetchHospital = async () => {
    try {
      const res = await axios.get(`/api/hospitals/${id}`);
      setHospital(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSlots = async (docId, d) => {
    try {
      const r = await axios.get(`/api/doctors/${docId}/slots`, { params: { date: d } });
      setSlots(r.data.slots);
    } catch { setSlots([]); }
  };

  const selectDoctor = (doc) => {
    setSelectedDoctor(doc);
    fetchSlots(doc.id, date);
    setMessage('');
  };

  const handleDateChange = (e) => {
    const d = e.target.value;
    setDate(d);
    if (selectedDoctor) fetchSlots(selectedDoctor.id, d);
  };

  const bookSlot = async (time) => {
    if (!user) {
      navigate('/login');
      return;
    }
    try {
      await axios.post('/api/appointments', {
        doctor_id: selectedDoctor.id, date, time_slot: time, notes
      });
      setMessage(`✅ Appointment booked successfully with Dr. ${selectedDoctor.name}`);
      fetchSlots(selectedDoctor.id, date);
      setNotes('');
    } catch (err) {
      setMessage(`❌ ${err.response?.data?.error || 'Booking failed'}`);
    }
  };

  if (loading) return <div style={{textAlign: 'center', padding: '4rem'}}>Loading...</div>;
  if (!hospital) return <div style={{textAlign: 'center', padding: '4rem'}}>Hospital not found</div>;

  return (
    <div style={styles.page}>
      {/* Hospital Header */}
      <div style={styles.header}>
        <div style={styles.container}>
          <div style={styles.headerContent}>
            <div style={styles.headerText}>
              <span style={hospital.type === 'Private' ? styles.badgePrivate : styles.badgeGovt}>
                {hospital.type} Hospital
              </span>
              <h1 style={styles.title}>{hospital.name}</h1>
              <p style={styles.address}>📍 {hospital.address}, {hospital.city}</p>
              <div style={styles.metaRow}>
                <span>📞 {hospital.contact_number}</span>
                <span>🕒 {hospital.opening_hours}</span>
                <span style={styles.rating}>⭐ {hospital.rating}</span>
                {hospital.map_url && (
                  <a href={hospital.map_url} target="_blank" rel="noreferrer" style={styles.mapLink}>🗺️ View on Map</a>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div style={styles.container}>
        {message && (
          <div style={{...styles.alert, background: message.startsWith('✅') ? '#d1e7dd' : '#f8d7da', color: message.startsWith('✅') ? '#0f5132' : '#842029'}}>
            {message}
          </div>
        )}

        <div style={styles.grid}>
          {/* Doctors List */}
          <div style={styles.doctorsSection}>
            <h2 style={styles.sectionTitle}>Available Doctors</h2>
            {hospital.doctors && hospital.doctors.length > 0 ? (
              <div style={styles.docList}>
                {hospital.doctors.map(doc => (
                  <div 
                    key={doc.id} 
                    style={{...styles.docCard, border: selectedDoctor?.id === doc.id ? '2px solid #2D68FE' : '2px solid transparent'}}
                    onClick={() => selectDoctor(doc)}
                  >
                    <div style={styles.docInfoRow}>
                      <img 
                        src={`https://i.pravatar.cc/150?img=${(doc.id % 50) + 10}`} 
                        alt={doc.name} 
                        style={styles.docAvatarImg} 
                      />
                      <div style={{flex: 1}}>
                        <h3 style={styles.docName}>Dr. {doc.name}</h3>
                        <p style={styles.docSpec}>{doc.specialization} • {doc.department}</p>
                        <p style={styles.docExp}>⭐ {4.5 + (doc.id % 5) * 0.1} ({doc.experience} yrs exp)</p>
                      </div>
                      <div style={styles.docFeeBox}>
                        <span style={styles.docFeeLabel}>Consultation</span>
                        <span style={styles.docFeeValue}>₹{500 + (doc.id % 5) * 150}</span>
                      </div>
                    </div>
                    
                    <div style={styles.docActionRow}>
                      <div style={styles.docAvailability}>
                        📅 {doc.working_hours_start} - {doc.working_hours_end}
                      </div>
                      <button style={styles.btnBookSecondary}>Select</button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p style={styles.noData}>No doctors currently available at this hospital.</p>
            )}
          </div>

          {/* Booking Panel */}
          <div style={styles.bookingSection}>
            {selectedDoctor ? (
              <div style={styles.bookingPanel}>
                <h2 style={styles.sectionTitle}>Book Appointment</h2>
                <div style={styles.selectedDocInfo}>
                  <strong>Dr. {selectedDoctor.name}</strong>
                  <span>{selectedDoctor.specialization}</span>
                </div>

                <label style={styles.label}>Select Date</label>
                <input 
                  type="date" 
                  value={date} 
                  onChange={handleDateChange} 
                  style={styles.input} 
                  min={new Date().toISOString().split('T')[0]} 
                />

                <label style={{...styles.label, marginTop: '1.5rem'}}>Available Time Slots</label>
                <div style={styles.slotGrid}>
                  {slots.length === 0 ? (
                    <p style={{color: '#6c757d', fontSize: '0.9rem', gridColumn: '1/-1'}}>No slots available for this date.</p>
                  ) : (
                    slots.map(slot => (
                      <button 
                        key={slot.time}
                        disabled={!slot.available}
                        onClick={() => bookSlot(slot.time)}
                        style={{...styles.slotBtn, ...(slot.available ? styles.slotAvailable : styles.slotBooked)}}
                      >
                        {slot.time}
                      </button>
                    ))
                  )}
                </div>

                <label style={{...styles.label, marginTop: '1.5rem'}}>Notes (optional)</label>
                <textarea 
                  value={notes} 
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Describe your symptoms or reason for visit..."
                  style={{...styles.input, minHeight: '80px', resize: 'vertical'}} 
                />
              </div>
            ) : (
              <div style={styles.emptyPanel}>
                <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📅</div>
                <h3>Select a Doctor</h3>
                <p>Click on a doctor from the list to see available slots and book an appointment.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    background: '#f8f9fa',
    minHeight: '100vh',
    paddingBottom: '4rem'
  },
  header: {
    background: '#fff',
    borderBottom: '1px solid #eaeaea',
    padding: '3rem 0',
    marginBottom: '2rem'
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1.5rem'
  },
  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
  },
  headerText: {
    maxWidth: '800px'
  },
  badgePrivate: {
    background: '#E6F0FF',
    color: '#2D68FE',
    padding: '0.3rem 0.8rem',
    borderRadius: '20px',
    fontSize: '0.85rem',
    fontWeight: 600,
    display: 'inline-block',
    marginBottom: '1rem'
  },
  badgeGovt: {
    background: '#E8F5E9',
    color: '#2E7D32',
    padding: '0.3rem 0.8rem',
    borderRadius: '20px',
    fontSize: '0.85rem',
    fontWeight: 600,
    display: 'inline-block',
    marginBottom: '1rem'
  },
  title: {
    fontSize: '2.2rem',
    fontWeight: 800,
    color: '#1A1D27',
    margin: '0 0 0.5rem 0'
  },
  address: {
    fontSize: '1.1rem',
    color: '#6c757d',
    margin: '0 0 1rem 0'
  },
  metaRow: {
    display: 'flex',
    gap: '1.5rem',
    alignItems: 'center',
    color: '#495057',
    fontSize: '0.95rem',
    flexWrap: 'wrap'
  },
  rating: {
    background: '#FFF8E1',
    color: '#F57C00',
    padding: '0.2rem 0.6rem',
    borderRadius: '6px',
    fontWeight: 700
  },
  mapLink: {
    color: '#2D68FE',
    textDecoration: 'none',
    fontWeight: 600
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '2rem',
    alignItems: 'start'
  },
  sectionTitle: {
    fontSize: '1.25rem',
    fontWeight: 700,
    color: '#1A1D27',
    marginBottom: '1.5rem'
  },
  docList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  docCard: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem',
    padding: '1.25rem',
    background: '#fff',
    borderRadius: '16px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.04)',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  docInfoRow: {
    display: 'flex',
    gap: '1rem',
    alignItems: 'flex-start',
  },
  docAvatarImg: {
    width: '64px',
    height: '64px',
    borderRadius: '12px',
    objectFit: 'cover',
    background: '#f8f9fa',
  },
  docName: {
    margin: 0,
    fontSize: '1.15rem',
    fontWeight: 700,
    color: '#1A1D27'
  },
  docSpec: {
    margin: '0.2rem 0',
    color: '#6c757d',
    fontSize: '0.9rem'
  },
  docExp: {
    margin: '0.4rem 0 0',
    color: '#F57C00',
    fontWeight: 600,
    fontSize: '0.85rem'
  },
  docFeeBox: {
    textAlign: 'right',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    background: '#F0F4FF',
    padding: '0.5rem 0.75rem',
    borderRadius: '10px'
  },
  docFeeLabel: {
    fontSize: '0.75rem',
    color: '#6c757d',
    fontWeight: 600,
    textTransform: 'uppercase'
  },
  docFeeValue: {
    fontSize: '1.1rem',
    color: '#2D68FE',
    fontWeight: 800,
  },
  docActionRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: '0.75rem',
    borderTop: '1px solid #f1f3f5'
  },
  docAvailability: {
    fontSize: '0.85rem',
    color: '#495057',
    fontWeight: 500,
    display: 'flex',
    alignItems: 'center',
    gap: '0.4rem'
  },
  btnBookSecondary: {
    padding: '0.5rem 1rem',
    background: '#fff',
    color: '#2D68FE',
    border: '1px solid #2D68FE',
    borderRadius: '8px',
    fontWeight: 600,
    fontSize: '0.85rem',
    cursor: 'pointer'
  },
  bookingPanel: {
    background: '#fff',
    borderRadius: '16px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
    padding: '2rem'
  },
  selectedDocInfo: {
    background: '#F8F9FA',
    padding: '1rem',
    borderRadius: '12px',
    marginBottom: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.25rem'
  },
  emptyPanel: {
    background: '#fff',
    borderRadius: '16px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
    padding: '4rem 2rem',
    textAlign: 'center',
    color: '#6c757d'
  },
  label: {
    display: 'block',
    fontWeight: 600,
    fontSize: '0.95rem',
    color: '#495057',
    marginBottom: '0.5rem'
  },
  input: {
    width: '100%',
    padding: '0.75rem 1rem',
    border: '2px solid #dee2e6',
    borderRadius: '10px',
    fontSize: '1rem',
    fontFamily: 'inherit',
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'border 0.2s'
  },
  slotGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(90px, 1fr))',
    gap: '0.5rem'
  },
  slotBtn: {
    padding: '0.6rem',
    border: 'none',
    borderRadius: '8px',
    fontSize: '0.9rem',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
    transition: 'all 0.2s'
  },
  slotAvailable: {
    background: '#E6F0FF',
    color: '#2D68FE',
  },
  slotBooked: {
    background: '#f1f3f5',
    color: '#adb5bd',
    cursor: 'not-allowed'
  },
  alert: {
    padding: '1rem 1.25rem',
    borderRadius: '10px',
    marginBottom: '1.5rem',
    fontWeight: 500,
    fontSize: '0.95rem'
  },
  noData: {
    color: '#6c757d',
    padding: '2rem',
    background: '#fff',
    borderRadius: '12px',
    textAlign: 'center',
    border: '1px dashed #dee2e6'
  }
};
