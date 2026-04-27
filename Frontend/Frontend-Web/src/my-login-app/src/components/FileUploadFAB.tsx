import React, { useRef, useState } from 'react';
import { useAuth } from './AuthProvider';

const FileUploadFAB: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; msg: string } | null>(null);
  const { token } = useAuth();

  const showToast = (type: 'success' | 'error', msg: string) => {
    setToast({ type, msg });
    setTimeout(() => setToast(null), 5000);
  };

  const handleFabClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
      showToast('error', 'Por favor selecciona un archivo .csv o .json válido.');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/ingestion/datasets/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        showToast('success', `✓ Archivo "${file.name}" subido correctamente.`);
      } else {
        let errorMsg = `Error ${response.status}`;
        try {
          const errData = await response.json();
          // FastAPI puede devolver detail como string o como array de errores
          if (typeof errData.detail === 'string') {
            errorMsg = errData.detail;
          } else if (Array.isArray(errData.detail)) {
            errorMsg = errData.detail.map((e: any) => e.msg).join('. ');
          } else {
            errorMsg = response.statusText || errorMsg;
          }
        } catch {
          errorMsg = response.statusText || errorMsg;
        }
        showToast('error', errorMsg);
      }
    } catch (err) {
      showToast('error', 'Ups, tenemos problemas de comunicación con el servicio de análisis. Por favor, reintenta en unos momentos.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <>
      <input
        type="file"
        accept=".csv,.json"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />

      {/* Toast de notificación */}
      {toast && (
        <div style={{
          position: 'fixed',
          bottom: '5.5rem',
          right: '2rem',
          maxWidth: '360px',
          background: toast.type === 'success' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
          border: `1px solid ${toast.type === 'success' ? 'rgba(34,197,94,0.35)' : 'rgba(239,68,68,0.35)'}`,
          borderRadius: '12px',
          padding: '0.75rem 1rem',
          color: toast.type === 'success' ? '#4ade80' : '#fca5a5',
          fontSize: '0.8375rem',
          lineHeight: '1.5',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          zIndex: 1100,
          animation: 'fadeInUp 0.25s ease-out',
        }}>
          {toast.msg}
          {toast.type === 'error' && (
            <div style={{ marginTop: '0.5rem', color: '#94a3b8', fontSize: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.4rem' }}>
              El CSV debe tener columnas: <strong style={{ color: '#cbd5e1' }}>zone_code</strong>, <strong style={{ color: '#cbd5e1' }}>zone_name</strong>, <strong style={{ color: '#cbd5e1' }}>departamento</strong> y al menos <strong style={{ color: '#cbd5e1' }}>3 columnas numéricas</strong>.
            </div>
          )}
        </div>
      )}

      {/* FAB button */}
      <button
        className="fab-upload"
        onClick={handleFabClick}
        disabled={isUploading}
        title="Subir Dataset (.csv, .json)"
        style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: isUploading
            ? 'rgba(99,102,241,0.5)'
            : 'linear-gradient(135deg, #6366f1, #818cf8)',
          color: 'white',
          border: 'none',
          boxShadow: '0 4px 20px rgba(99,102,241,0.45)',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'transform 0.2s, opacity 0.2s',
          zIndex: 1000,
          opacity: isUploading ? 0.7 : 1,
        }}
        onMouseOver={(e) => { if (!isUploading) e.currentTarget.style.transform = 'scale(1.08)'; }}
        onMouseOut={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
      >
        {isUploading ? (
          <span className="spinner" style={{ width: '24px', height: '24px', borderWidth: '3px' }}></span>
        ) : (
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        )}
      </button>
    </>
  );
};

export default FileUploadFAB;
