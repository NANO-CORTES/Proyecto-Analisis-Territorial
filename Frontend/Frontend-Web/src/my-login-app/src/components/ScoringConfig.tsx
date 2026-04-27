import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthProvider';

interface Profile {
  id: string;
  name: string;
  description: string;
}

interface ScoringConfigProps {
  onScoringExecuted: (executionId: string) => void;
}

const ScoringConfig: React.FC<ScoringConfigProps> = ({ onScoringExecuted }) => {
  const { token } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState('');
  const [weights, setWeights] = useState({
    population: 0.25,
    income: 0.25,
    education: 0.25,
    competition: 0.25
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Mapa de pesos recomendados por tipo de negocio
  const RECOMMENDED_WEIGHTS: Record<string, typeof weights> = {
    "Tiendas de Conveniencia": { population: 0.45, income: 0.15, education: 0.10, competition: 0.30 },
    "Gimnasios / Centros Deportivos": { population: 0.30, income: 0.30, education: 0.20, competition: 0.20 },
    "Inmobiliaria de Lujo": { population: 0.10, income: 0.70, education: 0.10, competition: 0.10 },
    "Farmacias / Salud": { population: 0.50, income: 0.10, education: 0.10, competition: 0.30 },
    "Servicios Médicos / Clínicas": { population: 0.35, income: 0.35, education: 0.15, competition: 0.15 },
    "Instituciones Educativas": { population: 0.30, income: 0.20, education: 0.40, competition: 0.10 },
    "Entidades Bancarias / Cajeros": { population: 0.25, income: 0.45, education: 0.10, competition: 0.20 },
    "Restaurantes de Comida Rápida": { population: 0.50, income: 0.15, education: 0.05, competition: 0.30 },
    "Centros de Distribución (Logística)": { population: 0.30, income: 0.20, education: 0.10, competition: 0.40 },
    "Hoteles y Turismo": { population: 0.15, income: 0.40, education: 0.15, competition: 0.30 },
    "Coworking / Oficinas": { population: 0.20, income: 0.40, education: 0.30, competition: 0.10 },
    "Supermercados de Gran Superficie": { population: 0.55, income: 0.20, education: 0.05, competition: 0.20 },
    "Centros de Estética y Bienestar": { population: 0.25, income: 0.45, education: 0.10, competition: 0.20 }
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  // Actualizar pesos cuando cambia el perfil
  useEffect(() => {
    const currentProfile = profiles.find(p => p.id === selectedProfileId);
    if (currentProfile) {
      // Buscar coincidencia exacta o usar valores por defecto equilibrados
      const newWeights = RECOMMENDED_WEIGHTS[currentProfile.name] || {
        population: 0.25, income: 0.25, education: 0.25, competition: 0.25
      };
      setWeights(newWeights);
    }
  }, [selectedProfileId, profiles]);

  const fetchProfiles = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/configuration/api/v1/config/profiles', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data: Profile[] = await res.json();
        // Deduplicar por nombre
        const uniqueProfiles = data.filter((v, i, a) => a.findIndex(t => t.name === v.name) === i);
        setProfiles(uniqueProfiles);
        if (uniqueProfiles.length > 0) setSelectedProfileId(uniqueProfiles[0].id);
      }
    } catch (err) {
      console.error("Error fetching profiles:", err);
    }
  };

  const handleWeightChange = (name: keyof typeof weights, value: number) => {
    setWeights(prev => ({ ...prev, [name]: value }));
  };

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);
  const isTotalValid = Math.abs(totalWeight - 1.0) < 0.001;

  const handleSaveAndExecute = async () => {
    if (!isTotalValid) {
      setMessage({ type: 'error', text: 'La suma de los pesos debe ser exactamente 1.0 (100%)' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      // 1. Guardar Configuración de Pesos
      const configRes = await fetch('http://127.0.0.1:8000/api/v1/configuration/api/v1/config/scoring', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          profile_id: selectedProfileId,
          population_weight: weights.population,
          income_weight: weights.income,
          education_weight: weights.education,
          competition_weight: weights.competition
        })
      });

      if (!configRes.ok) throw new Error('Error al guardar la configuración de pesos');

      // 2. Obtener el último Run ID de Transformación (usando el prefijo correcto)
      const transRes = await fetch('http://127.0.0.1:8000/api/v1/transformation/api/v1/transform/results', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const transData = await transRes.json();
      const lastRunId = transData.length > 0 ? transData[0].id : null;

      if (!lastRunId) {
        throw new Error('No se encontró una transformación previa para ejecutar el scoring');
      }

      // 3. Ejecutar Scoring
      const scoringRes = await fetch(`http://127.0.0.1:8000/api/v1/analytics/api/v1/scoring/execute?transformation_run_id=${lastRunId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!scoringRes.ok) throw new Error('Error al ejecutar el motor de scoring');
      
      const result = await scoringRes.json();
      setMessage({ type: 'success', text: '¡Scoring ejecutado con éxito!' });
      onScoringExecuted(result.execution_id);

    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handlePrevProfile = () => {
    const currentIndex = profiles.findIndex(p => p.id === selectedProfileId);
    const prevIndex = (currentIndex - 1 + profiles.length) % profiles.length;
    if (profiles.length > 0) setSelectedProfileId(profiles[prevIndex].id);
  };

  const handleNextProfile = () => {
    const currentIndex = profiles.findIndex(p => p.id === selectedProfileId);
    const nextIndex = (currentIndex + 1) % profiles.length;
    if (profiles.length > 0) setSelectedProfileId(profiles[nextIndex].id);
  };

  const currentProfile = profiles.find(p => p.id === selectedProfileId);

  return (
    <div className="scoring-config-card" style={{
      background: 'rgba(255, 255, 255, 0.03)',
      borderRadius: '20px',
      padding: '1.5rem',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      marginBottom: '1.5rem',
      position: 'relative',
      overflow: 'hidden',
      backdropFilter: 'blur(10px)'
    }}>
      <style>{`
        @keyframes fadeInScale {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        .carousel-button {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: white;
          width: 32px;
          height: 32px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .carousel-button:hover {
          background: #6366f1;
          border-color: #818cf8;
          transform: scale(1.1);
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }
        .carousel-button:active {
          transform: scale(0.95);
        }
        .profile-display {
          flex: 1;
          text-align: center;
          padding: 0 0.5rem;
          animation: fadeInScale 0.3s ease-out;
        }
        .profile-name {
          font-size: 0.95rem;
          font-weight: 600;
          color: #fff;
          margin-bottom: 0.15rem;
          display: block;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .profile-desc {
          font-size: 0.65rem;
          opacity: 0.5;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      `}</style>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{
          background: 'linear-gradient(135deg, #10b981, #3b82f6)',
          padding: '0.6rem',
          borderRadius: '12px',
          boxShadow: '0 4px 10px rgba(16, 185, 129, 0.2)'
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
            <path d="M12 20v-6M9 20v-10M12 4v4M15 20v-4M12 8l4 4M12 8l-4 4" />
          </svg>
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 600 }}>Configuración de Scoring</h2>
          <p style={{ margin: 0, opacity: 0.5, fontSize: '0.8rem' }}>Estrategia de análisis territorial</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
        {/* Selector de Perfil Tipo Carousel */}
        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
          <label style={{ 
            display: 'block', 
            marginBottom: '0.5rem', 
            fontSize: '0.7rem', 
            opacity: 0.6, 
            fontWeight: 600, 
            textTransform: 'uppercase', 
            letterSpacing: '1px'
          }}>
            Modelo de Negocio Seleccionado
          </label>
          
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              background: 'rgba(0,0,0,0.3)', 
              padding: '0.75rem', 
              borderRadius: '16px',
              border: '1px solid rgba(255,255,255,0.08)',
              outline: 'none',
              transition: 'all 0.3s',
              cursor: 'pointer'
            }}
            tabIndex={0}
            onKeyDown={(e) => {
              if (['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp'].includes(e.key)) {
                e.preventDefault(); // Prevenir scroll de la página
                if (e.key === 'ArrowRight' || e.key === 'ArrowDown') handleNextProfile();
                if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') handlePrevProfile();
              }
            }}
            onFocus={(e) => e.currentTarget.style.borderColor = '#6366f1'}
            onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'}
          >
            <button className="carousel-button" onClick={(e) => { e.stopPropagation(); handlePrevProfile(); }} title="Anterior">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>

            <div className="profile-display" key={selectedProfileId}>
              <span className="profile-name">{currentProfile?.name || 'Cargando...'}</span>
              <span className="profile-desc">{currentProfile?.target_business_type || 'MODELO SELECCIONADO'}</span>
            </div>

            <button className="carousel-button" onClick={(e) => { e.stopPropagation(); handleNextProfile(); }} title="Siguiente">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </div>

        {/* Sliders de Pesos */}
        <div style={{ gridColumn: 'span 2', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {[
            { label: 'Población', key: 'population', color: '#6366f1' },
            { label: 'Ingresos', key: 'income', color: '#10b981' },
            { label: 'Educación', key: 'education', color: '#f59e0b' },
            { label: 'Competencia', key: 'competition', color: '#ef4444' }
          ].map((item) => (
            <div key={item.key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8125rem', opacity: 0.8 }}>{item.label}</span>
                <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{(weights[item.key as keyof typeof weights] * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range" 
                min="0" max="1" step="0.05"
                value={weights[item.key as keyof typeof weights]}
                onChange={(e) => handleWeightChange(item.key as keyof typeof weights, parseFloat(e.target.value))}
                style={{
                  width: '100%',
                  accentColor: item.color,
                  height: '4px',
                  background: 'rgba(255,255,255,0.1)',
                  borderRadius: '2px',
                  cursor: 'pointer'
                }}
              />
            </div>
          ))}
        </div>
      </div>

      <div style={{ 
        marginTop: '2rem', 
        padding: '1.5rem', 
        background: isTotalValid ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)',
        borderRadius: '12px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        border: `1px solid ${isTotalValid ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)'}`
      }}>
        <div>
          <span style={{ fontSize: '0.875rem', opacity: 0.6 }}>Total Acumulado:</span>
          <strong style={{ marginLeft: '0.5rem', fontSize: '1.1rem', color: isTotalValid ? '#10b981' : '#ef4444' }}>
            {(totalWeight * 100).toFixed(0)}%
          </strong>
        </div>
        
        <button 
          onClick={handleSaveAndExecute}
          disabled={loading || !isTotalValid}
          style={{
            padding: '0.75rem 2rem',
            background: isTotalValid ? 'linear-gradient(135deg, #10b981, #059669)' : 'rgba(255,255,255,0.05)',
            border: 'none',
            borderRadius: '10px',
            color: 'white',
            fontWeight: 600,
            cursor: loading || !isTotalValid ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
            boxShadow: isTotalValid ? '0 4px 12px rgba(16, 185, 129, 0.2)' : 'none'
          }}
        >
          {loading ? 'Procesando...' : 'Guardar y Ejecutar Scoring'}
        </button>
      </div>

      {message && (
        <div style={{ 
          marginTop: '1rem', 
          padding: '1rem', 
          borderRadius: '8px',
          background: message.type === 'success' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
          color: message.type === 'success' ? '#10b981' : '#ef4444',
          fontSize: '0.875rem',
          textAlign: 'center'
        }}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default ScoringConfig;
