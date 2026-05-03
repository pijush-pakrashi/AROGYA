import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../App';

export default function Home() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryLocation = searchParams.get('location');
  
  const [location, setLocation] = useState(queryLocation || user?.city || 'Kolkata');
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (queryLocation) {
      setLocation(queryLocation);
      fetchHospitals(queryLocation);
    } else if (user?.city) {
      setLocation(user.city);
      fetchHospitals(user.city);
    } else {
      fetchHospitals(location);
    }
  }, [user, queryLocation]);

  const fetchHospitals = async (loc) => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/hospitals?location=${loc}`);
      setHospitals(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchParams({ location });
    // fetchHospitals will be called by useEffect when queryLocation updates, 
    // but we can also just let useEffect handle it or keep it here.
    // However, if location is the same, useEffect won't trigger if queryLocation doesn't change,
    // so it's safe to keep fetchHospitals(location) here just in case.
    fetchHospitals(location);
  };

  const privateHospitals = hospitals.filter(h => h.type === 'Private').slice(0, 5);
  const govtHospitals = hospitals.filter(h => h.type === 'Government').slice(0, 5);

  return (
    <div style={{background: '#f8f9fa', minHeight: '100vh', paddingBottom: '3rem'}}>
      {/* Hero Search Section */}
      <section style={styles.hero}>
        <div style={styles.heroContent}>
          <h1 style={styles.heroTitle}>Find the Best Healthcare Near You</h1>
          <p style={styles.heroSubtitle}>
            Discover top-rated private and government hospitals. Book appointments instantly and securely.
          </p>
          
          <form onSubmit={handleSearch} style={styles.searchForm}>
            <div style={styles.searchWrapper}>
              <span style={styles.searchIcon}>📍</span>
              <input 
                type="text" 
                value={location}
                onChange={e => setLocation(e.target.value)}
                placeholder="Enter city or location (e.g., Kolkata)" 
                style={styles.searchInput}
              />
              <button type="submit" style={styles.searchBtn}>Search</button>
            </div>
          </form>
        </div>
      </section>

      {/* Hospitals Display */}
      <div style={styles.container}>
        {loading ? (
          <div style={{textAlign: 'center', padding: '3rem'}}>Loading hospitals...</div>
        ) : (
          <>
            {/* Private Hospitals */}
            <section style={{marginBottom: '3rem'}}>
              <div style={styles.sectionHeader}>
                <h2 style={styles.sectionTitle}>Top Private Hospitals</h2>
                <span style={styles.badgePrivate}>Premium Care</span>
              </div>
              
              {privateHospitals.length === 0 ? (
                <p style={styles.noData}>No private hospitals found in this location.</p>
              ) : (
                <div style={styles.grid}>
                  {privateHospitals.map(h => (
                    <HospitalCard key={h.id} hospital={h} navigate={navigate} />
                  ))}
                </div>
              )}
            </section>

            {/* Government Hospitals */}
            <section>
              <div style={styles.sectionHeader}>
                <h2 style={styles.sectionTitle}>Top Government Hospitals</h2>
                <span style={styles.badgeGovt}>Public Healthcare</span>
              </div>
              
              {govtHospitals.length === 0 ? (
                <p style={styles.noData}>No government hospitals found in this location.</p>
              ) : (
                <div style={styles.grid}>
                  {govtHospitals.map(h => (
                    <HospitalCard key={h.id} hospital={h} navigate={navigate} />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  );
}

function HospitalCard({ hospital, navigate }) {
  return (
    <div style={styles.card} onClick={() => navigate(`/hospital/${hospital.id}`)}>
      <div style={styles.cardHeader}>
        <div style={styles.cardIcon}>🏥</div>
        <div style={styles.rating}>⭐ {hospital.rating}</div>
      </div>
      <h3 style={styles.cardTitle}>{hospital.name}</h3>
      <p style={styles.cardAddress}>📍 {hospital.address}</p>
      <div style={styles.cardMeta}>
        <span>📞 {hospital.contact_number}</span>
        <span>🕒 {hospital.opening_hours}</span>
      </div>
      <div style={styles.cardFooter}>
        <span style={styles.docCount}>{hospital.doctors_count} Doctors Available</span>
        <button style={styles.viewBtn}>View Details</button>
      </div>
    </div>
  );
}

const styles = {
  hero: {
    background: 'linear-gradient(135deg, #2D68FE 0%, #1A4BCE 100%)',
    padding: '5rem 2rem',
    textAlign: 'center',
    color: '#fff',
    borderBottomLeftRadius: '30px',
    borderBottomRightRadius: '30px',
    marginBottom: '2rem'
  },
  heroContent: {
    maxWidth: '800px',
    margin: '0 auto'
  },
  heroTitle: {
    fontSize: '2.5rem',
    fontWeight: 800,
    marginBottom: '1rem',
    letterSpacing: '-0.5px'
  },
  heroSubtitle: {
    fontSize: '1.1rem',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '2.5rem'
  },
  searchForm: {
    maxWidth: '600px',
    margin: '0 auto',
    background: '#fff',
    padding: '0.5rem',
    borderRadius: '50px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
  },
  searchWrapper: {
    display: 'flex',
    alignItems: 'center',
  },
  searchIcon: {
    padding: '0 1rem',
    fontSize: '1.2rem'
  },
  searchInput: {
    flex: 1,
    border: 'none',
    outline: 'none',
    fontSize: '1rem',
    padding: '0.75rem 0',
    color: '#333',
    background: 'transparent'
  },
  searchBtn: {
    background: '#2D68FE',
    color: '#fff',
    border: 'none',
    padding: '0.75rem 2rem',
    borderRadius: '40px',
    fontSize: '1rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background 0.2s'
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 1.5rem'
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '1.5rem'
  },
  sectionTitle: {
    fontSize: '1.5rem',
    fontWeight: 700,
    color: '#1A1D27',
    margin: 0
  },
  badgePrivate: {
    background: '#E6F0FF',
    color: '#2D68FE',
    padding: '0.25rem 0.75rem',
    borderRadius: '20px',
    fontSize: '0.8rem',
    fontWeight: 600
  },
  badgeGovt: {
    background: '#E8F5E9',
    color: '#2E7D32',
    padding: '0.25rem 0.75rem',
    borderRadius: '20px',
    fontSize: '0.8rem',
    fontWeight: 600
  },
  noData: {
    color: '#6c757d',
    padding: '2rem',
    background: '#fff',
    borderRadius: '12px',
    textAlign: 'center',
    border: '1px dashed #dee2e6'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '1.5rem'
  },
  card: {
    background: '#fff',
    borderRadius: '16px',
    padding: '1.5rem',
    boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
    cursor: 'pointer',
    transition: 'transform 0.2s, boxShadow 0.2s',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  cardIcon: {
    fontSize: '2rem',
    background: '#F0F4FF',
    width: '50px',
    height: '50px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '12px'
  },
  rating: {
    background: '#FFF8E1',
    color: '#F57C00',
    padding: '0.25rem 0.5rem',
    borderRadius: '8px',
    fontSize: '0.85rem',
    fontWeight: 700
  },
  cardTitle: {
    fontSize: '1.2rem',
    fontWeight: 700,
    color: '#1A1D27',
    margin: '0.5rem 0 0 0'
  },
  cardAddress: {
    color: '#6c757d',
    fontSize: '0.9rem',
    margin: 0,
    lineHeight: 1.4
  },
  cardMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.4rem',
    fontSize: '0.85rem',
    color: '#495057',
    marginTop: '0.5rem',
    padding: '0.75rem 0',
    borderTop: '1px solid #f1f3f5',
    borderBottom: '1px solid #f1f3f5'
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '0.5rem'
  },
  docCount: {
    fontSize: '0.85rem',
    fontWeight: 600,
    color: '#2D68FE'
  },
  viewBtn: {
    background: 'transparent',
    color: '#2D68FE',
    border: '1px solid #2D68FE',
    padding: '0.4rem 1rem',
    borderRadius: '20px',
    fontSize: '0.85rem',
    fontWeight: 600,
    cursor: 'pointer'
  }
};
