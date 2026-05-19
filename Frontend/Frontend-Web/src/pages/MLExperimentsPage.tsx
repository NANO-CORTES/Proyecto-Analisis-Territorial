import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import '../styles/Dashboard.css';
import '../styles/UserManagement.css';

interface Experiment {
  id: string;
  transformation_run_id: string;
  algorithm: string;
  target_variable: string;
  r2_score: number;
  mae: number;
  rmse: number;
  created_at: string;
  status: string;
  trained_models: { id: string; storage_path: string; is_active: boolean }[];
}

const MLExperimentsPage: React.FC = () => {
  const { username, role, logout, token } = useAuth();
  const navigate = useNavigate();

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form state
  const [transformationRunId, setTransformationRunId] = useState('');
  const [algorithm, setAlgorithm] = useState('linear_regression');
  const [targetVariable, setTargetVariable] = useState('territorial_score');
  
  // Fake or fetched runs
  const [runs, setRuns] = useState<{id: string, started_at: string}[]>([]);

  useEffect(() => {
    if (role !== 'ADMIN') {
      navigate('/dashboard');
    } else {
      fetchExperiments();
      fetchTransformationRuns();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role, navigate]);

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const fetchExperiments = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await axios.get(`${apiBase}/api/v1/ml/experiments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExperiments(res.data);
    } catch (err: any) {
      setError('Error al cargar experimentos');
    } finally {
      setLoading(false);
    }
  };

  const fetchTransformationRuns = async () => {
    try {
      // Intentar obtener de transformation, si no, mock
      const res = await axios.get(`${apiBase}/api/v1/transformation/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRuns(res.data);
    } catch (err) {
      console.warn("No se pudieron cargar runs, mostrando default");
      setRuns([{id: "default_run", started_at: new Date().toISOString()}]);
    }
  };

  const handleTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transformationRunId) {
      alert("Seleccione un transformation run");
      return;
    }
    setLoading(true);
    setError('');
    try {
      await axios.post(`${apiBase}/api/v1/ml/experiments`, {
        transformation_run_id: transformationRunId,
        algorithm,
        target_variable: targetVariable
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchExperiments();
    } catch (err: any) {
      setError('Error al entrenar el modelo');
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await axios.patch(`${apiBase}/api/v1/ml/experiments/${id}/activate`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchExperiments();
    } catch (err) {
      alert("Error al activar");
    }
  };

  const formatAlgorithm = (alg: string) => {
    switch (alg) {
      case 'linear_regression':
        return 'Regresión Lineal';
      case 'random_forest':
        return 'Random Forest';
      case 'gradient_boosting':
        return 'Gradient Boosting';
      default:
        return alg;
    }
  };

  const formatTarget = (tar: string) => {
    switch (tar) {
      case 'territorial_score':
        return 'Score Territorial (Calculado)';
      case 'education_level':
        return 'Nivel de Educación';
      case 'average_income':
        return 'Ingreso Promedio';
      default:
        return tar;
    }
  };

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-brand" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Análisis Territorial</span>
        </div>

        <nav className="dashboard-nav">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            Dashboard
          </button>

          {role === 'ADMIN' && (
            <>
              <button className="nav-link" onClick={() => navigate('/admin/users')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                Usuarios
              </button>

              <button className="nav-link active">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                Experimentos ML
              </button>

              <button className="nav-link" onClick={() => navigate('/admin/audit')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
                Auditoría
              </button>
            </>
          )}
        </nav>

        <div className="dashboard-user">
          <span className="user-greeting">
            Hola, <strong>{username}</strong>
          </span>
          <span className="user-role-badge">{role}</span>
          <button onClick={logout} className="btn-logout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Salir
          </button>
        </div>
      </header>

      <main className="um-main">
        <div className="um-header-row">
          <h1>Experimentos de Machine Learning</h1>
        </div>

        {error && <div className="um-error">{error}</div>}

        {/* Sección: Formulario Glassmorphism para entrenar modelo */}
        <div className="um-table-wrap" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.1rem', color: '#f1f5f9', marginBottom: '1.25rem', marginTop: 0, fontWeight: 600 }}>
            Entrenar Nuevo Modelo
          </h2>
          <form onSubmit={handleTrain} style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div className="modal-field" style={{ flex: '1 1 240px' }}>
              <label>Transformation Run</label>
              <select value={transformationRunId} onChange={e => setTransformationRunId(e.target.value)} required>
                <option value="">Seleccione un run...</option>
                {runs.map(r => (
                  <option key={r.id} value={r.id}>
                    {r.id} ({new Date(r.started_at).toLocaleDateString()} {new Date(r.started_at).toLocaleTimeString()})
                  </option>
                ))}
              </select>
            </div>

            <div className="modal-field" style={{ flex: '1 1 200px' }}>
              <label>Algoritmo</label>
              <select value={algorithm} onChange={e => setAlgorithm(e.target.value)}>
                <option value="linear_regression">Regresión Lineal</option>
                <option value="random_forest">Random Forest</option>
                <option value="gradient_boosting">Gradient Boosting</option>
              </select>
            </div>

            <div className="modal-field" style={{ flex: '1 1 200px' }}>
              <label>Variable Objetivo</label>
              <select value={targetVariable} onChange={e => setTargetVariable(e.target.value)}>
                <option value="territorial_score">Score Territorial (Calculado)</option>
                <option value="education_level">Nivel de Educación</option>
                <option value="average_income">Ingreso Promedio</option>
              </select>
            </div>

            <button type="submit" className="btn-create" disabled={loading} style={{ height: '39px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {loading ? (
                <>
                  <span className="spinner" style={{ marginRight: '0.4rem', width: '14px', height: '14px' }}></span>
                  Entrenando...
                </>
              ) : (
                'Iniciar Entrenamiento'
              )}
            </button>
          </form>
        </div>

        {/* Sección: Tabla Glassmorphism de experimentos */}
        <div className="um-header-row" style={{ marginBottom: '1rem' }}>
          <h2 style={{ fontSize: '1.25rem', color: '#f1f5f9', margin: 0, fontWeight: 700 }}>
            Historial de Experimentos y Modelos
          </h2>
        </div>

        {loading && experiments.length === 0 ? (
          <div className="um-loading">
            <span className="spinner"></span>
            Cargando historial de experimentos...
          </div>
        ) : (
          <div className="um-table-wrap">
            <table className="um-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Algoritmo</th>
                  <th>Variable Target</th>
                  <th>R2 Score</th>
                  <th>MAE</th>
                  <th>RMSE</th>
                  <th>Estado Modelo</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {experiments.map(exp => {
                  const isActive = exp.trained_models.some(tm => tm.is_active);
                  return (
                    <tr key={exp.id}>
                      <td style={{ fontFamily: 'monospace', color: '#94a3b8' }}>
                        {exp.id.slice(0, 8)}
                      </td>
                      <td>{formatAlgorithm(exp.algorithm)}</td>
                      <td>{formatTarget(exp.target_variable)}</td>
                      <td>
                        {exp.r2_score !== undefined && exp.r2_score !== null ? (
                          <span style={{ fontWeight: 600, color: '#38bdf8' }}>{exp.r2_score.toFixed(4)}</span>
                        ) : (
                          <span style={{ color: '#64748b' }}>-</span>
                        )}
                      </td>
                      <td>
                        {exp.mae !== undefined && exp.mae !== null ? (
                          <span>{exp.mae.toFixed(4)}</span>
                        ) : (
                          <span style={{ color: '#64748b' }}>-</span>
                        )}
                      </td>
                      <td>
                        {exp.rmse !== undefined && exp.rmse !== null ? (
                          <span>{exp.rmse.toFixed(4)}</span>
                        ) : (
                          <span style={{ color: '#64748b' }}>-</span>
                        )}
                      </td>
                      <td>
                        <span className={`status-badge status-${isActive ? 'active' : 'inactive'}`}>
                          {isActive ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        {isActive ? (
                          <span style={{ fontSize: '0.8rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                            En producción
                          </span>
                        ) : (
                          <button className="btn-action btn-role" onClick={() => handleActivate(exp.id)} title="Poner modelo activo">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polygon points="5 3 19 12 5 21 5 3" />
                            </svg>
                            Poner en Producción
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}

                {experiments.length === 0 && (
                  <tr>
                    <td colSpan={8} className="um-empty">
                      No se han entrenado experimentos de Machine Learning aún.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
};

export default MLExperimentsPage;
