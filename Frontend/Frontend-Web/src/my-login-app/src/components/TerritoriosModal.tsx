import React, { useState, useEffect } from 'react';

const DEPARTAMENTOS_COLOMBIA = [
  { codigo: 'ANT', nombre: 'Antioquia' },
  { codigo: 'ATL', nombre: 'Atlántico' },
  { codigo: 'BOG', nombre: 'Bogotá D.C.' },
  { codigo: 'BOL', nombre: 'Bolívar' },
  { codigo: 'BOY', nombre: 'Boyacá' },
  { codigo: 'CAL', nombre: 'Caldas' },
  { codigo: 'CAQ', nombre: 'Caquetá' },
  { codigo: 'CAS', nombre: 'Casanare' },
  { codigo: 'CAU', nombre: 'Cauca' },
  { codigo: 'CES', nombre: 'Cesar' },
  { codigo: 'CHO', nombre: 'Chocó' },
  { codigo: 'COR', nombre: 'Córdoba' },
  { codigo: 'CUN', nombre: 'Cundinamarca' },
  { codigo: 'GUA', nombre: 'Guainía' },
  { codigo: 'GUV', nombre: 'Guaviare' },
  { codigo: 'HUI', nombre: 'Huila' },
  { codigo: 'LAG', nombre: 'La Guajira' },
  { codigo: 'MAG', nombre: 'Magdalena' },
  { codigo: 'MET', nombre: 'Meta' },
  { codigo: 'NAR', nombre: 'Nariño' },
  { codigo: 'NDS', nombre: 'Norte de Santander' },
  { codigo: 'PUT', nombre: 'Putumayo' },
  { codigo: 'QUI', nombre: 'Quindío' },
  { codigo: 'RIS', nombre: 'Risaralda' },
  { codigo: 'SAP', nombre: 'San Andrés y Providencia' },
  { codigo: 'SAN', nombre: 'Santander' },
  { codigo: 'SUC', nombre: 'Sucre' },
  { codigo: 'TOL', nombre: 'Tolima' },
  { codigo: 'VAC', nombre: 'Valle del Cauca' },
  { codigo: 'VAU', nombre: 'Vaupés' },
  { codigo: 'VIC', nombre: 'Vichada' },
  { codigo: 'ARA', nombre: 'Arauca' },
];

interface TerritoriosModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const TerritoriosModal: React.FC<TerritoriosModalProps> = ({ isOpen, onClose }) => {
  const [nombre, setNombre] = useState('');
  const [departamento, setDepartamento] = useState('');
  const [municipio, setMunicipio] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [submitted, setSubmitted] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const deptosFiltrados = DEPARTAMENTOS_COLOMBIA.filter(d =>
    d.nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setNombre('');
      setDepartamento('');
      setMunicipio('');
      setDescripcion('');
      setBusqueda('');
      onClose();
    }, 1800);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-left">
            <div className="modal-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </div>
            <div>
              <h2 className="modal-title">Nuevo Territorio</h2>
              <p className="modal-subtitle">Registrar un territorio en Colombia</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Cerrar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="modal-form">

          <div className="form-group">
            <label htmlFor="territorio-nombre">Nombre del Territorio</label>
            <input
              id="territorio-nombre"
              type="text"
              placeholder="Ej: Región Andina Norte"
              value={nombre}
              onChange={e => setNombre(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="depto-search">Departamento</label>
            <input
              id="depto-search"
              type="text"
              placeholder="Buscar departamento..."
              value={busqueda}
              onChange={e => {
                setBusqueda(e.target.value);
                setDepartamento('');
              }}
              className="search-input"
            />
            <div className="depto-list">
              {deptosFiltrados.length === 0 ? (
                <div className="depto-empty">Sin resultados</div>
              ) : (
                deptosFiltrados.map(d => (
                  <button
                    type="button"
                    key={d.codigo}
                    className={`depto-item ${departamento === d.codigo ? 'selected' : ''}`}
                    onClick={() => {
                      setDepartamento(d.codigo);
                      setBusqueda(d.nombre);
                    }}
                  >
                    <span className="depto-codigo">{d.codigo}</span>
                    <span className="depto-nombre">{d.nombre}</span>
                    {departamento === d.codigo && (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="depto-check">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="territorio-municipio">Municipio <span className="optional">(opcional)</span></label>
            <input
              id="territorio-municipio"
              type="text"
              placeholder="Ej: Medellín"
              value={municipio}
              onChange={e => setMunicipio(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="territorio-descripcion">Descripción <span className="optional">(opcional)</span></label>
            <textarea
              id="territorio-descripcion"
              placeholder="Descripción del territorio..."
              value={descripcion}
              onChange={e => setDescripcion(e.target.value)}
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-cancel" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className={`btn-submit ${submitted ? 'submitted' : ''}`} disabled={submitted}>
              {submitted ? (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  Guardado
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  Guardar Territorio
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TerritoriosModal;
