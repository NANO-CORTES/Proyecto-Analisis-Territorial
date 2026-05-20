import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import axios from 'axios';
import { downloadLatestReport } from '../services/bffApi';
import '../styles/Dashboard.css';

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

type ReportFormat = 'csv' | 'json' | 'xls';

const DashboardPage: React.FC = () => {
  const { username, role, logout } = useAuth();
  const navigate = useNavigate();

  const [isUploading, setIsUploading] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const [uploadStatus, setUploadStatus] = React.useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [showUploadPanel, setShowUploadPanel] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const [selectedDept, setSelectedDept] = React.useState<string>('');
  const [municipioSearch, setMunicipioSearch] = React.useState('');
  const [selectedMunicipios, setSelectedMunicipios] = React.useState<string[]>([]);

  const [downloadModalOpen, setDownloadModalOpen] = React.useState(false);
  const [downloadError, setDownloadError] = React.useState('');
  const [downloadSuccess, setDownloadSuccess] = React.useState('');
  const [downloading, setDownloading] = React.useState(false);

  const [showReportsModal, setShowReportsModal] = React.useState(false);

  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

  const handleLogout = () => { logout(); navigate('/'); };

  const buildCsv = (zones: any[]): string => {
    const header = 'rank,zone_code,zone_name,score,level,poblacion,ingresos,educacion,competitividad,recomendacion';
    const lines = zones.map((z: any, i: number) => {
      const inds: Record<string, number> = {};
      (z.indicators || []).forEach((ind: any) => { inds[ind.name?.toLowerCase()] = ind.value; });
      const rec = (z.recommendation || '').replace(/[\r\n,]+/g, ' ').replace(/"/g, '""');
      return [
        i + 1,
        z.zone_code ?? '',
        z.name ?? '',
        z.score ?? '',
        z.level ?? '',
        inds.poblacion ?? '',
        inds.ingresos ?? '',
        inds.educacion ?? '',
        inds.competitividad ?? '',
        `"${rec}"`,
      ].join(',');
    });
    return [header, ...lines].join('\n');
  };

  const buildXls = (zones: any[]): string => {
    const rows = zones.map((z: any, i: number) => {
      const inds: Record<string, number> = {};
      (z.indicators || []).forEach((ind: any) => { inds[ind.name?.toLowerCase()] = ind.value; });
      return `<Row>
        <Cell><Data ss:Type="Number">${i + 1}</Data></Cell>
        <Cell><Data ss:Type="String">${z.zone_code ?? ''}</Data></Cell>
        <Cell><Data ss:Type="String">${z.name ?? ''}</Data></Cell>
        <Cell><Data ss:Type="Number">${z.score ?? 0}</Data></Cell>
        <Cell><Data ss:Type="String">${z.level ?? ''}</Data></Cell>
        <Cell><Data ss:Type="Number">${inds.poblacion ?? 0}</Data></Cell>
        <Cell><Data ss:Type="Number">${inds.ingresos ?? 0}</Data></Cell>
        <Cell><Data ss:Type="Number">${inds.educacion ?? 0}</Data></Cell>
        <Cell><Data ss:Type="Number">${inds.competitividad ?? 0}</Data></Cell>
      </Row>`;
    }).join('\n');
    return `<?xml version="1.0"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Worksheet ss:Name="Ranking">
<Table>
<Row>
  <Cell><Data ss:Type="String">rank</Data></Cell>
  <Cell><Data ss:Type="String">zone_code</Data></Cell>
  <Cell><Data ss:Type="String">zone_name</Data></Cell>
  <Cell><Data ss:Type="String">score</Data></Cell>
  <Cell><Data ss:Type="String">level</Data></Cell>
  <Cell><Data ss:Type="String">poblacion</Data></Cell>
  <Cell><Data ss:Type="String">ingresos</Data></Cell>
  <Cell><Data ss:Type="String">educacion</Data></Cell>
  <Cell><Data ss:Type="String">competitividad</Data></Cell>
</Row>
${rows}
</Table>
</Worksheet>
</Workbook>`;
  };

  const handleDownloadReport = async (format: ReportFormat) => {
    setDownloadError('');
    try {
      const blob = await downloadLatestReport(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `reporte_territorial.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setDownloadSuccess(`Reporte descargado correctamente en formato ${format.toUpperCase()}`);
      setTimeout(() => {
          setDownloadSuccess('');
          setDownloadModalOpen(false);
      }, 3000);
    } catch (err: any) {
      setDownloadError(err.message || 'Error al descargar el reporte.');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setIsUploading(true);
    setUploadProgress(0);
    setUploadStatus(null);
    try {
      const response = await axios.post(`${apiBase}/api/v1/ingestion/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setUploadProgress(progress);
        },
      });
      setUploadStatus({ type: 'success', message: `Exito: ${response.data.filename || file.name} cargado correctamente.` });
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch {
      setUploadStatus({ type: 'error', message: 'Error al cargar el archivo. Intenta de nuevo.' });
    } finally {
      setIsUploading(false);
    }
  };

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
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <span>Analisis Territorial</span>
        </div>
        <nav className="dashboard-nav">
          <button className="nav-link active" onClick={() => navigate('/dashboard')}>Dashboard</button>
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
          <button onClick={handleLogout} className="btn-logout">Salir</button>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="welcome-card">
          <div className="welcome-icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1>Bienvenido, {username}</h1>
          <p>Sistema de Analisis Territorial. Selecciona un territorio o inicia un analisis.</p>
        </div>

        <div className="action-cards-grid">
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

          <button
            className="action-card action-card-green action-card-btn"
            onClick={() => navigate('/analysis')}
          >
            <div className="action-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </div>
            <div className="action-card-body">
              <span className="action-card-title">Analisis</span>
              <span className="action-card-subtitle">
                {selectedMunicipios.length > 0
                  ? `${selectedMunicipios.length} municipio(s) seleccionado(s)`
                  : 'Iniciar analisis territorial'}
              </span>
            </div>
            <div className="action-card-arrow">{'->'}</div>
          </button>

          <button
            type="button"
            className="action-card action-card-purple action-card-btn"
            onClick={() => setShowReportsModal(true)}
          >
            <div className="action-card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
            </div>
            <div className="action-card-body">
              <span className="action-card-title">Reportes</span>
              <span className="action-card-subtitle">Descargar ultimo analisis</span>
            </div>
            <div className="action-card-arrow">{'->'}</div>
          </button>
        </div>

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
                    className={`municipio-chip ${selectedMunicipios.includes(m) ? 'selected' : ''}`}
                    onClick={() => toggleMunicipio(m)}
                  >
                    {m}
                    {selectedMunicipios.includes(m) && <span className="chip-check"> v</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {selectedMunicipios.length > 0 && (
            <div className="municipios-footer">
              <span>{selectedMunicipios.length} municipio(s) en {selectedDept} seleccionado(s)</span>
              <button className="btn-run-analysis" onClick={() => navigate('/analysis')}>
                Analizar seleccion
              </button>
            </div>
          )}
        </div>
      </main>

      <div className={`fab-upload-panel ${showUploadPanel ? 'open' : ''}`}>
        <div className="fab-panel-content">
          <div className="fab-panel-header">
            <span>Subir Archivo</span>
            <button className="fab-panel-close" onClick={() => { setShowUploadPanel(false); setUploadStatus(null); }}>x</button>
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
            <span className="upload-text-fab">
              {isUploading ? 'Subiendo...' : 'Haz clic para cargar un archivo'}
            </span>
            <span className="upload-hint-fab">CSV, JSON, XLS</span>
          </label>
          {isUploading && (
            <div className="fab-progress">
              <div className="fab-progress-info"><span>Progreso</span><span>{uploadProgress}%</span></div>
              <div className="fab-progress-bar">
                <div className="fab-progress-fill" style={{ width: `${uploadProgress}%` }} />
              </div>
            </div>
          )}
          {downloadError && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '10px', color: '#ef4444' }}>
            {downloadError}
          </div>
        )}
        {downloadSuccess && (
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(74, 222, 128, 0.1)', border: '1px solid #4ade80', borderRadius: '10px', color: '#4ade80' }}>
            {downloadSuccess}
          </div>
        )}
          {uploadStatus && (
            <div className={`fab-upload-msg ${uploadStatus.type}`}>
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
        {showUploadPanel ? 'x' : '+'}
      </button>

      {showReportsModal && (
        <div className="rm-backdrop" onClick={() => setShowReportsModal(false)}>
          <div className="rm-modal" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="rm-header">
              <div className="rm-header-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
              </div>
              <div>
                <h3 className="rm-title">Descargar Último Análisis</h3>
                <p className="rm-subtitle">Selecciona el formato de exportación</p>
              </div>
              <button className="rm-close" onClick={() => setShowReportsModal(false)} aria-label="Cerrar">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            {/* Description */}
            <p className="rm-description">
              Se exportará el último análisis ejecutado, incluyendo ranking de zonas, scores de competitividad, indicadores socioeconómicos y recomendaciones.
            </p>

            {/* Error / Success */}
            {downloadError && (
              <div className="rm-alert rm-alert-error">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                {downloadError}
              </div>
            )}
            {downloadSuccess && (
              <div className="rm-alert rm-alert-success">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                {downloadSuccess}
              </div>
            )}

            {/* Format Buttons */}
            <div className="rm-formats">
              <button type="button" className="rm-format-btn rm-format-csv" onClick={() => handleDownloadReport('csv')}>
                <div className="rm-format-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                </div>
                <div className="rm-format-info">
                  <span className="rm-format-name">CSV</span>
                  <span className="rm-format-desc">Hoja de cálculo</span>
                </div>
                <svg className="rm-format-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>

              <button type="button" className="rm-format-btn rm-format-json" onClick={() => handleDownloadReport('json')}>
                <div className="rm-format-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="16 18 22 12 16 6"/>
                    <polyline points="8 6 2 12 8 18"/>
                  </svg>
                </div>
                <div className="rm-format-info">
                  <span className="rm-format-name">JSON</span>
                  <span className="rm-format-desc">Datos estructurados</span>
                </div>
                <svg className="rm-format-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>

              <button type="button" className="rm-format-btn rm-format-xls" onClick={() => handleDownloadReport('xls')}>
                <div className="rm-format-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="3" y1="15" x2="21" y2="15"/>
                    <line x1="9" y1="3" x2="9" y2="21"/>
                    <line x1="15" y1="3" x2="15" y2="21"/>
                  </svg>
                </div>
                <div className="rm-format-info">
                  <span className="rm-format-name">XLS</span>
                  <span className="rm-format-desc">Excel compatible</span>
                </div>
                <svg className="rm-format-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>
            </div>

            <button type="button" className="rm-cancel" onClick={() => setShowReportsModal(false)}>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
