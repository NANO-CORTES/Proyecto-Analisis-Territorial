import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LoginForm.css'; // Reusing the same styles as LoginForm

const RegisterForm: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !email.trim() || !password) {
      setError('Por favor llena todos los campos');
      return;
    }

    if (password.length > 72) {
      setError('La contraseña no puede exceder 72 caracteres.');
      return;
    }

    setIsLoading(true);
    try {
      // Si el email termina en @admin.com, es ADMIN
      const role = email.trim().toLowerCase().endsWith('@admin.com') ? 'ADMIN' : 'USER';
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), email: email.trim(), password, role }),
      });

      if (!response.ok) {
        try {
          const data = await response.json();
          if (data.detail) {
            setError(typeof data.detail === 'string' ? data.detail : 'Error al registrar.');
          } else if (data.message) {
            setError(data.message);
          } else if (response.status === 400) {
            setError('El nombre de usuario ya está en uso. Elige otro.');
          } else if (response.status === 422) {
            setError('Datos inválidos. Revisa los campos e intenta de nuevo.');
          } else {
            setError('Error al registrar. Intenta de nuevo más tarde.');
          }
        } catch {
          setError('Error al registrar. Intenta con otro usuario.');
        }
      } else {
        navigate('/'); // Volver al login tras registro exitoso
      }
    } catch {
      setError('Error de conexión. Verifica que el servidor esté activo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form" autoComplete="off">
      <div className="form-header">
        <div className="logo-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <line x1="19" y1="8" x2="19" y2="14" />
            <line x1="22" y1="11" x2="16" y2="11" />
          </svg>
        </div>
        <h2>Registro</h2>
        <p className="form-subtitle">Crear nueva cuenta</p>
      </div>

      {error && (
        <div className="error-message" role="alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
          {error}
        </div>
      )}

      <div className="input-group">
        <label htmlFor="reg-username">Usuario</label>
        <div className="input-wrapper">
          <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <input
            type="text"
            id="reg-username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Ingresa tu usuario"
            disabled={isLoading}
            autoFocus
          />
        </div>
      </div>

      <div className="input-group">
        <label htmlFor="reg-email">Correo Electrónico</label>
        <div className="input-wrapper">
          <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
          <input
            type="email"
            id="reg-email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Ej. juan@admin.com"
            disabled={isLoading}
          />
        </div>
      </div>

      <div className="input-group">
        <label htmlFor="reg-password">Contraseña</label>
        <div className="input-wrapper">
          <svg className="input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <input
            type={showPassword ? 'text' : 'password'}
            id="reg-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Ingresa tu contraseña"
            disabled={isLoading}
          />
          <button
            type="button"
            className="toggle-password"
            onClick={() => setShowPassword(!showPassword)}
            tabIndex={-1}
            aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showPassword ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
      </div>

      <button type="submit" className="btn-login" disabled={isLoading}>
        {isLoading ? (
          <>
            <span className="spinner"></span>
            Registrando...
          </>
        ) : (
          'Registrarse'
        )}
      </button>

      <div style={{ marginTop: '1rem', textAlign: 'center' }}>
        <Link to="/" style={{ color: 'var(--primary-color)', fontSize: '0.9rem', textDecoration: 'none' }}>
          ¿Ya tienes cuenta? Inicia sesión
        </Link>
      </div>
    </form>
  );
};

export default RegisterForm;
