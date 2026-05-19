import React, { useState, useEffect } from 'react';
import { externalDataService } from '../services/externalDataApi';
import '../styles/TerritorialDataCard.css';

interface TerritorialDataCardProps {
  department?: string;
  municipality?: string;
}

interface IndicatorData {
  variable: string;
  found: boolean;
  sources: {
    datos_gov: any[];
    bogota: any[];
  };
  loading?: boolean;
  error?: string;
}

const TerritorialDataCard: React.FC<TerritorialDataCardProps> = ({ 
  department = '', 
  municipality = '' 
}) => {
  const [indicators, setIndicators] = useState<{
    population?: IndicatorData;
    income?: IndicatorData;
    education?: IndicatorData;
    competition?: IndicatorData;
  }>({});
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVariable, setSelectedVariable] = useState<'population' | 'income' | 'education' | 'competition'>('population');

  useEffect(() => {
    if (!department || !municipality) {
      setIndicators({});
      return;
    }

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await externalDataService.getMunicipalityIndicators(
          department,
          municipality
        );

        if (result.success) {
          const ind = result.data.indicators;
          setIndicators({
            population: ind.population,
            income: ind.income,
            education: ind.education,
            competition: ind.competition
          });
        } else {
          setError('No se pudieron cargar los indicadores');
        }
      } catch (err) {
        console.error('Error fetching indicators:', err);
        setError('Error al conectar con los datos externos');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [department, municipality]);

  if (!department || !municipality) {
    return (
      <div className="territorial-data-card empty">
        <div className="card-placeholder">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          <p>Selecciona un departamento y municipio para ver los datos territoriales</p>
        </div>
      </div>
    );
  }

  const variableLabels = {
    population: '👥 Población',
    income: '💰 Ingreso',
    education: '🎓 Educación',
    competition: '📊 Competencia'
  };

  const currentData = indicators[selectedVariable];

  return (
    <div className="territorial-data-card">
      <div className="card-header">
        <h3>Datos Territoriales - {selectedVariable === 'population' ? 'Población' : selectedVariable === 'income' ? 'Ingresos' : selectedVariable === 'education' ? 'Educación' : 'Competencia'}</h3>
        <span className="location-badge">
          {department} - {municipality}
        </span>
      </div>

      {/* Variable Selector */}
      <div className="variable-selector">
        {(Object.keys(variableLabels) as Array<'population' | 'income' | 'education' | 'competition'>).map((variable) => (
          <button
            key={variable}
            className={`var-button ${selectedVariable === variable ? 'active' : ''}`}
            onClick={() => setSelectedVariable(variable)}
            disabled={loading}
          >
            {variableLabels[variable]}
          </button>
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Cargando datos...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-state">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <p>{error}</p>
        </div>
      )}

      {/* Data Display */}
      {!loading && currentData && (
        <div className="data-content">
          {currentData.found ? (
            <div>
              <div className="data-sources">
                {/* Datos.gov.co */}
                {currentData.sources?.datos_gov && currentData.sources.datos_gov.length > 0 && (
                  <div className="source-section">
                    <div className="source-header">
                      <h4>📊 Datos.gov.co</h4>
                      <span className="badge">{currentData.sources.datos_gov.length} dataset(s)</span>
                    </div>
                    <div className="datasets-list">
                      {currentData.sources.datos_gov.map((dataset, idx) => (
                        <div key={idx} className="dataset-item">
                          <div className="dataset-title">{dataset.title || dataset.name}</div>
                          <div className="dataset-org">{dataset.organization}</div>
                          {dataset.notes && <p className="dataset-notes">{dataset.notes}</p>}
                          {dataset.resources && dataset.resources.length > 0 && (
                            <div className="resources">
                              <small>📦 {dataset.resources.length} recurso(s)</small>
                              <ul>
                                {dataset.resources.slice(0, 2).map((res: any, ridx: number) => (
                                  <li key={ridx}>
                                    {res.name} <span className="format-badge">{res.format}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Datos Abiertos Bogotá */}
                {currentData.sources?.bogota && currentData.sources.bogota.length > 0 && (
                  <div className="source-section">
                    <div className="source-header">
                      <h4>🏛️ Datos Abiertos Bogotá</h4>
                      <span className="badge">{currentData.sources.bogota.length} dataset(s)</span>
                    </div>
                    <div className="datasets-list">
                      {currentData.sources.bogota.map((dataset, idx) => (
                        <div key={idx} className="dataset-item">
                          <div className="dataset-title">{dataset.title || dataset.name}</div>
                          <div className="dataset-org">{dataset.organization}</div>
                          {dataset.notes && <p className="dataset-notes">{dataset.notes}</p>}
                          {dataset.resources && dataset.resources.length > 0 && (
                            <div className="resources">
                              <small>📦 {dataset.resources.length} recurso(s)</small>
                              <ul>
                                {dataset.resources.slice(0, 2).map((res: any, ridx: number) => (
                                  <li key={ridx}>
                                    {res.name} <span className="format-badge">{res.format}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-data-state">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <p>No se encontraron datos para esta variable en {department}, {municipality}</p>
            </div>
          )}
        </div>
      )}

      {/* Info Footer */}
      <div className="card-footer">
        <small>📌 Datos obtenidos de: datos.gov.co y datosabiertos.bogota.gov.co</small>
      </div>
    </div>
  );
};

export default TerritorialDataCard;
