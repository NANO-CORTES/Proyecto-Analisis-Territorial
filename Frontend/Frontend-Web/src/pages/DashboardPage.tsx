import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import axios from 'axios';
import '../styles/Dashboard.css';

// ─── Colombia Data ────────────────────────────────────────────────────────────
const DEPARTAMENTOS: Record<string, string[]> = {
  'Antioquia': ['Medellín', 'Bello', 'Itagüí', 'Envigado', 'Rionegro', 'Apartadó', 'Turbo', 'Caucasia'],
  'Valle del Cauca': ['Cali', 'Buenaventura', 'Palmira', 'Tuluá', 'Manizales', 'Buga', 'Cartago'],
  'Cundinamarca': ['Bogotá D.C.', 'Soacha', 'Fusagasugá', 'Facatativá', 'Zipaquirá', 'Chía', 'Madrid'],
  'Atlántico': ['Barranquilla', 'Soledad', 'Malambo', 'Sabanalarga', 'Galapa', 'Puerto Colombia'],
  'Bolívar': ['Cartagena', 'Magangué', 'Turbaco', 'Arjona', 'El Carmen de Bolívar'],
  'Santander': ['Bucaramanga', 'Floridablanca', 'Girón', 'Piedecuesta', 'Barrancabermeja'],
  'Nariño': ['Pasto', 'Tumaco', 'Ipiales', 'Túquerres', 'La Unión'],
  'Córdoba': ['Montería', 'Planeta Rica', 'Sahagún', 'Lorica', 'Cereté'],
  'Tolima': ['Ibagué', 'Espinal', 'Melgar', 'Chaparral', 'Girardot'],
  'Cauca': ['Popayán', 'Santander de Quilichao', 'Puerto Tejada', 'Guapi', 'Miranda'],
  'Huila': ['Neiva', 'Pitalito', 'Garzón', 'La Plata', 'Campoalegre'],
  'Boyacá': ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquirá', 'Paipa'],
  'Magdalena': ['Santa Marta', 'Ciénaga', 'Fundación', 'El Banco', 'Plato'],
  'Cesar': ['Valledupar', 'Aguachica', 'Agustín Codazzi', 'La Jagua de Ibirico'],
  'Meta': ['Villavicencio', 'Acacías', 'Granada', 'Puerto López', 'Restrepo'],
};

// ─── Main Page ────────────────────────────────────────────────────────────────

const DashboardPage: React.FC = () => {
  const { username, role, logout } = useAuth();
  const navigate = useNavigate();

  // File upload state
  const [isUploading, setIsUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [uploadStatus, setUploadStatus] = React.useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [showUploadPanel, setShowUploadPanel] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Territories state
  const [selectedDept, setSelectedDept] = React.useState<string>('');
  const [municipioSearch, setMunicipioSearch] = React.useState('');
  const [selectedMunicipios, setSelectedMunicipios] = React.useState<string[]>([]);

  const handleLogout = () => { logout(); navigate('/'); };

  // ── File upload ────────────────────────────────────────────────────────────
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setUploadProgress(0);
    setUploadStatus(null);

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiBase}/api/v1/ingestion/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setUploadProgress(progress);
        },
      });
      setUploadStatus({ type: 'success', message: `¡Éxito! ${response.data.filename} cargado correctamente.` });
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (error: any) {
      setUploadStatus({ type: 'error', message: 'Error al cargar el archivo. Intenta de nuevo.' });
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // ── Municipios ─────────────────────────────────────────────────────────────
  const currentMunicipios = selectedDept ? DEPARTAMENTOS[selectedDept] ?? [] : [];
  const filteredMunicipios = currentMunicipios.filter(m =>
    m.toLowerCase().includes(municipioSearch.toLowerCase())
  );

  const toggleMunicipio = (m: string) => {
    setSelectedMunicipios(prev =>
      prev.includes(m) ? prev.filter(x => x !== m) : [...prev, m]
    );
  };

  return (
    <div className="dashboard-page">
      {/* ── Header ── */}
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Análisis Territorial</span>
        </div>
        <nav className="dashboard-nav">
          <button className="nav-link active" onClick={() => navigate('/dashboard')}>
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
                Gestión de Usuarios
              </button>
              <button className="nav-link" onClick={() => navigate('/admin/ml-experiments')}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <line x1="3" y1="9" x2="21" y2="9" />
                  <line x1="9" y1="21" x2="9" y2="9" />
                </svg>
                Experimentos ML
              </button>
            </>
          )}
        </nav>
        <div className="dashboard-user">
          <span className="user-greeting">Hola, <strong>{username}</strong></span>
          <span className="user-role-badge">{role}</span>
          <button onClick={handleLogout} className="btn-logout">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Salir
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        {/* ── Welcome ── */}
        <div className="welcome-card">
          <div className="welcome-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1>¡Bienvenido, {username}!</h1>
          <p>Sistema de Análisis Territorial — Selecciona un territorio o inicia un análisis.</p>
        </div>

        {/* ── Top Action Cards ── */}
        <div className="action-cards-grid">

          {/* Card: Territorios */}
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
                id="dept-select"
                className="dept-select"
                value={selectedDept}
                onChange={e => {
                  setSelectedDept(e.target.value);
                  setMunicipioSearch('');
                  setSelectedMunicipios([]);
                }}
              >
                <option value="">Seleccionar...</option>
                {Object.keys(DEPARTAMENTOS).sort().map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Card: Análisis */}
          <button
            id="btn-start-analysis"
            className="action-card action-card-green action-card-btn"
            onClick={() => navigate('/analysis')}
          >
            <div className="action-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <div className="action-card-body">
              <span className="action-card-title">Análisis</span>
              <span className="action-card-subtitle">
                {selectedMunicipios.length > 0
                  ? `${selectedMunicipios.length} municipio(s) seleccionado(s)`
                  : 'Iniciar análisis territorial'}
              </span>
            </div>
            <div className="action-card-arrow">→</div>
          </button>

          {/* Card: Reportes */}
          <div className="action-card action-card-purple">
            <div className="action-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <div className="action-card-body">
              <span className="action-card-title">Reportes</span>
              <span className="action-card-subtitle">--</span>
            </div>
          </div>

        </div>

        {/* ── Municipios Cargados ── */}
        <div className="municipios-section">
          <div className="municipios-header">
            <div className="municipios-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span>Municipios Cargados</span>
              {selectedMunicipios.length > 0 && (
                <span className="municipios-count">{selectedMunicipios.length} seleccionado(s)</span>
              )}
            </div>
            <div className="municipios-search-wrap">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                id="municipio-search"
                type="text"
                className="municipios-search"
                placeholder="Buscar municipio o código..."
                value={municipioSearch}
                onChange={e => setMunicipioSearch(e.target.value)}
                disabled={!selectedDept}
              />
            </div>
          </div>

          <div className="municipios-body">
            {!selectedDept ? (
              <div className="municipios-empty">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                <p>Selecciona un departamento en la tarjeta superior para ver sus municipios cargados.</p>
              </div>
            ) : filteredMunicipios.length === 0 ? (
              <div className="municipios-empty">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <p>No se encontraron municipios con ese criterio.</p>
              </div>
            ) : (
              <div className="municipios-grid">
                {filteredMunicipios.map(m => (
                  <button
                    key={m}
                    className={`municipio-chip ${selectedMunicipios.includes(m) ? 'selected' : ''}`}
                    onClick={() => toggleMunicipio(m)}
                    title={selectedMunicipios.includes(m) ? 'Deseleccionar' : 'Seleccionar'}
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                    {m}
                    {selectedMunicipios.includes(m) && <span className="chip-check">✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {selectedMunicipios.length > 0 && (
            <div className="municipios-footer">
              <span>{selectedMunicipios.length} municipio(s) en {selectedDept} seleccionado(s) para análisis</span>
              <button
                className="btn-run-analysis"
                onClick={() => navigate('/analysis')}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
                Analizar selección
              </button>
            </div>
          )}
        </div>
      </main>

      {/* ── FAB: Upload ── */}
      <div className={`fab-upload-panel ${showUploadPanel ? 'open' : ''}`}>
        <div className="fab-panel-content">
          <div className="fab-panel-header">
            <span>Subir Archivo</span>
            <button className="fab-panel-close" onClick={() => { setShowUploadPanel(false); setUploadStatus(null); }}>✕</button>
          </div>
          <input
            type="file"
            id="file-upload-fab"
            hidden
            onChange={handleFileUpload}
            ref={fileInputRef}
            disabled={isUploading}
            accept=".csv,.json,.xls,.xlsx"
          />
          <label htmlFor="file-upload-fab" className={`upload-box-fab ${isUploading ? 'disabled' : ''}`}>
            <div className="upload-icon-fab">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <span className="upload-text-fab">
              {isUploading ? 'Subiendo...' : 'Haz clic para cargar un archivo'}
            </span>
            <span className="upload-hint-fab">CSV, JSON, XLS</span>
          </label>

          {isUploading && (
            <div className="fab-progress">
              <div className="fab-progress-info">
                <span>Progreso</span><span>{uploadProgress}%</span>
              </div>
              <div className="fab-progress-bar">
                <div className="fab-progress-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
            </div>
          )}

          {uploadStatus && (
            <div className={`fab-upload-msg ${uploadStatus.type}`}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {uploadStatus.type === 'success'
                  ? <polyline points="20 6 9 17 4 12" />
                  : <><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></>}
              </svg>
              {uploadStatus.message}
            </div>
          )}
        </div>
      </div>

      <button
        id="fab-upload-btn"
        className={`fab-btn ${showUploadPanel ? 'fab-active' : ''}`}
        onClick={() => { setShowUploadPanel(p => !p); setUploadStatus(null); }}
        title="Subir archivo"
      >
        {showUploadPanel ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default DashboardPage;