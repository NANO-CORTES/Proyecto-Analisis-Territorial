import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import { getAuditEvents } from '../services/bffApi';
import '../styles/Dashboard.css';

interface AuditEvent {
    id: number;
    event_type: string;
    service_name: string;
    reference_id: string | null;
    user_id: string | null;
    status: string;
    event_summary: any;
    created_at: string;
}

const AuditTimelinePage: React.FC = () => {
    const { logout, username, role } = useAuth();
    const navigate = useNavigate();
    const [events, setEvents] = React.useState<AuditEvent[]>([]);
    const [filterService, setFilterService] = React.useState('');
    const [filterUser, setFilterUser] = React.useState('');
    const [filterType, setFilterType] = React.useState('');
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);

    const fetchAll = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getAuditEvents({
                service: filterService || undefined,
                user_id: filterUser || undefined,
                event_type: filterType || undefined,
                limit: 200,
            });
            setEvents(data);
        } catch (e: any) {
            setError(e.message || 'Error al cargar el log');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => { fetchAll(); }, []);

    return (
        <div className="dashboard-page">
            <header className="dashboard-header">
                <div className="dashboard-brand">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    <span>Analisis Territorial</span>
                </div>
                <nav className="dashboard-nav">
                    <button className="nav-link" onClick={() => navigate('/dashboard')}>Dashboard</button>
                    <button className="nav-link" onClick={() => navigate('/compare')}>Comparador</button>
                    {role === 'ADMIN' && (
                        <>
                            <button className="nav-link" onClick={() => navigate('/admin/users')}>Gestion de Usuarios</button>
                            <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>Experimentos ML</button>
                            <button className="nav-link" onClick={() => navigate('/configuration')}>Configuracion</button>
                            <button className="nav-link active" onClick={() => navigate('/audit')}>Auditoria</button>
                        </>
                    )}
                </nav>
                <div className="dashboard-user">
                    
                    <span className="user-role-badge">{role}</span>
                    <button onClick={() => { logout(); navigate('/'); }} className="btn-logout">Salir</button>
                </div>
            </header>
            <main className="dashboard-main" style={{ padding: '2rem' }}>
            <section className="admin-card">
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
                    <input className="admin-input" style={{ padding: '0.55rem 0.85rem', borderRadius: 10, background: 'rgba(255,255,255,0.05)', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.12)' }} placeholder="Servicio" value={filterService} onChange={(e) => setFilterService(e.target.value)} />
                    <input className="admin-input" style={{ padding: '0.55rem 0.85rem', borderRadius: 10, background: 'rgba(255,255,255,0.05)', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.12)' }} placeholder="Usuario" value={filterUser} onChange={(e) => setFilterUser(e.target.value)} />
                    <input className="admin-input" style={{ padding: '0.55rem 0.85rem', borderRadius: 10, background: 'rgba(255,255,255,0.05)', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.12)' }} placeholder="Tipo de evento" value={filterType} onChange={(e) => setFilterType(e.target.value)} />
                    <button className="admin-btn-primary" onClick={fetchAll} disabled={loading}>{loading ? 'Cargando...' : 'Aplicar filtros'}</button>
                </div>
                {error && <p className="admin-error">{error}</p>}
                <div style={{ maxHeight: 600, overflowY: 'auto' }}>
                    {events.length === 0 && <p>No hay eventos para los filtros seleccionados.</p>}
                    {events.map((event) => (
                        <article key={event.id} style={{ borderLeft: '3px solid #6366f1', padding: '8px 12px', marginBottom: 8, background: 'rgba(255,255,255,0.03)', borderRadius: '0 8px 8px 0' }}>
                            <header style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <strong>{event.event_type}</strong>
                                <small style={{ color: '#94a3b8' }}>{event.created_at}</small>
                            </header>
                            <div style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: '4px 0' }}>
                                <span>servicio: {event.service_name}</span>
                                {' | '}
                                <span>usuario: {event.user_id || 'system'}</span>
                                {' | '}
                                <span>estado: <span className={`admin-badge ${event.status === 'success' ? 'active' : 'inactive'}`}>{event.status}</span></span>
                            </div>
                            {event.event_summary && (
                                <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, background: 'rgba(0,0,0,0.2)', padding: 8, borderRadius: 6, border: '1px solid rgba(255,255,255,0.05)' }}>
                                    {JSON.stringify(event.event_summary, null, 2)}
                                </pre>
                            )}
                        </article>
                    ))}
                </div>
            </section>
            </main>
        </div>
    );
};

export default AuditTimelinePage;
