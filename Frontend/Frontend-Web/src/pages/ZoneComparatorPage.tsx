import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import { compareZones, CompareResponse, CompareRow } from '../services/bffApi';
import '../styles/Dashboard.css';

const MAX_ZONES = 5;

const DEPARTAMENTOS: Record<string, string[]> = {
  'Antioquia': ['Medellin', 'Bello', 'Itagui', 'Envigado', 'Rionegro', 'Apartado', 'Turbo', 'Caucasia'],
  'Valle del Cauca': ['Cali', 'Buenaventura', 'Palmira', 'Tulua', 'Manizales', 'Buga', 'Cartago'],
  'Cundinamarca': ['Bogota D.C.', 'Soacha', 'Fusagasuga', 'Facatativa', 'Zipaquira', 'Chia', 'Madrid'],
  'Atlantico': ['Barranquilla', 'Soledad', 'Malambo', 'Sabanalarga', 'Galapa', 'Puerto Colombia'],
  'Bolivar': ['Cartagena', 'Magangue', 'Turbaco', 'Arjona', 'El Carmen de Bolivar'],
  'Santander': ['Bucaramanga', 'Floridablanca', 'Giron', 'Piedecuesta', 'Barrancabermeja'],
  'Narino': ['Pasto', 'Tumaco', 'Ipiales', 'Tuquerres', 'La Union'],
  'Cordoba': ['Monteria', 'Planeta Rica', 'Sahagun', 'Lorica', 'Cerete'],
  'Tolima': ['Ibague', 'Espinal', 'Melgar', 'Chaparral', 'Girardot'],
  'Cauca': ['Popayan', 'Santander de Quilichao', 'Puerto Tejada', 'Guapi', 'Miranda'],
  'Huila': ['Neiva', 'Pitalito', 'Garzon', 'La Plata', 'Campoalegre'],
  'Boyaca': ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquira', 'Paipa'],
  'Magdalena': ['Santa Marta', 'Cienaga', 'Fundacion', 'El Banco', 'Plato'],
  'Cesar': ['Valledupar', 'Aguachica', 'Agustin Codazzi', 'La Jagua de Ibirico'],
  'Meta': ['Villavicencio', 'Acacias', 'Granada', 'Puerto Lopez', 'Restrepo'],
};

const ZoneComparatorPage: React.FC = () => {
    const { logout, username, role } = useAuth();
    const navigate = useNavigate();
    const [input, setInput] = React.useState('');
    const [zones, setZones] = React.useState<string[]>([]);
    const [result, setResult] = React.useState<CompareResponse | null>(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [tab, setTab] = React.useState<'indicators' | 'ai'>('indicators');
    
    const [selectedDept, setSelectedDept] = React.useState<string>('');
    const [municipioSearch, setMunicipioSearch] = React.useState('');

    const currentMunicipios = selectedDept ? DEPARTAMENTOS[selectedDept] ?? [] : [];
    const filteredMunicipios = currentMunicipios.filter(m =>
        m.toLowerCase().includes(municipioSearch.toLowerCase())
    );

    const addZone = () => {
        const code = input.trim();
        if (!code) return;
        if (zones.length >= MAX_ZONES) {
            setError(`Solo se pueden comparar hasta ${MAX_ZONES} zonas`);
            return;
        }
        if (zones.includes(code)) {
            setError('La zona ya fue agregada');
            return;
        }
        setZones([...zones, code]);
        setInput('');
        setError(null);
    };

    const toggleMunicipio = (m: string) => {
        if (zones.includes(m)) {
            removeZone(m);
        } else {
            if (zones.length >= MAX_ZONES) {
                setError(`Solo se pueden comparar hasta ${MAX_ZONES} zonas`);
                return;
            }
            setZones([...zones, m]);
            setError(null);
        }
    };

    const removeZone = (code: string) => setZones(zones.filter((z) => z !== code));

    const runCompare = async () => {
        if (zones.length < 2) {
            setError('Selecciona al menos dos zonas');
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const response = await compareZones(zones);
            setResult(response);
        } catch (e: any) {
            setError(e.message || 'Error al comparar');
        } finally {
            setLoading(false);
        }
    };

    const downloadCsv = () => {
        if (!result) return;
        const headers = ['zone_code', 'zone_name', 'score_value', 'score_level', 'combined_score', 'prediction_value'];
        const lines = [headers.join(',')];
        for (const row of result.zones) {
            lines.push(headers.map((h) => String((row as any)[h] ?? '')).join(','));
        }
        const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `comparativa.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const bestZone = (key: keyof CompareRow): string | null => {
        if (!result) return null;
        const candidates = result.zones.filter((z) => z[key] != null);
        if (!candidates.length) return null;
        return candidates.reduce((best, current) => (
            (current[key] as number) > (best[key] as number) ? current : best
        )).zone_code;
    };

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
                    <button className="nav-link active" onClick={() => navigate('/compare')}>Comparador</button>
                    {role === 'ADMIN' && (
                        <>
                            <button className="nav-link" onClick={() => navigate('/admin/users')}>Gestion de Usuarios</button>
                            <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>Experimentos ML</button>
                            <button className="nav-link" onClick={() => navigate('/configuration')}>Configuracion</button>
                            <button className="nav-link" onClick={() => navigate('/audit')}>Auditoria</button>
                        </>
                    )}
                </nav>
                <div className="dashboard-user">
                    
                    <span className="user-role-badge">{role}</span>
                    <button onClick={() => { logout(); navigate('/'); }} className="btn-logout">Salir</button>
                </div>
            </header>
            <main className="dashboard-main" style={{ padding: '2rem' }}>
            <div className="action-cards-grid" style={{ marginBottom: '1.5rem' }}>
              <div className="action-card action-card-blue">
                <div className="action-card-icon">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                </div>
                <div className="action-card-body">
                  <span className="action-card-title">Territorios</span>
                  <select
                    className="dept-select"
                    value={selectedDept}
                    onChange={e => {
                      setSelectedDept(e.target.value);
                      setMunicipioSearch('');
                    }}
                  >
                    <option value="">Seleccionar...</option>
                    {Object.keys(DEPARTAMENTOS).sort().map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="municipios-section" style={{ marginBottom: '2rem' }}>
              <div className="municipios-header">
                <div className="municipios-title">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  <span>Municipios Cargados</span>
                </div>
                <div className="municipios-search-wrap">
                  <input
                    type="text"
                    className="municipios-search"
                    placeholder="Buscar municipio..."
                    value={municipioSearch}
                    onChange={e => setMunicipioSearch(e.target.value)}
                    disabled={!selectedDept}
                  />
                </div>
              </div>

              <div className="municipios-body">
                {!selectedDept ? (
                  <div className="municipios-empty">
                    <p>Selecciona un departamento para ver sus municipios.</p>
                  </div>
                ) : filteredMunicipios.length === 0 ? (
                  <div className="municipios-empty">
                    <p>No se encontraron municipios con ese criterio.</p>
                  </div>
                ) : (
                  <div className="municipios-grid">
                    {filteredMunicipios.map(m => (
                      <button
                        key={m}
                        className={`municipio-chip ${zones.includes(m) ? 'selected' : ''}`}
                        onClick={() => toggleMunicipio(m)}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <section className="admin-card">
                <h2>Zonas seleccionadas ({zones.length}/{MAX_ZONES})</h2>
                <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                    <input
                        placeholder="zone_code (ej. BOG-001)"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') addZone(); }}
                        style={{ padding: '0.55rem 0.85rem', borderRadius: 10, background: 'rgba(255,255,255,0.05)', color: '#f1f5f9', border: '1px solid rgba(255,255,255,0.12)' }}
                    />
                    <button className="admin-btn-primary" onClick={addZone}>Agregar zona</button>
                    <button className="admin-btn-primary" onClick={runCompare} disabled={zones.length < 2 || loading}>
                        {loading ? 'Comparando...' : 'Comparar'}
                    </button>
                    <button className="admin-btn-secondary" onClick={downloadCsv} disabled={!result}>
                        Exportar CSV
                    </button>
                </div>
                {error && <p className="admin-error">{error}</p>}
                
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {zones.map((z) => (
                        <span key={z} className="badge" style={{ padding: '4px 10px', background: 'rgba(255,255,255,0.1)', borderRadius: 12, fontSize: '0.875rem' }}>
                            {z}
                            <button onClick={() => removeZone(z)} style={{ marginLeft: 8, cursor: 'pointer', background: 'none', border: 'none', color: '#fca5a5' }}>x</button>
                        </span>
                    ))}
                </div>
            </section>

            {result && (
                <section className="admin-card">
                    <div style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: 16, display: 'flex', gap: 16 }}>
                        <button
                            style={{
                                background: 'transparent',
                                border: 'none',
                                padding: '8px 0',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                color: tab === 'indicators' ? '#818cf8' : '#94a3b8',
                                borderBottom: tab === 'indicators' ? '2px solid #818cf8' : '2px solid transparent'
                            }}
                            onClick={() => setTab('indicators')}
                        >
                            Indicadores
                        </button>
                        <button
                            style={{
                                background: 'transparent',
                                border: 'none',
                                padding: '8px 0',
                                cursor: 'pointer',
                                fontWeight: 'bold',
                                color: tab === 'ai' ? '#818cf8' : '#94a3b8',
                                borderBottom: tab === 'ai' ? '2px solid #818cf8' : '2px solid transparent'
                            }}
                            onClick={() => setTab('ai')}
                        >
                            Vista IA
                        </button>
                    </div>
                    {tab === 'indicators' ? (
                        <table className="admin-table" style={{ width: '100%' }}>
                            <thead>
                                <tr>
                                    <th>Zona</th>
                                    <th>Población</th>
                                    <th>Ingreso</th>
                                    <th>Educación</th>
                                    <th>Competencia</th>
                                    <th>Score</th>
                                    <th>Nivel</th>
                                </tr>
                            </thead>
                            <tbody>
                                {result.zones.map((z) => (
                                    <tr key={z.zone_code} style={z.zone_code === bestZone('score_value') ? { background: '#e8f5e9' } : {}}>
                                        <td>{z.zone_name}</td>
                                        <td>{z.indicators?.population_indicator?.toFixed(2) ?? '—'}</td>
                                        <td>{z.indicators?.income_indicator?.toFixed(2) ?? '—'}</td>
                                        <td>{z.indicators?.education_indicator?.toFixed(2) ?? '—'}</td>
                                        <td>{z.indicators?.competition_indicator?.toFixed(2) ?? '—'}</td>
                                        <td>{z.score_value?.toFixed(2) ?? '—'}</td>
                                        <td>{z.score_level ?? '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <table className="table" style={{ width: '100%' }}>
                            <thead>
                                <tr>
                                    <th>Zona</th>
                                    <th>Score</th>
                                    <th>Predicción IA</th>
                                    <th>Etiqueta</th>
                                    <th>Combinado</th>
                                    <th>Revisar</th>
                                </tr>
                            </thead>
                            <tbody>
                                {result.zones.map((z) => (
                                    <tr key={z.zone_code} style={z.zone_code === bestZone('combined_score') ? { background: '#e3f2fd' } : {}}>
                                        <td>{z.zone_name}</td>
                                        <td>{z.score_value?.toFixed(2) ?? '—'}</td>
                                        <td>{z.prediction_value?.toFixed(2) ?? '—'}</td>
                                        <td>{z.prediction_label ?? '—'}</td>
                                        <td>{z.combined_score?.toFixed(2) ?? '—'}</td>
                                        <td>{z.discrepancy_flag ? 'Si' : 'No'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                    <p style={{ marginTop: 12, fontStyle: 'italic' }}>
                        {(() => {
                            const winner = result.zones.find((z) => z.zone_code === bestZone('combined_score'));
                            if (!winner) return 'Sin datos suficientes para una síntesis automática.';
                            return `La zona ${winner.zone_name} obtiene el mayor combined_score (${winner.combined_score?.toFixed(2) ?? '—'}) y por tanto es la más recomendada.`;
                        })()}
                    </p>
                </section>
            )}
            </main>
        </div>
    );
};

export default ZoneComparatorPage;
