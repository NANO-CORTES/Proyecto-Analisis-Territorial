import React, { useState, useEffect } from 'react';

interface ServiceStatus {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  url: string;
}

const SystemHealth: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Gateway', status: 'loading', url: 'http://127.0.0.1:8000/health' },
    { name: 'Auth', status: 'loading', url: 'http://127.0.0.1:8000/api/v1/auth/health' },
    { name: 'Ingestion', status: 'loading', url: 'http://127.0.0.1:8000/api/v1/ingestion/health' },
    { name: 'Transformation', status: 'loading', url: 'http://127.0.0.1:8000/api/v1/transformation/health' },
  ]);

  const checkHealth = async () => {
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        try {
          const res = await fetch(service.url, { cache: 'no-store' });
          return { ...service, status: res.ok ? 'healthy' : 'unhealthy' as any };
        } catch {
          return { ...service, status: 'unhealthy' as any };
        }
      })
    );
    setServices(updatedServices);
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="system-health-panel" style={{
      marginTop: '2rem',
      padding: '1.5rem',
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '16px',
      border: '1px solid rgba(255, 255, 255, 0.08)'
    }}>
      <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
        Estado del Sistema
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
        {services.map((s) => (
          <div key={s.name} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            padding: '0.75rem',
            background: 'rgba(0,0,0,0.2)',
            borderRadius: '12px',
            border: '1px solid rgba(255,255,255,0.04)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: s.status === 'healthy' ? '#10b981' : s.status === 'loading' ? '#f59e0b' : '#ef4444',
              boxShadow: s.status === 'healthy' ? '0 0 8px #10b981' : 'none'
            }} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{s.name}</span>
              <span style={{ fontSize: '0.8125rem', fontWeight: 500 }}>
                {s.status === 'loading' ? 'Cargando...' : s.status === 'healthy' ? 'Operativo' : 'Desconectado'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemHealth;
