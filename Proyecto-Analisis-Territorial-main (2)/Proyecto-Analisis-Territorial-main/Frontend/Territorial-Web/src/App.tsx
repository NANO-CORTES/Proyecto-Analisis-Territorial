import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import './index.css';

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if token exists on mount
    const savedToken = localStorage.getItem('access_token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Por favor completa todos los campos.');
      return;
    }

    setLoading(true);
    
    try {
      // Create FormData as expected by OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append('username', email); // email maps to username in OAuth2
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });

      if (!response.ok) {
        throw new Error('Credenciales inválidas');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
      
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
  };

  // Render Dashboard securely if token is present
  if (token) {
    return (
      <div className="dashboard">
        <div className="header glass">
          <h2>Plataforma de Analítica Territorial</h2>
          <button className="btn-primary" style={{ width: 'auto', background: '#EF4444' }} onClick={handleLogout}>
            Cerrar Sesión
          </button>
        </div>
        <div className="glass" style={{ padding: '2rem' }}>
          <h3>Bienvenido al Dashboard (Sprint 1)</h3>
          <p>Has iniciado sesión correctamente. Tu token JWT ha sido almacenado localmente y la sesión es segura.</p>
          <div style={{ marginTop: '2rem' }}>
            <p><strong>Token Payload Guardado:</strong></p>
            <code style={{ background: '#F1F5F9', padding: '1rem', display: 'block', borderRadius: '8px', wordBreak: 'break-all' }}>
              {token}
            </code>
          </div>
        </div>
      </div>
    );
  }

  // Render Login Form
  return (
    <div className="auth-container">
      <div className="login-card glass">
        <h1>Iniciar Sesión</h1>
        <p>Plataforma de Analítica Territorial</p>
        
        {error && <div className="error-msg">{error}</div>}
        
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label htmlFor="email">Usuario / Correo</label>
            <input 
              type="text" 
              id="email" 
              placeholder="admin@territorial.co" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Contraseña</label>
            <input 
              type="password" 
              id="password" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Verificando...' : 'Ingresar'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;