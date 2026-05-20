import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import '../styles/Dashboard.css';
import '../styles/Analysis.css';

interface Indicator { name: string; value: number; }
interface Zone {
  name: string;
  zone_code: string;
  score: number;
  indicators: Indicator[];
  level: 'Alto' | 'Medio' | 'Bajo' | 'Critico';
  recommendation: string;
}

const INDICATORS_NAMES = ['Poblacion', 'Ingresos', 'Educacion', 'Competitividad'];

const BOGOTA_SEED = [
  { code: 'BOG-001', name: 'Chapinero', pop: 18500, inc: 4200000, edu: 88, eco: 85, com: 92 },
  { code: 'BOG-002', name: 'Usaquen', pop: 16200, inc: 5100000, edu: 90, eco: 82, com: 88 },
  { code: 'BOG-003', name: 'Suba', pop: 22500, inc: 2400000, edu: 72, eco: 65, com: 70 },
  { code: 'BOG-004', name: 'Kennedy', pop: 25100, inc: 1800000, edu: 65, eco: 58, com: 68 },
  { code: 'BOG-005', name: 'Engativa', pop: 23000, inc: 2100000, edu: 70, eco: 62, com: 65 },
  { code: 'BOG-006', name: 'Bosa', pop: 24800, inc: 1500000, edu: 58, eco: 48, com: 52 },
  { code: 'BOG-007', name: 'Fontibon', pop: 17500, inc: 3100000, edu: 78, eco: 75, com: 80 },
  { code: 'BOG-008', name: 'Puente Aranda', pop: 19000, inc: 2700000, edu: 74, eco: 78, com: 82 },
  { code: 'BOG-009', name: 'Barrios Unidos', pop: 17800, inc: 2900000, edu: 76, eco: 70, com: 75 },
  { code: 'BOG-010', name: 'Teusaquillo', pop: 13500, inc: 3800000, edu: 85, eco: 72, com: 78 },
  { code: 'BOG-011', name: 'Bosa Occidental', pop: 26200, inc: 1300000, edu: 52, eco: 42, com: 45 },
  { code: 'BOG-012', name: 'Ciudad Bolivar', pop: 27500, inc: 1100000, edu: 48, eco: 38, com: 40 },
  { code: 'BOG-013', name: 'San Cristobal', pop: 21000, inc: 1700000, edu: 60, eco: 50, com: 55 },
  { code: 'BOG-014', name: 'Antonio Narino', pop: 16500, inc: 2300000, edu: 68, eco: 64, com: 72 },
  { code: 'BOG-015', name: 'Tunjuelito', pop: 22000, inc: 1600000, edu: 62, eco: 52, com: 58 },
  { code: 'BOG-016', name: 'La Candelaria', pop: 12000, inc: 3200000, edu: 82, eco: 70, com: 75 },
  { code: 'BOG-017', name: 'Los Martires', pop: 14500, inc: 2500000, edu: 71, eco: 68, com: 73 },
  { code: 'BOG-018', name: 'Santa Fe', pop: 15800, inc: 2200000, edu: 66, eco: 60, com: 65 },
  { code: 'BOG-019', name: 'Rafael Uribe', pop: 23500, inc: 1450000, edu: 55, eco: 45, com: 48 },
  { code: 'BOG-020', name: 'Usme', pop: 26800, inc: 1200000, edu: 50, eco: 40, com: 42 },
];

const RECOMENDATIONS: Record<Zone['level'], string> = {
  Alto: 'Zona con excelente desempeno territorial. Se recomienda mantener inversion y fortalecer indicadores de riesgo.',
  Medio: 'Zona con desempeno moderado. Priorizar mejora en cobertura de servicios y acceso vial.',
  Bajo: 'Zona deficiente. Intervencion urgente en infraestructura vial y servicios basicos.',
  Critico: 'Zona critica. Requiere plan de emergencia territorial y reasignacion presupuestaria.',
};

function normalize(values: number[], invert = false): number[] {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return values.map((v) => {
    const norm = (v - min) / span;
    return invert ? 1 - norm : norm;
  });
}

function levelOf(score: number): Zone['level'] {
  if (score >= 75) return 'Alto';
  if (score >= 50) return 'Medio';
  if (score >= 30) return 'Bajo';
  return 'Critico';
}

function computeZones(rawRows: any[], jitter: number): Zone[] {
  const rows = rawRows.map((r, i) => ({
    code: r.zone_code ?? r.code ?? `Z-${i + 1}`,
    name: r.zone_name ?? r.name ?? `Zona ${i + 1}`,
    pop: Number(r.population_density ?? r.pop ?? r.matriculados_oficial ?? 0),
    inc: Number(r.average_income ?? r.inc ?? r.ingreso_per_capita ?? 0),
    edu: Number(r.education_level ?? r.edu ?? r.puntaje_saber_11 ?? 0),
    eco: Number(r.economic_activity_index ?? r.eco ?? (r.tasa_desempleo ? 100 - r.tasa_desempleo : 0) ?? 0),
    com: Number(r.commercial_presence_index ?? r.com ?? (r.indice_pobreza_multidimensional ? 100 - r.indice_pobreza_multidimensional : 0) ?? 0),
  }));

  const popN = normalize(rows.map((r) => r.pop));
  const incN = normalize(rows.map((r) => r.inc));
  const eduN = normalize(rows.map((r) => r.edu));
  const ecoN = normalize(rows.map((r) => r.eco));
  const comN = normalize(rows.map((r) => r.com));

  const zones: Zone[] = rows.map((r, i) => {
    const noise = () => (Math.sin(jitter + i * 1.7) * 0.06);
    const popInd = Math.max(0, Math.min(1, popN[i] + noise()));
    const incInd = Math.max(0, Math.min(1, incN[i] + noise()));
    const eduInd = Math.max(0, Math.min(1, eduN[i] + noise()));
    const compInd = Math.max(0, Math.min(1, (ecoN[i] + comN[i]) / 2 + noise()));
    const raw = 0.3 * popInd + 0.3 * incInd + 0.2 * eduInd + 0.2 * compInd;
    const score = Math.round(Math.max(0, Math.min(1, raw)) * 100);
    const indicators: Indicator[] = [
      { name: 'Poblacion', value: Math.round(popInd * 100) },
      { name: 'Ingresos', value: Math.round(incInd * 100) },
      { name: 'Educacion', value: Math.round(eduInd * 100) },
      { name: 'Competitividad', value: Math.round(compInd * 100) },
    ];
    const level = levelOf(score);
    return {
      name: r.name,
      zone_code: r.code,
      score,
      indicators,
      level,
      recommendation: RECOMENDATIONS[level],
    };
  });
  return zones.sort((a, b) => b.score - a.score);
}

function getBarColor(score: number) {
  if (score >= 75) return '#4ade80';
  if (score >= 50) return '#818cf8';
  if (score >= 30) return '#facc15';
  return '#fca5a5';
}

function getFillClass(value: number) {
  if (value >= 70) return 'fill-high';
  if (value >= 45) return 'fill-blue';
  if (value >= 25) return 'fill-mid';
  return 'fill-danger';
}

function getLevelClass(level: Zone['level']) {
  if (level === 'Alto') return 'level-alto';
  if (level === 'Medio') return 'level-medio';
  if (level === 'Bajo') return 'level-bajo';
  return 'level-critico';
}

function getBadgeClass(rank: number) {
  if (rank === 0) return 'badge-gold';
  if (rank === 1) return 'badge-silver';
  if (rank === 2) return 'badge-bronze';
  if (rank < 6) return 'badge-blue';
  return 'badge-gray';
}

function heatColor(value: number) {
  const r = value < 50 ? 220 : Math.round(220 - (value - 50) * 3.2);
  const g = value > 50 ? 190 : Math.round(value * 3.8);
  return {
    bg: `rgba(${r}, ${g}, 60, 0.25)`,
    color: value >= 60 ? '#4ade80' : value >= 35 ? '#facc15' : '#fca5a5',
  };
}

const ZoneDetailCard: React.FC<{ zone: Zone; rank: number; onClose?: () => void }> = ({ zone, rank, onClose }) => (
  <div className="glass-card detail-card" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div className="detail-zone-header" style={{ border: 'none', paddingBottom: 0 }}>
        <div className={`detail-zone-badge ${getBadgeClass(rank)}`}>#{rank + 1}</div>
        <div>
          <div className="detail-zone-name">{zone.name}</div>
          <span className={`detail-zone-level ${getLevelClass(zone.level)}`}>{zone.level}</span>
        </div>
      </div>
      {onClose && (
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem', padding: '0.25rem' }}>x</button>
      )}
    </div>
    <div className="detail-score-row">
      <span className="detail-score-value">{zone.score}</span>
      <span className="detail-score-max">/ 100 pts</span>
    </div>
    <div className="detail-recommendation">{zone.recommendation}</div>
    <div>
      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
        INDICADORES
      </div>
      <div className="indicators-list">
        {zone.indicators.map((ind) => (
          <div key={ind.name} className="indicator-row">
            <div className="indicator-meta">
              <span className="indicator-name">{ind.name}</span>
              <span className="indicator-val">{ind.value}</span>
            </div>
            <div className="progress-track">
              <div className={`progress-fill ${getFillClass(ind.value)}`} style={{ width: `${ind.value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const HeatmapTable: React.FC<{ zones: Zone[] }> = ({ zones }) => {
  const top15 = zones.slice(0, 15);
  return (
    <div className="glass-card heatmap-section">
      <div className="card-title">Mapa de Calor de Indicadores</div>
      <div className="card-subtitle">Intensidad por zona. Verde = alto, rojo = bajo</div>
      <div className="heatmap-scroll">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th className="col-zone">Zona</th>
              {INDICATORS_NAMES.map((n) => <th key={n}>{n}</th>)}
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {top15.map((zone) => (
              <tr key={zone.zone_code}>
                <td className="zone-name-cell">{zone.name}</td>
                {zone.indicators.map((ind) => {
                  const { bg, color } = heatColor(ind.value);
                  return (
                    <td key={ind.name} className="heat-cell" style={{ background: bg, color }}>{ind.value}</td>
                  );
                })}
                <td style={{ ...heatColor(zone.score), background: heatColor(zone.score).bg, color: heatColor(zone.score).color, fontWeight: 800 }}>{zone.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const RecommendationsSection: React.FC<{ zones: Zone[] }> = ({ zones }) => {
  const topZones = zones.slice(0, 15);
  return (
    <div className="glass-card" style={{ marginTop: '1rem' }}>
      <div className="card-title">Recomendaciones Estratégicas</div>
      <div className="card-subtitle">Acciones sugeridas basadas en el desempeño territorial de las principales zonas</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginTop: '1.25rem' }}>
        {topZones.map((zone, i) => (
          <div key={zone.zone_code} style={{ padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className={`detail-zone-badge ${getBadgeClass(i)}`} style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}>#{i + 1}</span>
                <strong style={{ color: '#f1f5f9', fontSize: '0.95rem' }}>{zone.name}</strong>
              </div>
              <span className={`detail-zone-level ${getLevelClass(zone.level)}`} style={{ fontSize: '0.7rem' }}>{zone.level}</span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', lineHeight: '1.6', margin: 0 }}>
              {zone.recommendation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

const AnalysisPage: React.FC = () => {
  const { username, role, logout } = useAuth();
  const navigate = useNavigate();

  const [datasets, setDatasets] = useState<{ id: string; label: string; rows: any[] }[]>([]);
  const [datasetId, setDatasetId] = useState('');
  const [zones, setZones] = useState<Zone[]>([]);
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const [pinnedIdx, setPinnedIdx] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [jitter, setJitter] = useState(0);

  useEffect(() => {
    const initial = [
      { id: 'bogota_desarrollo', label: 'bogota_desarrollo_socioeconomico.json', rows: BOGOTA_SEED.map((r) => ({
        zone_code: r.code, zone_name: r.name,
        population_density: r.pop, average_income: r.inc,
        education_level: r.edu, economic_activity_index: r.eco, commercial_presence_index: r.com,
      })) },
    ];
    setDatasets(initial);
    setDatasetId(initial[0].id);
  }, []);

  const runAnalysis = useCallback(() => {
    if (!datasetId) return;
    const ds = datasets.find((d) => d.id === datasetId);
    if (!ds) return;
    setRunning(true);
    const seed = Date.now();
    setJitter(seed);
    setTimeout(() => {
      const result = computeZones(ds.rows, seed / 1000);
      setZones(result);
      try {
        localStorage.setItem('latestAnalysis', JSON.stringify({
          execution_id: `exec_${seed}`,
          dataset: ds.label,
          generated_at: new Date().toISOString(),
          zones: result,
        }));
        localStorage.setItem('lastExecutionId', `exec_${seed}`);
      } catch {
        // ignore quota
      }
      setRunning(false);
    }, 700);
  }, [datasetId, datasets]);

  useEffect(() => {
    if (datasetId && zones.length === 0) {
      runAnalysis();
    }
  }, [datasetId, runAnalysis, zones.length]);

  const handleReset = () => {
    setZones([]);
    setHoverIdx(null);
    setPinnedIdx(null);
    runAnalysis();
  };

  const handleFileLoad = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const text = await file.text();
      let rows: any[] = [];
      if (file.name.endsWith('.json')) {
        rows = JSON.parse(text);
      } else {
        const lines = text.split(/\r?\n/).filter(Boolean);
        const headers = lines[0].split(',').map((h) => h.trim());
        rows = lines.slice(1).map((ln) => {
          const cells = ln.split(',');
          const obj: any = {};
          headers.forEach((h, i) => { obj[h] = cells[i]?.trim(); });
          return obj;
        });
      }
      const id = file.name.replace(/\.[^.]+$/, '');
      setDatasets((prev) => [...prev.filter((d) => d.id !== id), { id, label: file.name, rows }]);
      setDatasetId(id);
      setZones([]);
    } catch (err) {
      alert('No se pudo leer el archivo. Verifica el formato.');
    }
  };

  const top10 = useMemo(() => zones.slice(0, 10), [zones]);
  const chartData = top10.map((z, i) => ({ name: z.name, score: z.score, index: i }));
  const activeIdx = hoverIdx ?? pinnedIdx;
  const activeZone = activeIdx != null ? top10[activeIdx] : null;

  return (
    <div className="analysis-page">
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Analisis Territorial</span>
        </div>
        <nav className="dashboard-nav">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>Dashboard</button>
          {role === 'ADMIN' && (
            <>
              <button className="nav-link" onClick={() => navigate('/admin/users')}>Gestion de Usuarios</button>
              <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>Experimentos ML</button>
            </>
          )}
        </nav>
        <div className="dashboard-user">
          <span className="user-greeting">Hola, <strong>{username}</strong></span>
          <span className="user-role-badge">{role}</span>
          <button onClick={() => { logout(); navigate('/'); }} className="btn-logout">Salir</button>
        </div>
      </header>

      <main className="analysis-main" style={{ padding: '2rem' }}>
        <section className="admin-card">
          <h3 style={{ color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.85rem' }}>DATASET DE ANALISIS</h3>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <select
              value={datasetId}
              onChange={(e) => { setDatasetId(e.target.value); setZones([]); }}
              style={{ flex: '1 1 320px', minWidth: 280, padding: '0.6rem 0.85rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.12)', color: '#f1f5f9', borderRadius: 10 }}
            >
              {datasets.map((d) => <option key={d.id} value={d.id} style={{ background: '#1e293b', color: '#f1f5f9' }}>{d.label}</option>)}
            </select>
            <label className="admin-btn-secondary" style={{ cursor: 'pointer', background: 'rgba(255,255,255,0.1)', color: '#fff', border: 'none', borderRadius: '10px', padding: '0.6rem 1rem' }}>
              Cargar archivo
              <input type="file" hidden accept=".csv,.json" onChange={handleFileLoad} />
            </label>
            <button className="admin-btn-primary" onClick={handleReset} disabled={running} style={{ background: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', padding: '0.6rem 1rem', cursor: 'pointer' }}>
              {running ? 'Calculando...' : 'Reiniciar / Recalcular'}
            </button>
          </div>
        </section>

        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 320px', gap: 16, marginTop: 16 }}>
          <section className="admin-card" style={{ padding: '1.5rem' }}>
            <h2 style={{ color: '#f1f5f9', marginBottom: 4 }}>Top 10 Zonas por Score</h2>
            <p style={{ color: '#94a3b8', marginTop: 0, marginBottom: 16 }}>
              Pasa el cursor sobre cada barra para ver el detalle de la zona.
            </p>
            <div style={{ width: '100%', height: 380 }} onMouseLeave={() => setHoverIdx(null)}>
              <ResponsiveContainer>
                <BarChart data={chartData} margin={{ top: 10, right: 20, bottom: 60, left: 0 }} onMouseMove={(state) => {
                  if (state && state.activeTooltipIndex !== undefined && state.activeTooltipIndex !== null) {
                    setHoverIdx(state.activeTooltipIndex);
                  }
                }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#94a3b8" interval={0} angle={-30} textAnchor="end" tickMargin={8} fontSize={11} />
                  <YAxis stroke="#94a3b8" domain={[0, 100]} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.04)' }} contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                  <Bar dataKey="score" radius={[8, 8, 0, 0]} onClick={(_, idx) => setPinnedIdx(idx)}>
                    {chartData.map((d) => (
                      <Cell key={d.name} fill={getBarColor(d.score)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {activeZone ? (
            <ZoneDetailCard zone={activeZone} rank={activeIdx ?? 0} onClose={pinnedIdx != null ? () => setPinnedIdx(null) : undefined} />
          ) : (
            <div className="admin-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', textAlign: 'center', padding: '2rem' }}>
              Pasa el cursor sobre una barra para ver el detalle de la zona.
            </div>
          )}
        </div>

        {zones.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <HeatmapTable zones={zones} />
            <RecommendationsSection zones={zones} />
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalysisPage;
