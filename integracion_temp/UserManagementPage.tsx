import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../components/AuthProvider';
import CreateUserModal from '../components/CreateUserModal';
import { fetchUsers, createUser, updateUser, deleteUser, resetPassword, UserData } from '../services/adminApi';
import '../styles/UserManagement.css';
import '../styles/Dashboard.css';

const UserManagementPage: React.FC = () => {
    const { username, role, logout } = useAuth();
    const navigate = useNavigate();

    const [users, setUsers] = useState<UserData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [actionMsg, setActionMsg] = useState('');

    const loadUsers = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await fetchUsers();
            setUsers(data);
        } catch (err: any) {
            setError(err.message || 'Error al cargar usuarios');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleToggleRole = async (user: UserData) => {
        const newRole = user.role === 'ADMIN' ? 'USER' : 'ADMIN';
        if (!confirm(`¿Cambiar el rol de "${user.full_name}" a ${newRole}? El cambio aplicará en su próximo inicio de sesión.`)) return;
        try {
            await updateUser(user.id, { role: newRole });
            setActionMsg(`Rol de ${user.full_name} cambiado a ${newRole}`);
            loadUsers();
            setTimeout(() => setActionMsg(''), 3000);
        } catch (err: any) {
            setError(err.message);
        }
    };

    const handleDeactivate = async (user: UserData) => {
        if (!confirm(`¿Estás seguro de desactivar a "${user.full_name}"? No podrá iniciar sesión.`)) return;
        try {
            await deleteUser(user.id);
            setActionMsg(`Usuario ${user.full_name} desactivado`);
            loadUsers();
            setTimeout(() => setActionMsg(''), 3000);
        } catch (err: any) {
            setError(err.message);
            setTimeout(() => setError(''), 4000);
        }
    };

    const handleActivate = async (user: UserData) => {
        try {
            await updateUser(user.id, { is_active: true });
            setActionMsg(`Usuario ${user.full_name} activado`);
            loadUsers();
            setTimeout(() => setActionMsg(''), 3000);
        } catch (err: any) {
            setError(err.message);
        }
    };

    const handleResetPassword = async (user: UserData) => {
        const newPwd = prompt(`Ingresa la nueva contraseña temporal para "${user.full_name}" (mín. 6 caracteres):`);
        if (!newPwd || newPwd.length < 6) {
            if (newPwd !== null) setError('La contraseña debe tener al menos 6 caracteres');
            return;
        }
        try {
            await resetPassword(user.id, newPwd);
            setActionMsg(`Contraseña de ${user.full_name} restablecida`);
            setTimeout(() => setActionMsg(''), 3000);
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <div className="dashboard-page">
            <header className="dashboard-header">
                <div className="dashboard-brand">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    <span>Análisis Territorial</span>
                </div>
                <nav className="dashboard-nav">
                    <button className="nav-link" onClick={() => navigate('/dashboard')}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                            <polyline points="9 22 9 12 15 12 15 22" />
                        </svg>
                        Dashboard
                    </button>
                    {role === 'ADMIN' && (
                        <button className="nav-link active">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                                <circle cx="9" cy="7" r="4" />
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                            </svg>
                            Usuarios
                        </button>
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

            <main className="um-main">
                <div className="um-header-row">
                    <h1>Gestión de Usuarios</h1>
                    <button className="btn-new-user" onClick={() => setShowModal(true)}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                        Nuevo Usuario
                    </button>
                </div>

                {actionMsg && <div className="um-success">{actionMsg}</div>}
                {error && <div className="um-error">{error}</div>}

                {loading ? (
                    <div className="um-loading">
                        <span className="spinner"></span>
                        Cargando usuarios...
                    </div>
                ) : (
                    <div className="um-table-wrap">
                        <table className="um-table">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Email</th>
                                    <th>Rol</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.id} className={!user.is_active ? 'row-inactive' : ''}>
                                        <td>{user.full_name}</td>
                                        <td>{user.email}</td>
                                        <td>
                                            <span className={`role-badge role-${user.role.toLowerCase()}`}>{user.role}</span>
                                        </td>
                                        <td>
                                            <span className={`status-badge status-${user.is_active ? 'active' : 'inactive'}`}>
                                                {user.is_active ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </td>
                                        <td className="actions-cell">
                                            <button className="btn-action btn-role" onClick={() => handleToggleRole(user)} title="Cambiar rol">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                                                    <circle cx="8.5" cy="7" r="4" />
                                                    <polyline points="17 11 19 13 23 9" />
                                                </svg>
                                                {user.role === 'ADMIN' ? 'Hacer USER' : 'Hacer ADMIN'}
                                            </button>
                                            {user.is_active ? (
                                                <button className="btn-action btn-deactivate" onClick={() => handleDeactivate(user)} title="Desactivar">
                                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                        <circle cx="12" cy="12" r="10" />
                                                        <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
                                                    </svg>
                                                    Desactivar
                                                </button>
                                            ) : (
                                                <button className="btn-action btn-activate" onClick={() => handleActivate(user)} title="Activar">
                                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                                        <polyline points="22 4 12 14.01 9 11.01" />
                                                    </svg>
                                                    Activar
                                                </button>
                                            )}
                                            <button className="btn-action btn-reset" onClick={() => handleResetPassword(user)} title="Restablecer contraseña">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                                                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                                                </svg>
                                                Reset Pass
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {users.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="um-empty">No hay usuarios registrados</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </main>

            <CreateUserModal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
                onCreated={loadUsers}
                onCreate={createUser}
            />
        </div>
    );
};

export default UserManagementPage;
