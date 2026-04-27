import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';

interface RankingItem {
  zone_code: string;
  zone_name: string;
  score: number;
  level: 'ALTA' | 'MEDIA' | 'BAJA';
}

interface RankingListProps {
  executionId: string | null;
}

const RankingList: React.FC<RankingListProps> = ({ executionId }) => {
  const { token } = useAuth();
  const [ranking, setRanking] = useState<RankingItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (executionId) {
      fetchRanking();
    }
  }, [executionId]);

  const fetchRanking = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/analytics/ranking?execution_id=${executionId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setRanking(data.data || []);
      }
    } catch (err) {
      console.error("Error fetching ranking:", err);
    } finally {
      setLoading(false);
    }
  };

  if (!executionId) return null;

  const getLevelStyles = (level: string) => {
    switch (level) {
      case 'ALTA': return { color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', border: 'rgba(16, 185, 129, 0.2)' };
      case 'MEDIA': return { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.2)' };
      case 'BAJA': return { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.2)' };
      default: return { color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.1)', border: 'rgba(148, 163, 184, 0.2)' };
    }
  };

  return (
    <div className="ranking-container" style={{
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '20px',
      padding: '2rem',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      marginTop: '2rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #a855f7, #6366f1)',
            padding: '0.75rem',
            borderRadius: '12px'
          }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Ranking de Oportunidades</h2>
            <p style={{ margin: 0, opacity: 0.5, fontSize: '0.875rem' }}>Las zonas con mayor potencial para tu negocio</p>
          </div>
        </div>
        <button 
          onClick={fetchRanking}
          style={{
            background: 'none',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'rgba(255,255,255,0.5)',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '0.75rem'
          }}
        >
          Actualizar
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', opacity: 0.5 }}>Calculando ranking...</div>
      ) : ranking.length > 0 ? (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <th style={{ padding: '1rem', fontSize: '0.75rem', opacity: 0.4, textTransform: 'uppercase' }}>Pos</th>
                <th style={{ padding: '1rem', fontSize: '0.75rem', opacity: 0.4, textTransform: 'uppercase' }}>Zona</th>
                <th style={{ padding: '1rem', fontSize: '0.75rem', opacity: 0.4, textTransform: 'uppercase' }}>Score</th>
                <th style={{ padding: '1rem', fontSize: '0.75rem', opacity: 0.4, textTransform: 'uppercase' }}>Nivel</th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((item, index) => {
                const styles = getLevelStyles(item.level);
                return (
                  <tr key={item.zone_code} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    <td style={{ padding: '1rem', fontWeight: 600, opacity: 0.5 }}>#{index + 1}</td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ fontWeight: 500 }}>{item.zone_name}</div>
                      <div style={{ fontSize: '0.75rem', opacity: 0.4 }}>{item.zone_code}</div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ 
                            width: `${item.score * 100}%`, 
                            height: '100%', 
                            background: `linear-gradient(90deg, ${styles.color}88, ${styles.color})`,
                            borderRadius: '3px'
                          }} />
                        </div>
                        <span style={{ fontSize: '0.875rem', fontWeight: 600, minWidth: '40px' }}>{item.score.toFixed(3)}</span>
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{
                        fontSize: '0.65rem',
                        fontWeight: 700,
                        padding: '4px 10px',
                        borderRadius: '20px',
                        background: styles.bg,
                        color: styles.color,
                        border: `1px solid ${styles.border}`
                      }}>
                        {item.level}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ 
          textAlign: 'center', 
          padding: '4rem 2rem', 
          border: '1px dashed rgba(255,255,255,0.1)', 
          borderRadius: '16px' 
        }}>
          <p style={{ margin: 0, color: '#94a3b8' }}>Ejecuta el scoring arriba para ver el ranking de oportunidades.</p>
        </div>
      )}
    </div>
  );
};

export default RankingList;
