import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LoginForm.css';

const RegisterForm: React.FC = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        full_name: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.id]: e.target.value
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return;
        }

        setIsLoading(true);
        try {
            // Predicción del endpoint de registro basado en la estructura del proyecto
            const response = await fetch('http://127.0.0.1:8000/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: formData.email,
                    username: formData.username,
                    full_name: formData.full_name,
                    password: formData.password
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Error en el registro');
            }

            navigate('/'); // Redirigir al login tras registro exitoso
        } catch (err: any) {
            setError(err.message || 'Error de conexión');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form">
            <div className="form-header">
                <div className="logo-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="8.5" cy="7" r="4" />
                        <line x1="20" y1="8" x2="20" y2="14" />
                        <line x1="23" y1="11" x2="17" y2="11" />
                    </svg>
                </div>
                <h2>Crear Cuenta</h2>
                <p className="form-subtitle">Únete a Análisis Territorial</p>
            </div>

            {error && (
                <div className="error-message" role="alert">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                    {error}
                </div>
            )}

            <div className="input-group">
                <label htmlFor="full_name">Nombre Completo</label>
                <input
                    type="text"
                    id="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="Tu nombre completo"
                    required
                />
            </div>

            <div className="input-group">
                <label htmlFor="username">Usuario</label>
                <input
                    type="text"
                    id="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Elige un nombre de usuario"
                    required
                />
            </div>

            <div className="input-group">
                <label htmlFor="email">Email</label>
                <input
                    type="email"
                    id="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="tu@email.com"
                    required
                />
            </div>

            <div className="input-group">
                <label htmlFor="password">Contraseña</label>
                <input
                    type="password"
                    id="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Mínimo 8 caracteres"
                    required
                />
            </div>

            <div className="input-group">
                <label htmlFor="confirmPassword">Confirmar Contraseña</label>
                <input
                    type="password"
                    id="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Repite tu contraseña"
                    required
                />
            </div>

            <button type="submit" className="btn-login" disabled={isLoading}>
                {isLoading ? 'Registrando...' : 'Registrarse'}
            </button>

            <div className="form-footer" style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem' }}>
                ¿Ya tienes cuenta? <Link to="/" style={{ color: '#6366f1', fontWeight: '600' }}>Inicia sesión</Link>
            </div>
        </form>
    );
};

export default RegisterForm;
