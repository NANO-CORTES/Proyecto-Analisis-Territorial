import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import SystemHealth from '../components/SystemHealth';
import '../styles/Dashboard.css';

interface Dataset {
  datasetId: string;
  fileName: string;
  fileSize: number;
  recordCount: number;
  uploadedAt: string;
  status: string;
}

interface AuditLog {
  id: number;
  service_name: string;
  action: string;
  details: string;
  user_id: string;
  created_at: string;
}

interface TransformationResult {
  id: number;
  file_hash: string;
  status: string;
  total_rows: number;
  processed_at: string;
  details: {
    duplicates_removed?: number;
    columns_processed?: string[];
    numeric_stats?: Record<string, { min: number, max: number, mean: number }>;
  };
}

const ProfilePage: React.FC = () => {
  const { username, logout, role, token } = useAuth();
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [transformResults, setTransformResults] = useState<TransformationResult[]>([]);
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [loadingAudit, setLoadingAudit] = useState(true);
  const [loadingTransform, setLoadingTransform] = useState(true);
  const [selectedResult, setSelectedResult] = useState<TransformationResult | null>(null);

  const fetchData = async () => {
    try {
      setLoadingDatasets(true);
      setLoadingAudit(true);
      setLoadingTransform(true);
      
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Fetch datasets
      const dsRes = await fetch('http://127.0.0.1:8000/api/v1/ingestion/datasets/', { headers });
      if (dsRes.ok) setDatasets(await dsRes.json());

      // Fetch audit logs
      const auditRes = await fetch('http://127.0.0.1:8000/api/v1/audit/', { headers });
      if (auditRes.ok) setAuditLogs(await auditRes.json());

      // Fetch transformation results
      const transRes = await fetch('http://127.0.0.1:8000/api/v1/transform/results', { headers });
      if (transRes.ok) setTransformResults(await transRes.json());

    } catch (err) {
      console.error("Error fetching profile data:", err);
    } finally {
      setLoadingDatasets(false);
      setLoadingAudit(false);
      setLoadingTransform(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleBack = () => {
    navigate('/dashboard');
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('es-CO', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="dashboard-page overflow-y-auto">
      <header className="dashboard-header">
        <div className="dashboard-brand" onClick={handleBack} style={{ cursor: 'pointer' }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          <span>Volver al Dashboard</span>
        </div>
        <div className="dashboard-user">
          <button onClick={() => { logout(); navigate('/'); }} className="btn-logout">
            Salir
          </button>
        </div>
      </header>

      <main className="dashboard-main" style={{ paddingBottom: '4rem' }}>
        <div className="welcome-card" style={{ marginBottom: '2rem' }}>
          <div className="welcome-icon" style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)' }}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          </div>
          <h1>Perfil de Usuario</h1>
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', opacity: 0.8 }}>
            <span>Nombre: <strong>{username}</strong></span>
            <span>Rol: <strong style={{ color: '#818cf8' }}>{role || 'USER'}</strong></span>
          </div>
        </div>

        <SystemHealth />

        <div className="profile-stats-grid" style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
          gap: '2rem', 
          marginTop: '2rem' 
        }}>
          {/* Tarjeta: Archivos Cargados */}
          <div className="stat-card" style={{ 
            flexDirection: 'column', 
            alignItems: 'flex-start', 
            padding: '1.5rem',
            background: 'rgba(0,0,0,0.2)',
            minHeight: '400px'
          }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
              </svg>
              Archivos Cargados
            </h3>
            
            {loadingDatasets ? (
              <div style={{ padding: '2rem', textAlign: 'center', width: '100%', opacity: 0.5 }}>Cargando archivos...</div>
            ) : datasets.length > 0 ? (
              <div style={{ width: '100%', maxHeight: '300px', overflowY: 'auto' }} className="hide-scrollbar">
                {datasets.map(ds => (
                  <div key={ds.datasetId} style={{ 
                    padding: '1rem', 
                    background: 'rgba(255,255,255,0.02)', 
                    borderRadius: '10px', 
                    marginBottom: '0.75rem',
                    border: '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{ds.fileName}</span>
                      <span style={{ fontSize: '0.75rem', opacity: 0.5 }}>{ds.recordCount} registros • {formatSize(ds.fileSize)}</span>
                    </div>
                    <span style={{ 
                      fontSize: '0.65rem', 
                      padding: '2px 8px', 
                      borderRadius: '12px', 
                      background: ds.status === 'VALID' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                      color: ds.status === 'VALID' ? '#10b981' : '#f59e0b',
                      border: `1px solid ${ds.status === 'VALID' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`
                    }}>
                      {ds.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', width: '100%', opacity: 0.5, border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '12px' }}>
                No has cargado archivos aún.
              </div>
            )}
          </div>

          {/* Tarjeta: Historial de Actividad (Auditoría) */}
          <div className="stat-card" style={{ 
            flexDirection: 'column', 
            alignItems: 'flex-start', 
            padding: '1.5rem',
            background: 'rgba(0,0,0,0.2)',
            minHeight: '400px'
          }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2">
                <path d="M12 20v-6M9 20v-10M12 4v4M15 20v-4M12 8l4 4M12 8l-4 4" />
                <path d="M3 12h18" />
              </svg>
              Historial de Actividad
            </h3>
            
            {loadingAudit ? (
              <div style={{ padding: '2rem', textAlign: 'center', width: '100%', opacity: 0.5 }}>Cargando actividad...</div>
            ) : auditLogs.length > 0 ? (
              <div style={{ width: '100%', maxHeight: '300px', overflowY: 'auto' }} className="hide-scrollbar">
                {auditLogs.map(log => (
                  <div key={log.id} style={{ 
                    padding: '0.875rem', 
                    background: 'rgba(255,255,255,0.01)', 
                    borderRadius: '8px', 
                    marginBottom: '0.6rem',
                    border: '1px solid rgba(255,255,255,0.03)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#22d3ee' }}>{log.action}</span>
                      <span style={{ fontSize: '0.7rem', opacity: 0.4 }}>{formatDate(log.created_at)}</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.8125rem', color: '#cbd5e1', lineHeight: 1.4 }}>{log.details}</p>
                    <span style={{ fontSize: '0.65rem', opacity: 0.3, display: 'block', marginTop: '0.25rem' }}>Servicio: {log.service_name}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', width: '100%', opacity: 0.5, border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '12px' }}>
                No hay eventos registrados.
              </div>
            )}
          </div>
        </div>

        {/* Tarjeta: Resultados Obtenidos (Fila Completa) */}
        <div className="stat-card" style={{ 
          marginTop: '2rem',
          flexDirection: 'column', 
          alignItems: 'flex-start', 
          padding: '1.5rem',
          background: 'rgba(0,0,0,0.2)',
          width: '100%'
        }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            Resultados de Transformación
          </h3>
          
          {loadingTransform ? (
            <div style={{ padding: '3rem', textAlign: 'center', width: '100%', opacity: 0.5 }}>Cargando resultados de análisis...</div>
          ) : transformResults.length > 0 ? (
            <div style={{ 
              width: '100%', 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
              gap: '1.5rem' 
            }}>
              {transformResults.map(res => (
                <div key={res.id} style={{
                  padding: '1.25rem',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '12px',
                  border: '1px solid rgba(255,255,255,0.08)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ overflow: 'hidden' }}>
                      <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#fff', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                        Dataset: {res.file_hash.substring(0, 12)}...
                      </h4>
                      <span style={{ fontSize: '0.75rem', opacity: 0.5 }}>{formatDate(res.processed_at)}</span>
                    </div>
                    <span style={{
                      fontSize: '0.65rem',
                      padding: '2px 8px',
                      borderRadius: '8px',
                      background: res.status === 'COMPLETED' ? 'rgba(168, 85, 247, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      color: res.status === 'COMPLETED' ? '#a855f7' : '#ef4444',
                      border: `1px solid ${res.status === 'COMPLETED' ? 'rgba(168, 85, 247, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
                    }}>
                      {res.status}
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem' }}>
                    <div>
                      <span style={{ display: 'block', opacity: 0.4, fontSize: '0.7rem' }}>REGISTROS</span>
                      <strong>{res.total_rows}</strong>
                    </div>
                    <div>
                      <span style={{ display: 'block', opacity: 0.4, fontSize: '0.7rem' }}>DUPLICADOS</span>
                      <strong>{res.details?.duplicates_removed || 0}</strong>
                    </div>
                  </div>

                  {res.details?.numeric_stats && (
                    <button 
                      onClick={() => setSelectedResult(res)}
                      style={{
                        padding: '0.5rem',
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(255,255,255,0.1)',
                        borderRadius: '6px',
                        color: '#a855f7',
                        fontSize: '0.75rem',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseOver={(e) => e.currentTarget.style.background = 'rgba(168, 85, 247, 0.1)'}
                      onMouseOut={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                    >
                      Ver Estadísticas de Columnas
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ 
              width: '100%', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              alignItems: 'center',
              padding: '3rem',
              textAlign: 'center',
              background: 'rgba(255,255,255,0.01)',
              borderRadius: '12px',
              border: '1px dashed rgba(255,255,255,0.05)'
            }}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="1" style={{ marginBottom: '1rem', opacity: 0.3 }}>
                 <circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path d="M12 8h.01" />
              </svg>
              <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9375rem' }}>
                No hay resultados de transformación disponibles. Procesa un dataset en el dashboard para ver los análisis aquí.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Modal Simple: Estadísticas de Columnas */}
      {selectedResult && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.8)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
          padding: '2rem'
        }} onClick={() => setSelectedResult(null)}>
          <div style={{
            width: '100%',
            maxWidth: '600px',
            background: '#121212',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '20px',
            padding: '2rem',
            position: 'relative'
          }} onClick={e => e.stopPropagation()}>
            <button 
              onClick={() => setSelectedResult(null)}
              style={{ position: 'absolute', right: '1.5rem', top: '1.5rem', background: 'none', border: 'none', color: '#fff', cursor: 'pointer', opacity: 0.5 }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
            </button>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', color: '#a855f7' }}>Detalles de Normalización</h2>
            <div style={{ maxHeight: '400px', overflowY: 'auto' }} className="hide-scrollbar">
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <th style={{ padding: '0.75rem', opacity: 0.5 }}>Columna</th>
                    <th style={{ padding: '0.75rem', opacity: 0.5 }}>Min</th>
                    <th style={{ padding: '0.75rem', opacity: 0.5 }}>Max</th>
                    <th style={{ padding: '0.75rem', opacity: 0.5 }}>Media</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(selectedResult.details.numeric_stats || {}).map(([col, stats]) => (
                    <tr key={col} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 500 }}>{col}</td>
                      <td style={{ padding: '0.75rem', color: '#94a3b8' }}>{stats.min.toFixed(3)}</td>
                      <td style={{ padding: '0.75rem', color: '#94a3b8' }}>{stats.max.toFixed(3)}</td>
                      <td style={{ padding: '0.75rem', color: '#94a3b8' }}>{stats.mean.toFixed(3)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(168, 85, 247, 0.1)', borderRadius: '10px', fontSize: '0.8rem', color: '#d8b4fe' }}>
              ℹ️ Los valores de las columnas han sido escalados al rango [0, 1] mediante normalización Min-Max.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
