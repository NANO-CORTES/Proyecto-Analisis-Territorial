const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

export interface UserData {
    id: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
    created_at: string;
    last_login: string | null;
}

export async function fetchUsers(): Promise<UserData[]> {
    const res = await fetch(`${API_BASE}/api/v1/admin/users/`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al obtener usuarios');
    return res.json();
}

export async function createUser(data: {
    email: string;
    full_name: string;
    password: string;
    role: string;
}): Promise<UserData> {
    const res = await fetch(`${API_BASE}/api/v1/admin/users/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al crear usuario');
    return res.json();
}

export async function updateUser(
    userId: string,
    data: { role?: string; is_active?: boolean }
): Promise<UserData> {
    const res = await fetch(`${API_BASE}/api/v1/admin/users/${userId}`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al actualizar usuario');
    return res.json();
}

export async function deleteUser(userId: string): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/api/v1/admin/users/${userId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al desactivar usuario');
    return res.json();
}

export async function resetPassword(
    userId: string,
    newPassword: string
): Promise<{ message: string }> {
    const res = await fetch(`${API_BASE}/api/v1/admin/users/${userId}/reset-password`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ new_password: newPassword }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al restablecer contraseña');
    return res.json();
}
