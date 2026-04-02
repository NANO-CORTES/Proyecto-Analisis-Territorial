import os

base_dir = r"c:\Users\User\Downloads\Proyecto-Analisis-Territorial-main"
fe_dir = os.path.join(base_dir, "Frontend", "Territorial-Web")

files = {
    "Dockerfile": """FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173
# Expose port and configure nginx
RUN rm /etc/nginx/conf.d/default.conf
RUN echo "server { listen 5173; location / { root /usr/share/nginx/html; index index.html index.htm; try_files \$uri \$uri/ /index.html; } }" > /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]""",

    "src/index.css": """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #4F46E5;
  --primary-hover: #4338CA;
  --secondary: #10B981;
  --bg-color: #F8FAFC;
  --text-main: #1E293B;
  --text-muted: #64748B;
  --card-bg: rgba(255, 255, 255, 0.9);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-main);
  line-height: 1.5;
}

/* Glassmorphism utility */
.glass {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.auth-container {
  display: flex;
  height: 100vh;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #E0E7FF 0%, #FAFAFA 100%);
}

.login-card {
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.login-card h1 {
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary);
}

.login-card p {
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-main);
}

.input-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
}

.btn-primary {
  width: 100%;
  padding: 0.875rem;
  background-color: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:active {
  transform: scale(0.98);
}

.error-msg {
  color: #EF4444;
  font-size: 0.875rem;
  background: #FEE2E2;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.dashboard {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #E2E8F0;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}""",

    "src/App.tsx": """import { useState, FormEvent, useEffect } from 'react';
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

export default App;"""
}

# Ensure frontend dir exists before creating files in it
os.makedirs(fe_dir, exist_ok=True)

for filepath, content in files.items():
    full_path = os.path.join(fe_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Frontend configuration generated.")
