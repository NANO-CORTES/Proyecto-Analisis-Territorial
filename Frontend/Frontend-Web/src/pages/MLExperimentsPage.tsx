import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import '../styles/Dashboard.css';

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
  }, [role, navigate]);

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const fetchExperiments = async () => {
    try {
      setLoading(true);
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

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Experimentos ML</span>
        </div>
        <nav className="dashboard-nav">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>
            Dashboard
          </button>
          <button className="nav-link" onClick={() => navigate('/admin/users')}>
            Gestión de Usuarios
          </button>
          <button className="nav-link" onClick={() => navigate('/admin/audit')}>
            Auditoría
          </button>
          <button className="nav-link active" onClick={() => navigate('/admin/ml-experiments')}>
            Experimentos ML
          </button>
        </nav>
        <div className="dashboard-user">
          <span className="user-greeting">Hola, <strong>{username}</strong></span>
          <button onClick={logout} className="btn-logout">Salir</button>
        </div>
      </header>

      <main className="dashboard-main" style={{ padding: '2rem' }}>
        <h2>Entrenar Modelo</h2>
        <form onSubmit={handleTrain} style={{ background: '#fff', padding: '1rem', borderRadius: '8px', marginBottom: '2rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label>Transformation Run: </label>
            <select value={transformationRunId} onChange={e => setTransformationRunId(e.target.value)} required>
              <option value="">Seleccione...</option>
              {runs.map(r => <option key={r.id} value={r.id}>{r.id} ({new Date(r.started_at).toLocaleString()})</option>)}
            </select>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label>Algoritmo: </label>
            <select value={algorithm} onChange={e => setAlgorithm(e.target.value)}>
              <option value="linear_regression">Regresión Lineal</option>
              <option value="random_forest">Random Forest</option>
              <option value="gradient_boosting">Gradient Boosting</option>
            </select>
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label>Variable Objetivo: </label>
            <select value={targetVariable} onChange={e => setTargetVariable(e.target.value)}>
              <option value="territorial_score">Score Territorial (Calculado)</option>
              <option value="education_level">Nivel de Educación</option>
              <option value="average_income">Ingreso Promedio</option>
            </select>
          </div>
          <button type="submit" disabled={loading} style={{ background: '#2196F3', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px' }}>
            {loading ? 'Entrenando...' : 'Iniciar Entrenamiento'}
          </button>
        </form>

        {error && <p style={{ color: 'red' }}>{error}</p>}

        <h2>Historial de Experimentos</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff' }}>
          <thead>
            <tr style={{ background: '#f5f5f5' }}>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>ID</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>Algoritmo</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>Target</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>R2 Score</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>MAE</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>RMSE</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>Activo</th>
              <th style={{ padding: '8px', border: '1px solid #ddd' }}>Acción</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map(exp => {
              const isActive = exp.trained_models.some(tm => tm.is_active);
              return (
                <tr key={exp.id}>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.id.slice(0,8)}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.algorithm}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.target_variable}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.r2_score?.toFixed(4)}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.mae?.toFixed(4)}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd' }}>{exp.rmse?.toFixed(4)}</td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                    {isActive ? '✅' : '❌'}
                  </td>
                  <td style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'center' }}>
                    {!isActive && (
                      <button onClick={() => handleActivate(exp.id)} style={{ padding: '4px 8px', cursor: 'pointer' }}>
                        Activar modelo
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
            {experiments.length === 0 && (
              <tr>
                <td colSpan={8} style={{ padding: '8px', textAlign: 'center', border: '1px solid #ddd' }}>No hay experimentos</td>
              </tr>
            )}
          </tbody>
        </table>
      </main>
    </div>
  );
};

export default MLExperimentsPage;
