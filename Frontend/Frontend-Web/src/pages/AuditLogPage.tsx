import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';

import '../styles/Dashboard.css';
import '../styles/UserManagement.css';

interface AuditLog {
  id: number;
  trace_id: string;
  service_name: string;
  action: string;
  user_id?: string | null;
  details?: string | null;
  created_at: string;
}

const AuditLogPage: React.FC = () => {
  const { username, role, logout, token } = useAuth();
  const navigate = useNavigate();

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [userIdFilter, setUserIdFilter] = useState('');

  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);

  const formatDate = (value: string) => {
    try {
      const d = new Date(value);
      if (Number.isNaN(d.getTime())) return value;
      return d.toLocaleString();
    } catch {
      return value;
    }
  };

  const prettyDetails = (value: string | null | undefined) => {
    if (!value) return '';
    if (typeof value !== 'string') return JSON.stringify(value, null, 2);

    try {
      const parsed = JSON.parse(value);
      return JSON.stringify(parsed, null, 2);
    } catch {
      // Si no es JSON válido, lo mostramos como texto.
      return value;
    }
  };

  const fetchAuditLogs = async (userId?: string) => {
    setLoading(true);
    setError('');
    try {
      const params: Record<string, string> = {};
      const trimmed = (userId ?? '').trim();
      if (trimmed) params.user_id = trimmed;

      const res = await axios.get(`${apiBase}/api/v1/audit`, {
        headers: { Authorization: token ? `Bearer ${token}` : '' },
        params,
      });

      setLogs(res.data || []);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(detail || err.message || 'Error al cargar auditoría');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (role !== 'ADMIN') {
      navigate('/dashboard');
      return;
    }
    fetchAuditLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchAuditLogs(userIdFilter || undefined);
  };

  const openDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setDetailsOpen(true);
  };

  const closeDetails = () => {
    setDetailsOpen(false);
    setSelectedLog(null);
  };

  const detailsText = useMemo(() => {
    return selectedLog ? prettyDetails(selectedLog.details) : '';
  }, [selectedLog]);

  const activeUserId = selectedLog?.user_id || 'system';

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

          {role === 'ADMIN' && (
            <>
              <button className="nav-link" onClick={() => navigate('/admin/users')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                Usuarios
              </button>

              <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                Experimentos ML
              </button>

              <button className="nav-link active">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
                Auditoría
              </button>
            </>
          )}
        </nav>

        <div className="dashboard-user">
          <span className="user-greeting">
            Hola, <strong>{username}</strong>
          </span>
          <span className="user-role-badge">{role}</span>
          <button onClick={logout} className="btn-logout">
            Salir
          </button>
        </div>
      </header>

      <main className="um-main">
        <div className="um-header-row">
          <h1>Auditoría</h1>
        </div>

        {error && <div className="um-error">{error}</div>}

        <div className="um-table-wrap" style={{ padding: '1rem', marginBottom: '1.25rem' }}>
          <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: '1 1 260px' }}>
              <label style={{ display: 'block', fontSize: '0.8125rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.4rem' }}>
                Filtrar por user_id
              </label>
              <input
                type="text"
                value={userIdFilter}
                onChange={(e) => setUserIdFilter(e.target.value)}
                placeholder="Ej: user-123"
                style={{
                  width: '100%',
                  padding: '0.6rem 0.8rem',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  color: '#f1f5f9',
                  outline: 'none',
                }}
              />
            </div>

            <button type="submit" className="btn-create" disabled={loading} style={{ marginTop: '0.1rem' }}>
              Buscar
            </button>

            <button
              type="button"
              className="btn-cancel"
              disabled={loading}
              onClick={() => {
                setUserIdFilter('');
                fetchAuditLogs();
              }}
              style={{ marginTop: '0.1rem' }}
            >
              Limpiar
            </button>
          </form>
        </div>

        {loading ? (
          <div className="um-loading">
            <span className="spinner"></span>
            Cargando auditoría...
          </div>
        ) : (
          <div className="um-table-wrap">
            <table className="um-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Servicio</th>
                  <th>Acción</th>
                  <th>Usuario</th>
                  <th>Detalles</th>
                </tr>
              </thead>

              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDate(log.created_at)}</td>
                    <td>{log.service_name}</td>
                    <td>{log.action}</td>
                    <td>{log.user_id || 'system'}</td>
                    <td>
                      <button className="btn-action btn-role" onClick={() => openDetails(log)}>
                        Ver
                      </button>
                    </td>
                  </tr>
                ))}

                {logs.length === 0 && (
                  <tr>
                    <td colSpan={5} className="um-empty">
                      No hay eventos de auditoría
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {detailsOpen && selectedLog && (
        <div className="modal-overlay" onClick={closeDetails}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <h3>Detalles</h3>
              <button className="modal-close" onClick={closeDetails} title="Cerrar">
                ✕
              </button>
            </div>

            <div style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '0.85rem' }}>
              <div style={{ marginBottom: '0.25rem' }}>
                <strong>Servicio:</strong> {selectedLog.service_name}
              </div>
              <div style={{ marginBottom: '0.25rem' }}>
                <strong>Acción:</strong> {selectedLog.action}
              </div>
              <div style={{ marginBottom: '0.25rem' }}>
                <strong>Usuario:</strong> {activeUserId}
              </div>
              <div>
                <strong>Fecha:</strong> {formatDate(selectedLog.created_at)}
              </div>
            </div>

            <pre
              style={{
                margin: 0,
                padding: '1rem',
                borderRadius: '12px',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#e2e8f0',
                maxHeight: '60vh',
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {detailsText}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditLogPage;

