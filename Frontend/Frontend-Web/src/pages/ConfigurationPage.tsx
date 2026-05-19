import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import { getConfigActive, saveScoringConfig } from '../services/bffApi';
import '../styles/Dashboard.css';

interface Weights {
    population_weight: number;
    income_weight: number;
    education_weight: number;
    competition_weight: number;
    business_profile_name: string;
}

const DEFAULTS: Weights = {
    population_weight: 0.25,
    income_weight: 0.25,
    education_weight: 0.25,
    competition_weight: 0.25,
    business_profile_name: 'general',
};

const ConfigurationPage: React.FC = () => {
    const { logout, username, role } = useAuth();
    const navigate = useNavigate();
    const [weights, setWeights] = React.useState<Weights>(DEFAULTS);
    const [loading, setLoading] = React.useState(false);
    const [message, setMessage] = React.useState<string | null>(null);
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        getConfigActive()
            .then((data) => setWeights({ ...DEFAULTS, ...data }))
            .catch(() => setWeights(DEFAULTS));
    }, []);

    const update = (key: keyof Weights, value: number) => setWeights({ ...weights, [key]: value });

    const preview = React.useMemo(() => {
        const sample = { pop: 0.7, ing: 0.6, edu: 0.5, comp: 0.4 };
        return (
            weights.population_weight * sample.pop +
            weights.income_weight * sample.ing +
            weights.education_weight * sample.edu -
            weights.competition_weight * sample.comp
        );
    }, [weights]);

    const submit = async () => {
        setLoading(true);
        setMessage(null);
        setError(null);
        try {
            await saveScoringConfig(weights);
            setMessage('Configuración guardada y activada.');
        } catch (e: any) {
            setError(e.message || 'Error al guardar');
        } finally {
            setLoading(false);
        }
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
                    <button className="nav-link" onClick={() => navigate('/compare')}>Comparador</button>
                    {role === 'ADMIN' && (
                        <>
                            <button className="nav-link" onClick={() => navigate('/admin/users')}>Gestion de Usuarios</button>
                            <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>Experimentos ML</button>
                            <button className="nav-link active" onClick={() => navigate('/configuration')}>Configuracion</button>
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
            <section className="admin-card" style={{ maxWidth: 640 }}>
                <div className="admin-form">
                    <div className="form-row">
                        <label>Perfil de negocio</label>
                        <input
                            type="text"
                            value={weights.business_profile_name}
                            onChange={(e) => setWeights({ ...weights, business_profile_name: e.target.value })}
                        />
                    </div>
                    {(['population_weight', 'income_weight', 'education_weight', 'competition_weight'] as const).map((key) => (
                        <div key={key} className="form-row" style={{ marginTop: 8 }}>
                            <label>
                                {key} ({weights[key].toFixed(2)})
                            </label>
                            <input
                                type="range"
                                min={0}
                                max={1}
                                step={0.05}
                                value={weights[key]}
                                onChange={(e) => update(key, Number(e.target.value))}
                                style={{ width: '100%' }}
                            />
                        </div>
                    ))}
                    <p style={{ marginTop: 16, marginBottom: 12 }}>
                        <strong>Score de muestra (pob=.7, ing=.6, edu=.5, comp=.4):</strong>{' '}
                        {preview.toFixed(3)}
                    </p>
                    <button className="admin-btn-primary" onClick={submit} disabled={loading}>
                        {loading ? 'Guardando...' : 'Guardar y activar'}
                    </button>
                    {message && <p className="admin-success" style={{ marginTop: 16 }}>{message}</p>}
                    {error && <p className="admin-error" style={{ marginTop: 16 }}>{error}</p>}
                </div>
            </section>
            </main>
        </div>
    );
};

export default ConfigurationPage;
