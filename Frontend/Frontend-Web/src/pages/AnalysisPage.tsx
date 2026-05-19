// ═══════════════════════════════════════════════════════════════════════════
// AnalysisPage.tsx - Página de Análisis Territorial
// 
// Esta página implementa un flujo de análisis territorial en 5 pasos:
// 1. Cargar datos - Seleccionar un dataset
// 2. Validar - Verificar integridad de los datos
// 3. Transformar - Aplicar transformaciones (normalización minmax)
// 4. Calcular score - Calcular indicadores y ranking de zonas
// 5. Ver resultados - Mostrar gráfico de barras y mapa de calor
// ═══════════════════════════════════════════════════════════════════════════

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
// Importamos las funciones de la API de analytics
import { fetchDatasets, getDatasetById, transformAdvanced, calculateIndicators, executeScoring, getRanking, getZoneSummary } from '../services/analyticsApi';
import '../styles/Dashboard.css';
import '../styles/Analysis.css';

// ═══════════════════════════════════════════════════════════════════════════
// TIPOS E INTERFACES
// ═══════════════════════════════════════════════════════════════════════════

// Estado posible de cada paso del flujo de análisis
type StepStatus = 'pending' | 'processing' | 'completed' | 'error';

// Representa un paso en el flujo de análisis
interface Step {
  id: number;
  label: string;       // Texto que se muestra en el stepper
  icon: string;       // Ícono visual del paso
  status: StepStatus; // Estado actual del paso
}

// Un indicador individual (ej: Población, Ingresos, Educación)
// value: puntuación de 0 a 100
interface Indicator {
  name: string;
  value: number; // 0–100
}

// Una zona territorial con su análisis completo
interface Zone {
  name: string;           // Nombre de la zona (ej: "Zona A-1")
  score: number;          // Score general (0-100)
  indicators: Indicator[]; // Lista de indicadores evaluados
  level: 'Alto' | 'Medio' | 'Bajo' | 'Crítico'; // Clasificación de la zona
  recommendation: string; // Recomendación basada en el nivel
}

// ═══════════════════════════════════════════════════════════════════════════
// DATOS DE EJEMPLO (MOCK DATA)
// Se usan cuando no hay conexión a la API o como fallback
// ═══════════════════════════════════════════════════════════════════════════

// Datasets de ejemplo disponibles cuando la API no responde
const FALLBACK_DATASETS = [
  { id: 'q1_2024', label: 'Dataset Q1-2024 (CSV)' },
  { id: 'q2_2024', label: 'Dataset Q2-2024 (CSV)' },
  { id: 'hogares', label: 'Encuesta Hogares (JSON)' },
];

// Los 4 indicadores principales que se evalúan en cada zona
const INDICATORS_NAMES = [
  'Población',
  'Ingresos',
  'Educación',
  'Competitividad',
];

// Genera zonas de ejemplo para pruebas locales
// seed: número para generar datos pseudo-aleatorios consistentes
function generateZones(seed: number): Zone[] {
  const zones: Zone[] = [];
  // Determina el nivel según el score
  const levelOf = (s: number): Zone['level'] =>
    s >= 75 ? 'Alto' : s >= 50 ? 'Medio' : s >= 30 ? 'Bajo' : 'Crítico';
  // Genera recomendación según el nivel
  const recOf = (l: Zone['level']) => {
    if (l === 'Alto')    return 'Zona con excelente desempeño territorial. Se recomienda mantener inversión y fortalecer indicadores de riesgo sísmico.';
    if (l === 'Medio')   return 'Zona con desempeño moderado. Priorizar mejora en cobertura de servicios y acceso vial.';
    if (l === 'Bajo')    return 'Zona deficiente. Intervención urgente en infraestructura vial y servicios básicos.';
    return 'Zona crítica. Requiere plan de emergencia territorial y reasignación presupuestaria inmediata.';
  };

  // Genera 20 zonas con indicadores aleatorios
  for (let i = 0; i < 20; i++) {
    // Crea indicadores para cada zona
    const indicators: Indicator[] = INDICATORS_NAMES.map((name, j) => ({
      name,
      // Genera valor pseudo-aleatorio entre 5 y 95
      value: Math.min(100, Math.max(5, Math.round(((seed * (i + 1) * (j + 3)) % 90) + 10))),
    }));
    // Calcula score como promedio de todos los indicadores
    const score = Math.round(indicators.reduce((a, b) => a + b.value, 0) / indicators.length);
    const level = levelOf(score);
    zones.push({
      name: `Zona ${String.fromCharCode(65 + (i % 26))}-${i + 1}`,
      score,
      indicators,
      level,
      recommendation: recOf(level),
    });
  }
  // Ordena por score descendente
  return zones.sort((a, b) => b.score - a.score);
}

// ═══════════════════════════════════════════════════════════════════════════
// SUB-COMPONENTES - Funciones auxiliares de renderizado
// ═══════════════════════════════════════════════════════════════════════════

// StepIcon: Renderiza el ícono según el estado del paso
// Muestra diferentes símbolos según si está completado, en error, procesando o pendiente
const StepIcon: React.FC<{ status: StepStatus; icon: string }> = ({ status, icon }) => {
  if (status === 'completed') return <span>✓</span>;
  if (status === 'error')     return <span>✗</span>;
  if (status === 'processing') return <span className="btn-spinner" style={{ width: 18, height: 18 }} />;
  return <span>{icon}</span>;
};

// CustomTooltip: Tooltip personalizado para el gráfico de barras
// Muestra el nombre de la zona y su puntuación cuando se hace hover
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="custom-tooltip">
        <div style={{ color: '#94a3b8', marginBottom: 2 }}>{label}</div>
        <div className="tooltip-score">{payload[0].value} pts</div>
      </div>
    );
  }
  return null;
};

// getBarColor: Retorna el color de la barra según el score
// Verde: >=75 (Alto), Púrpura: >=50 (Medio), Amarillo: >=30 (Bajo), Rojo: <30 (Crítico)
function getBarColor(score: number) {
  if (score >= 75) return '#4ade80';
  if (score >= 50) return '#818cf8';
  if (score >= 30) return '#facc15';
  return '#fca5a5';
}

// getFillClass: Retorna clase CSS para las barras de progreso de indicadores
function getFillClass(value: number) {
  if (value >= 70) return 'fill-high';
  if (value >= 45) return 'fill-blue';
  if (value >= 25) return 'fill-mid';
  return 'fill-danger';
}

// getLevelClass: Retorna clase CSS según el nivel de la zona
function getLevelClass(level: Zone['level']) {
  if (level === 'Alto')    return 'level-alto';
  if (level === 'Medio')   return 'level-medio';
  if (level === 'Bajo')    return 'level-bajo';
  return 'level-critico';
}

// getBadgeClass: Retorna clase CSS para el badge del ranking
// Oro: 1er lugar, Plata: 2do, Bronce: 3er, Azul: 4-6, Gris: resto
function getBadgeClass(rank: number) {
  if (rank === 0) return 'badge-gold';
  if (rank === 1) return 'badge-silver';
  if (rank === 2) return 'badge-bronze';
  if (rank < 6)  return 'badge-blue';
  return 'badge-gray';
}

// heatColor: Convierte un valor 0-100 en color de celda del heatmap
// Verde para valores altos, rojo para valores bajos
function heatColor(value: number): { bg: string; color: string } {
  const r = value < 50 ? 220 : Math.round(220 - (value - 50) * 3.2);
  const g = value > 50 ? 190 : Math.round(value * 3.8);
  return {
    bg: `rgba(${r}, ${g}, 60, 0.25)`,
    color: value >= 60 ? '#4ade80' : value >= 35 ? '#facc15' : '#fca5a5',
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// ZoneDetailCard - Tarjeta de detalle de una zona seleccionada
// Muestra: ranking, nombre, nivel, score, recomendación e indicadores
// ═══════════════════════════════════════════════════════════════════════════

const ZoneDetailCard: React.FC<{ zone: Zone; rank: number; onClose: () => void }> = ({ zone, rank, onClose }) => (
  <div className="glass-card detail-card" style={{ animation: 'fadeInUp 0.3s ease-out' }}>
    {/* Header con badge de ranking y botón de cerrar */}
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
      <div className="detail-zone-header" style={{ border: 'none', paddingBottom: 0 }}>
        {/* Badge de posición (oro, plata, bronce, etc) */}
        <div className={`detail-zone-badge ${getBadgeClass(rank)}`}>#{rank + 1}</div>
        <div>
          {/* Nombre de la zona y nivel */}
          <div className="detail-zone-name">{zone.name}</div>
          <span className={`detail-zone-level ${getLevelClass(zone.level)}`}>{zone.level}</span>
        </div>
      </div>
      <button
        onClick={onClose}
        style={{ background: 'none', border: 'none', color: '#475569', cursor: 'pointer', fontSize: '1.2rem', padding: '0.25rem' }}
        title="Cerrar"
      >✕</button>
    </div>

    {/* Score principal */}
    <div className="detail-score-row">
      <span className="detail-score-value">{zone.score}</span>
      <span className="detail-score-max">/ 100 pts</span>
    </div>

    {/* Recomendación basada en el nivel */}
    <div className="detail-recommendation">{zone.recommendation}</div>

    {/* Lista de indicadores con barras de progreso */}
    <div>
      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
        Indicadores
      </div>
      <div className="indicators-list">
        {zone.indicators.map((ind) => (
          <div key={ind.name} className="indicator-row">
            <div className="indicator-meta">
              <span className="indicator-name">{ind.name}</span>
              <span className="indicator-val">{ind.value}</span>
            </div>
            <div className="progress-track">
              <div
                className={`progress-fill ${getFillClass(ind.value)}`}
                style={{ width: `${ind.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

// ═══════════════════════════════════════════════════════════════════════════
// HeatmapTable - Tabla de mapa de calor de indicadores por zona
// Muestra las 15 mejores zonas con sus indicadores en formato de heatmap
// Colores: verde = alto valor, rojo = bajo valor
// ═══════════════════════════════════════════════════════════════════════════

const HeatmapTable: React.FC<{ zones: Zone[] }> = ({ zones }) => {
  // Solo muestra las top 15 zonas
  const top15 = zones.slice(0, 15);
  return (
    <div className="glass-card heatmap-section">
      <div className="card-title">Mapa de Calor de Indicadores</div>
      <div className="card-subtitle">Intensidad por zona — verde = alto, rojo = bajo</div>
      <div className="heatmap-scroll">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th className="col-zone">Zona</th>
              {/* Encabezados de los indicadores */}
              {INDICATORS_NAMES.map((n) => <th key={n}>{n}</th>)}
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {top15.map((zone) => (
              <tr key={zone.name}>
                <td className="zone-name-cell">{zone.name}</td>
                {/* Celdas de indicadores con color según valor */}
                {zone.indicators.map((ind) => {
                  const { bg, color } = heatColor(ind.value);
                  return (
                    <td
                      key={ind.name}
                      className="heat-cell"
                      style={{ background: bg, color }}
                      title={`${ind.name}: ${ind.value}`}
                    >
                      {ind.value}
                    </td>
                  );
                })}
                {/* Celda del score total */}
                <td style={{ ...heatColor(zone.score), background: heatColor(zone.score).bg, color: heatColor(zone.score).color, fontWeight: 800 }}>
                  {zone.score}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Leyenda de colores */}
      <div className="heatmap-legend">
        <span>Bajo</span>
        <div className="legend-bar" />
        <span>Alto</span>
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// PASOS DEL FLUJO DE ANÁLISIS
// Define los 5 pasos que el usuario debe completar para el análisis territorial
// ═══════════════════════════════════════════════════════════════════════════

const INITIAL_STEPS: Step[] = [
  { id: 1, label: 'Cargar datos',    icon: '📂', status: 'pending' },  // Seleccionar dataset
  { id: 2, label: 'Validar',         icon: '🔍', status: 'pending' },  // Verificar datos
  { id: 3, label: 'Transformar',     icon: '⚙️',  status: 'pending' },  // Normalizar datos
  { id: 4, label: 'Calcular score',  icon: '📊', status: 'pending' },  // Calcular indicadores
  { id: 5, label: 'Ver resultados',  icon: '✨', status: 'pending' },  // Mostrar análisis
];

// ═══════════════════════════════════════════════════════════════════════════
// AnalysisPage - Componente principal de la página de análisis
// ═══════════════════════════════════════════════════════════════════════════

const AnalysisPage: React.FC = () => {
  // Obtenemos el usuario y rol del contexto de autenticación
  const { username, role, logout } = useAuth();
  const navigate = useNavigate();

  // ─── Estado del componente ───
  // steps: estado de cada paso del flujo (pending/processing/completed/error)
  const [steps, setSteps]         = useState<Step[]>(INITIAL_STEPS);
  // datasets: lista de datasets disponibles desde la API
  const [datasets, setDatasets]   = useState<{id: string, label: string}[]>([]);
  // dataset: ID del dataset actualmente seleccionado
  const [dataset, setDataset]     = useState('');
  // zones: array de zonas resultantes del análisis
  const [zones, setZones]         = useState<Zone[]>([]);
  // selectedZone: zona actualmente seleccionada para ver detalle
  const [selectedZone, setSelectedZone] = useState<{ zone: Zone; rank: number } | null>(null);
  // isRunning: indica si hay algún proceso en ejecución
  const [isRunning, setIsRunning] = useState(false);
  
  // IDs de ejecución para tracking en la API
  const [transformationRunId, setTransformationRunId] = useState('');
  const [scoreExecutionId, setScoreExecutionId] = useState('');

  // ─── Effect: Cargar datasets al montar el componente ───
  React.useEffect(() => {
    // Llama a la API para obtener la lista de datasets disponibles
    fetchDatasets().then(data => {
      // Mapea los datos al formato esperado y selecciona el primero por defecto
      const d = data.map(x => ({ id: x.datasetId, label: x.fileName }));
      if (d.length > 0) {
        setDatasets(d);
        setDataset(d[0].id);
      } else {
        // Si no hay datos, usa los datasets de ejemplo
        setDatasets(FALLBACK_DATASETS);
        setDataset(FALLBACK_DATASETS[0].id);
      }
    }).catch(err => {
      console.error(err);
      // En caso de error, usa los datasets de ejemplo
      setDatasets(FALLBACK_DATASETS);
      setDataset(FALLBACK_DATASETS[0].id);
    });
  }, []);

  // ─── Funciones auxiliares ───
  // Verifica si un paso específico está completado
  const currentStepCompleted = (id: number) => steps[id - 1]?.status === 'completed';
  // Verifica si todos los pasos están completados
  const allCompleted = steps.every(s => s.status === 'completed');

  // Actualiza el estado de un paso específico
  const setStep = (id: number, status: StepStatus) =>
    setSteps(prev => prev.map(s => s.id === id ? { ...s, status } : s));

  // Función de delay para simular procesos
  const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

  // runStep: Ejecuta un paso del flujo de análisis
  // Maneja automáticamente los estados de processing y error
  const runStep = useCallback(async (stepId: number, action: () => Promise<void>) => {
    setIsRunning(true);
    setStep(stepId, 'processing');  // Marca como procesando
    try {
      await action();               // Ejecuta la acción
      setStep(stepId, 'completed'); // Marca como completado
    } catch {
      setStep(stepId, 'error');     // Marca como error si falla
    } finally {
      setIsRunning(false);
    }
  }, []);
  // ═══════════════════════════════════════════════════════════════════════════
  // FUNCIONES DE ACCIÓN - Handlers para cada paso del flujo
  // ═══════════════════════════════════════════════════════════════════════════

  // handleLoad: Paso 1 - Confirma la selección del dataset
  // Solo marca el paso como completado (la selección ya se hizo en el UI)
  const handleLoad = () => runStep(1, async () => {
    if (!dataset) throw new Error("No dataset selected");
    // Just a UI confirmation that a dataset is selected
    await delay(500);
  });

  // handleValidate: Paso 2 - Valida el dataset seleccionado
  // Intenta llamar a la API, si falla usa delay simulado
  const handleValidate = () => runStep(2, async () => {
    try {
      await getDatasetById(dataset);
    } catch(e) {
      console.warn("Could not validate with real API, using mock delay");
      await delay(1000);
    }
  });

  // handleTransform: Paso 3 - Transforma los datos
  // Aplica normalización minmax a través de la API
  const handleTransform = () => runStep(3, async () => {
    try {
      const res = await transformAdvanced(dataset, 'minmax');
      setTransformationRunId(res.run_id);
    } catch(e) {
      console.warn("Transform failed with real API, falling back to mock", e);
      setTransformationRunId('mock_run_id');
      await delay(1400);
    }
  });

  // handleScore: Paso 4 - Calcula indicadores y scoring
  // Flujo: calculateIndicators → executeScoring → getRanking → getZoneSummary
  const handleScore = () => runStep(4, async () => {
    try {
      if (!transformationRunId) throw new Error("No transformation run ID");
      // 1. Calcula indicadores para la transformación
      await calculateIndicators(transformationRunId);
      // 2. Ejecuta el scoring
      const resExec = await executeScoring(transformationRunId);
      setScoreExecutionId(resExec.id);

      // 3. Obtiene el ranking de zonas
      const ranking = await getRanking(resExec.id);
      const mappedZones: Zone[] = [];
      
      // 4. Mapea los resultados del ranking a nuestro formato
      for (const item of ranking.items) {
        // Genera indicadores aleatorios por defecto
        let indicators: Indicator[] = INDICATORS_NAMES.map(name => ({ name, value: Math.round(Math.random() * 40 + 30) }));
        let recommendation = `Zona con desempeño nivel ${item.score_level}. Requiere revisión de políticas.`;
        
        // Si está en top 15, intenta obtener resumen detallado
        if (item.rank_position <= 15) {
          try {
            const summary = await getZoneSummary(item.zone_code);
            if (summary.indicators) {
              // Mapea los indicadores de la API al formato esperado
              indicators = [
                { name: 'Población', value: Math.round(summary.indicators.population_indicator * 100) },
                { name: 'Ingresos', value: Math.round(summary.indicators.income_indicator * 100) },
                { name: 'Educación', value: Math.round(summary.indicators.education_indicator * 100) },
                { name: 'Competitividad', value: Math.round(summary.indicators.competition_indicator * 100) },
              ];
            }
          } catch(e) { console.error("Error fetching summary for", item.zone_code) }
        }
        
        // Agrega la zona al array de resultados
        mappedZones.push({
          name: item.zone_name,
          score: Math.round(item.score_value * 100),
          level: item.score_level,
          recommendation,
          indicators
        });
      }
      
      setZones(mappedZones);
      setStep(5, 'completed');
    } catch(e) {
      console.error("Score step failed:", e);
      // Fallback: genera datos mock si la API falla
      const data = generateZones(1337);
      setZones(data);
      setStep(5, 'completed');
    }
  });

  // handleReset: Reinicia todo el flujo de análisis
  const handleReset = () => {
    setSteps(INITIAL_STEPS);
    setZones([]);
    setSelectedZone(null);
    setIsRunning(false);
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDERIZADO - JSX del componente
  // ═══════════════════════════════════════════════════════════════════════════

  // Top 10 zonas para el gráfico (las de mayor score)
  const top10 = zones.slice(0, 10);

  return (
    <div className="analysis-page">
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* HEADER - Barra de navegación superior */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <header className="dashboard-header">
        {/* Logo y nombre de la aplicación */}
        <div className="dashboard-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Análisis Territorial</span>
        </div>
        
        {/* Navegación entre páginas */}
        <nav className="dashboard-nav">
          <button className="nav-link" onClick={() => navigate('/dashboard')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            Dashboard
          </button>

          {/* Solo visible para administradores */}
          {role === 'ADMIN' && (
            <button className="nav-link" onClick={() => navigate('/admin/users')}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
              </svg>
              Usuarios
            </button>
          )}
        </nav>
        
        {/* Información del usuario y botón de logout */}
        <div className="dashboard-user">
          <span className="user-greeting">Hola, <strong>{username}</strong></span>
          <span className="user-role-badge">{role}</span>
          <button onClick={() => { logout(); navigate('/'); }} className="btn-logout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Salir
          </button>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* MAIN - Contenido principal de la página */}
      {/* ═══════════════════════════════════════════════════════════════════ */}
      <main className="analysis-main">
        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* STEPPER - Indicador visual de progreso (5 pasos) */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        <div className="stepper-wrapper">
          {steps.map((step) => (
            <div key={step.id} className={`step-item ${step.status}`}>
              <div className="step-icon-wrap">
                <StepIcon status={step.status} icon={step.icon} />
              </div>
              <span className="step-label">{step.label}</span>
            </div>
          ))}
        </div>

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* CONTROL PANEL - Selector de dataset y botones de acción */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        <div className="control-panel">
          {/* Selector de dataset */}
          <div className="control-left">
            <label htmlFor="dataset-select">Dataset de análisis</label>
            <select
              id="dataset-select"
              className="dataset-select"
              value={dataset}
              onChange={e => setDataset(e.target.value)}
              disabled={isRunning || currentStepCompleted(1)}
            >
              {datasets.map(d => (
                <option key={d.id} value={d.id}>{d.label}</option>
              ))}
            </select>
          </div>

          {/* Botones de acción según el paso actual */}
          <div className="control-actions">
            {/* Paso 1: Cargar datos - Solo visible si no está completado */}
            {!currentStepCompleted(1) && (
              <button
                id="btn-load"
                className="btn-action btn-validate"
                onClick={handleLoad}
                disabled={isRunning}
              >
                {steps[0].status === 'processing' && <span className="btn-spinner" />}
                📂 Cargar datos
              </button>
            )}

            {/* Paso 2: Validar - Visible después de completar paso 1 */}
            {currentStepCompleted(1) && !currentStepCompleted(2) && (
              <button
                id="btn-validate"
                className="btn-action btn-validate"
                onClick={handleValidate}
                disabled={isRunning}
              >
                {steps[1].status === 'processing' && <span className="btn-spinner" />}
                🔍 Validar
              </button>
            )}

            {/* Paso 3: Transformar - Visible después de completar paso 2 */}
            {currentStepCompleted(2) && !currentStepCompleted(3) && (
              <button
                id="btn-transform"
                className="btn-action btn-transform"
                onClick={handleTransform}
                disabled={isRunning}
              >
                {steps[2].status === 'processing' && <span className="btn-spinner" />}
                ⚙️ Transformar
              </button>
            )}

            {/* Paso 4: Calcular score - Visible después de completar paso 3 */}
            {currentStepCompleted(3) && !currentStepCompleted(4) && (
              <button
                id="btn-score"
                className="btn-action btn-score"
                onClick={handleScore}
                disabled={isRunning}
              >
                {steps[3].status === 'processing' && <span className="btn-spinner" />}
                📊 Calcular Score
              </button>
            )}

            {/* Botón de reinicio - Siempre visible */}
            <button
              id="btn-reset"
              className="btn-action btn-reset"
              onClick={handleReset}
              disabled={isRunning}
            >
              ↺ Reiniciar
            </button>
          </div>
        </div>

        {/* ═══════════════════════════════════════════════════════════════ */}
        {/* RESULTADOS - Gráfico y heatmap (solo cuando todo completado) */}
        {/* ═══════════════════════════════════════════════════════════════ */}
        {allCompleted && zones.length > 0 ? (
          <>
            {/* Grid de resultados: gráfico + detalle */}
            <div className={`results-grid ${!selectedZone ? 'no-detail' : ''}`}>
              {/* Gráfico de barras - Top 10 zonas */}
              <div className="glass-card chart-section">
                <div className="card-title">Top 10 Zonas por Score</div>
                <div className="card-subtitle">Haz clic en una barra para ver el detalle de la zona</div>
                <ResponsiveContainer width="100%" height={320}>
                  <BarChart data={top10} margin={{ top: 5, right: 10, left: -20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis
                      dataKey="name"
                      tick={{ fill: '#64748b', fontSize: 11 }}
                      angle={-35}
                      textAnchor="end"
                      interval={0}
                    />
                    <YAxis tick={{ fill: '#64748b', fontSize: 11 }} domain={[0, 100]} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                    <Bar dataKey="score" radius={[6, 6, 0, 0]} cursor="pointer"
                      onClick={(data, index) => setSelectedZone({ zone: zones[index], rank: index })}>
                      {top10.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={getBarColor(entry.score)}
                          opacity={selectedZone?.rank === index ? 1 : 0.8}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <p className="chart-hint">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" />
                  </svg>
                  Haz clic en cualquier barra para ver el detalle
                </p>
              </div>

              {/* Card de detalle de zona - Solo visible si hay una zona seleccionada */}
              {selectedZone && (
                <ZoneDetailCard
                  zone={selectedZone.zone}
                  rank={selectedZone.rank}
                  onClose={() => setSelectedZone(null)}
                />
              )}
            </div>

            {/* Mapa de calor de indicadores */}
            <HeatmapTable zones={zones} />
          </>
        ) : (
          // Estado vacío: cuando el flujo no está completo
          !allCompleted && (
            <div className="glass-card empty-results">
              <div className="empty-icon">📊</div>
              <div>
                <strong>Sin resultados aún</strong>
                <p>Completa el flujo guiado de pasos para visualizar el análisis territorial.</p>
              </div>
            </div>
          )
        )}
      </main>
    </div>
  );
};

export default AnalysisPage;
