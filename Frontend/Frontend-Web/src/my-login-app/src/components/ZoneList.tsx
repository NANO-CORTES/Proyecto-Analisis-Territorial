import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';

interface Zone {
  zoneCode: string;
  zoneName: string;
}

interface ZoneListProps {
  department?: string;
}

const ZoneList: React.FC<ZoneListProps> = ({ department }) => {
  const { token } = useAuth();
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchZones = async () => {
    if (!department) {
      setZones([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      let url = `http://127.0.0.1:8000/api/v1/ingestion/datasets/zones?limit=50`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (department) url += `&department=${encodeURIComponent(department)}`;
      
      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        // Local safety filter: only show codes with length >= 5 (municipalities)
        setZones(items.filter((z: Zone) => z.zoneCode.length >= 5));
      }
    } catch (err) {
      console.error("Error fetching zones:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchZones();
  }, [searchTerm, department]);

  return (
    <div className="zone-list-container" style={{
      marginTop: '2rem',
      padding: '1.5rem',
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '16px',
      border: '1px solid rgba(255, 255, 255, 0.08)'
    }}>
      <style>{`
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          </svg>
          Municipios Cargados
        </h3>
        <div style={{ position: 'relative' }}>
          <input 
            type="text" 
            placeholder="Buscar municipio o código..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            disabled={!department}
            style={{
              padding: '0.5rem 1rem 0.5rem 2.2rem',
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: 'white',
              fontSize: '0.875rem',
              width: '240px',
              opacity: !department ? 0.3 : 1
            }}
          />
          <svg style={{ position: 'absolute', left: '0.8rem', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
      </div>

      {!department ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '3rem 2rem', 
          background: 'rgba(255,255,255,0.01)', 
          borderRadius: '12px',
          border: '1px dashed rgba(255,255,255,0.05)'
        }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="1" style={{ marginBottom: '1rem', opacity: 0.5 }}>
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
          </svg>
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9375rem' }}>
            Selecciona un departamento en la tarjeta superior para ver sus municipios cargados.
          </p>
        </div>
      ) : loading ? (
        <div style={{ textAlign: 'center', padding: '2rem', opacity: 0.5 }}>Cargando municipios...</div>
      ) : zones.length > 0 ? (
        <div className="hide-scrollbar" style={{ maxHeight: '400px', overflowY: 'auto', borderRadius: '8px' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <th style={{ padding: '0.75rem', color: '#94a3b8', fontWeight: 500 }}>Código</th>
                <th style={{ padding: '0.75rem', color: '#94a3b8', fontWeight: 500 }}>Nombre del Territorio</th>
              </tr>
            </thead>
            <tbody>
              {zones.map((zone) => (
                <tr key={zone.zoneCode} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)', transition: 'background 0.2s' }} className="zone-row">
                  <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#6366f1' }}>{zone.zoneCode}</td>
                  <td style={{ padding: '0.75rem' }}>{zone.zoneName}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', background: 'rgba(0,0,0,0.1)', borderRadius: '12px' }}>
          <p style={{ margin: 0, color: '#64748b' }}>No se han encontrado municipios cargados para este departamento o búsqueda.</p>
        </div>
      )}
    </div>
  );
};

export default ZoneList;
