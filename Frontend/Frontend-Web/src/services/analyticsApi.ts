const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

export interface Dataset {
    datasetId: string;
    fileName: string;
    sourceName: string | null;
    sourceType: string | null;
    status: string;
    totalRecords: number;
    createdAt: string;
}

export async function fetchDatasets(): Promise<Dataset[]> {
    const res = await fetch(`${API_BASE}/api/v1/ingestion/datasets/`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al obtener datasets');
    return res.json();
}

export async function getDatasetById(id: string): Promise<Dataset> {
    const res = await fetch(`${API_BASE}/api/v1/ingestion/datasets/${id}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al validar dataset');
    return res.json();
}

export async function transformAdvanced(datasetLoadId: string, method: string = 'minmax'): Promise<{ run_id: string }> {
    const res = await fetch(`${API_BASE}/api/v1/transformation/api/v1/transform/advanced`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ dataset_load_id: datasetLoadId, method }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error en la transformación');
    return res.json();
}

export async function calculateIndicators(transformationRunId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/analytics/api/v1/indicators/calculate?transformation_run_id=${transformationRunId}`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al calcular indicadores');
    return res.json();
}

export async function executeScoring(transformationRunId: string): Promise<{ id: string }> {
    const res = await fetch(`${API_BASE}/api/v1/analytics/api/v1/scoring/execute?transformation_run_id=${transformationRunId}`, {
        method: 'POST',
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al ejecutar scoring');
    return res.json();
}

export async function getRanking(executionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/analytics/api/v1/ranking?execution_id=${executionId}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al obtener ranking');
    return res.json();
}

export async function getZoneSummary(zoneCode: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/bff/zone-summary/${zoneCode}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Error al obtener resumen de zona');
    return res.json();
}
