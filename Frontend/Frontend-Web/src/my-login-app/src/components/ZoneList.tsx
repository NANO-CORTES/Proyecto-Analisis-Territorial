import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';

interface Zone {
  zoneCode: string;
  zoneName: string;
}

interface ZoneSummary {
  zone_code: string;
  score: { score: number, level: string } | null;
  indicators: {
    population_indicator: number;
    income_indicator: number;
    education_indicator: number;
    competition_indicator: number;
  } | null;
}

interface ZoneListProps {
  department?: string;
}

const ZoneList: React.FC<ZoneListProps> = ({ department }) => {
  const { token } = useAuth();
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedZone, setSelectedZone] = useState<ZoneSummary | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const fetchZones = async () => {
    if (!department) {
      setZones([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      let url = `http://127.0.0.1:8000/api/v1/ingestion/zones?limit=50`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
      if (department) url += `&department=${encodeURIComponent(department)}`;
      
      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        const zonesList = data.data || data.items || [];
        setZones(zonesList.filter((z: Zone) => z.zoneCode && z.zoneCode.length >= 5));
      }
    } catch (err) {
      console.error("Error fetching zones:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchZoneDetails = async (zoneCode: string) => {
    setLoadingDetails(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/bff/zone-summary/${zoneCode}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedZone(data);
      }
    } catch (err) {
      console.error("Error fetching zone details:", err);
    } finally {
      setLoadingDetails(false);
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
        .zone-row:hover {
          background: rgba(255, 255, 255, 0.05) !important;
          cursor: pointer;
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
            placeholder="Buscar municipio..." 
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
          <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9375rem' }}>
            Selecciona un departamento para ver sus municipios y detalles de analítica.
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
                <th style={{ padding: '0.75rem', color: '#94a3b8', fontWeight: 500, textAlign: 'right' }}>Acción</th>
              </tr>
            </thead>
            <tbody>
              {zones.map((zone) => (
                <tr key={zone.zoneCode} className="zone-row" style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }} onClick={() => fetchZoneDetails(zone.zoneCode)}>
                  <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#6366f1' }}>{zone.zoneCode}</td>
                  <td style={{ padding: '0.75rem' }}>{zone.zoneName}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                    <button style={{ background: 'none', border: 'none', color: '#6366f1', fontSize: '0.75rem', cursor: 'pointer' }}>
                      Ver Detalles →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '2rem', background: 'rgba(0,0,0,0.1)', borderRadius: '12px' }}>
          <p style={{ margin: 0, color: '#64748b' }}>No se han encontrado municipios.</p>
        </div>
      )}

      {/* Modal de Detalles de Zona */}
      {selectedZone && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }} onClick={() => setSelectedZone(null)}>
          <div style={{
            width: '100%', maxWidth: '500px', background: '#121212', borderRadius: '24px',
            padding: '2rem', border: '1px solid rgba(255,255,255,0.1)'
          }} onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{zones.find(z => z.zoneCode === selectedZone.zone_code)?.zoneName}</h2>
            <p style={{ fontSize: '0.875rem', opacity: 0.5, marginBottom: '2rem' }}>Resumen de Indicadores y Scoring</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '16px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.75rem', opacity: 0.4, marginBottom: '0.5rem' }}>SCORE</span>
                <span style={{ fontSize: '1.5rem', fontWeight: 700, color: '#6366f1' }}>
                  {selectedZone.score?.score.toFixed(3) || 'N/A'}
                </span>
              </div>
              <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '16px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.75rem', opacity: 0.4, marginBottom: '0.5rem' }}>NIVEL</span>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: selectedZone.score?.level === 'ALTA' ? '#10b981' : '#f59e0b' }}>
                  {selectedZone.score?.level || 'SIN DATOS'}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {[
                { label: 'Población', val: selectedZone.indicators?.population_indicator, color: '#6366f1' },
                { label: 'Ingresos', val: selectedZone.indicators?.income_indicator, color: '#10b981' },
                { label: 'Educación', val: selectedZone.indicators?.education_indicator, color: '#f59e0b' },
                { label: 'Competencia', val: selectedZone.indicators?.competition_indicator, color: '#ef4444' }
              ].map(ind => (
                <div key={ind.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.8125rem' }}>
                    <span style={{ opacity: 0.6 }}>{ind.label}</span>
                    <span style={{ fontWeight: 600 }}>{ind.val?.toFixed(3) || '0.000'}</span>
                  </div>
                  <div style={{ height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '2px', overflow: 'hidden' }}>
                    <div style={{ width: `${(ind.val || 0) * 100}%`, height: '100%', background: ind.color }} />
                  </div>
                </div>
              ))}
            </div>

            <button 
              onClick={() => setSelectedZone(null)}
              style={{
                width: '100%', marginTop: '2.5rem', padding: '0.75rem',
                background: 'rgba(255,255,255,0.05)', border: 'none',
                borderRadius: '12px', color: 'white', cursor: 'pointer'
              }}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZoneList;
