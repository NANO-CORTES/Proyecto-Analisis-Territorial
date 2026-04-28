import React from 'react';
import { useAuth } from '../components/AuthProvider';
import { useNavigate } from 'react-router-dom';
import '../styles/Dashboard.css';

const ProfilePage: React.FC = () => {
    const { username, role, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    return (
        <div className="dashboard-page">
            <header className="dashboard-header">
                <div className="dashboard-brand" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    <span>Análisis Territorial</span>
                </div>
                <nav className="dashboard-nav">
                    <button className="nav-link" onClick={() => navigate('/dashboard')}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                            <polyline points="9 22 9 12 15 12 15 22" />
                        </svg>
                        Dashboard
                    </button>
                    <button className="nav-link active">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                        Perfil
                    </button>
                </nav>
                <div className="dashboard-user">
                    <span className="user-greeting">Hola, <strong>{username}</strong></span>
                    <span className="user-role-badge">{role}</span>
                    <button onClick={handleLogout} className="btn-logout">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                            <polyline points="16 17 21 12 16 7" />
                            <line x1="21" y1="12" x2="9" y2="12" />
                        </svg>
                        Salir
                    </button>
                </div>
            </header>

            <main className="dashboard-main">
                <div className="welcome-card">
                    <div className="welcome-icon">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                    </div>
                    <h1>Tu Perfil</h1>
                    <p>Gestiona la información de tu cuenta.</p>
                </div>

                <div className="profile-details-card" style={{ 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    backdropFilter: 'blur(10px)',
                    borderRadius: '16px',
                    padding: '2rem',
                    marginTop: '2rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                    <div className="detail-item" style={{ marginBottom: '1.5rem' }}>
                        <span style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.9rem', display: 'block' }}>Nombre de Usuario</span>
                        <span style={{ fontSize: '1.2rem', fontWeight: '500' }}>{username}</span>
                    </div>
                    <div className="detail-item" style={{ marginBottom: '1.5rem' }}>
                        <span style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.9rem', display: 'block' }}>Rol del Sistema</span>
                        <span className="user-role-badge" style={{ marginTop: '0.5rem', display: 'inline-block' }}>{role}</span>
                    </div>
                    <div className="detail-item">
                        <span style={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.9rem', display: 'block' }}>Estado de la Cuenta</span>
                        <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem' }}>
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></div>
                            Usuario Activo
                        </span>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ProfilePage;
