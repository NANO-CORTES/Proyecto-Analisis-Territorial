import React, { useState } from 'react';

interface CreateUserModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCreated: () => void;
    onCreate: (data: { email: string; full_name: string; password: string; role: string }) => Promise<any>;
}

const CreateUserModal: React.FC<CreateUserModalProps> = ({ isOpen, onClose, onCreated, onCreate }) => {
    const [email, setEmail] = useState('');
    const [fullName, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('USER');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!email.trim() || !fullName.trim() || !password) {
            setError('Todos los campos son obligatorios');
            return;
        }
        if (password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return;
        }

        setLoading(true);
        try {
            await onCreate({ email: email.trim(), full_name: fullName.trim(), password, role });
            setEmail('');
            setFullName('');
            setPassword('');
            setRole('USER');
            onCreated();
            onClose();
        } catch (err: any) {
            setError(err.message || 'Error al crear usuario');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Nuevo Usuario</h3>
                    <button className="modal-close" onClick={onClose}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                {error && <div className="modal-error">{error}</div>}

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="modal-field">
                        <label htmlFor="modal-name">Nombre completo</label>
                        <input
                            id="modal-name"
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Nombre del usuario"
                            disabled={loading}
                        />
                    </div>

                    <div className="modal-field">
                        <label htmlFor="modal-email">Email</label>
                        <input
                            id="modal-email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="correo@ejemplo.com"
                            disabled={loading}
                        />
                    </div>

                    <div className="modal-field">
                        <label htmlFor="modal-password">Contraseña temporal</label>
                        <input
                            id="modal-password"
                            type="text"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Mínimo 6 caracteres"
                            disabled={loading}
                        />
                    </div>

                    <div className="modal-field">
                        <label htmlFor="modal-role">Rol</label>
                        <select
                            id="modal-role"
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            disabled={loading}
                        >
                            <option value="USER">USER</option>
                            <option value="ADMIN">ADMIN</option>
                        </select>
                    </div>

                    <div className="modal-actions">
                        <button type="button" className="btn-cancel" onClick={onClose} disabled={loading}>
                            Cancelar
                        </button>
                        <button type="submit" className="btn-create" disabled={loading}>
                            {loading ? 'Creando...' : 'Crear Usuario'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateUserModal;
