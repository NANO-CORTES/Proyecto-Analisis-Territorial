import React, { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';

interface Zone {
  zoneCode: string;
  zoneName: string;
}

const ZonesFilter: React.FC = () => {
  const [zones, setZones] = useState<Zone[]>([]);
  const [selectedZone, setSelectedZone] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    const fetchZones = async () => {
      if (!token) return;
      setLoading(true);
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/ingestion/datasets/zones?limit=50', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setZones(data.items || []);
        }
      } catch (err) {
        console.error('Error fetching zones', err);
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
  }, [token]);

  return (
    <div className="zones-filter" style={{ minWidth: '200px' }}>
      <label htmlFor="zone-select" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
        Filtrar por Zona Territoral:
      </label>
      <select 
        id="zone-select" 
        value={selectedZone} 
        onChange={(e) => setSelectedZone(e.target.value)}
        style={{
          width: '100%',
          padding: '0.5rem',
          borderRadius: '4px',
          border: '1px solid #ccc'
        }}
        disabled={loading}
      >
        <option value="">Todas las Zonas</option>
        {zones.map((zone) => (
          <option key={zone.zoneCode} value={zone.zoneCode}>
            {zone.zoneName} ({zone.zoneCode})
          </option>
        ))}
      </select>
    </div>
  );
};

export default ZonesFilter;
