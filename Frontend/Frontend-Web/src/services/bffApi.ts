const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

export interface ZoneSummary {
    zone_code: string;
    analytics: any | null;
    recommendation: any | null;
    prediction: any | null;
    partial: boolean;
}

export interface CompareRow {
    zone_code: string;
    zone_name: string;
    indicators: Record<string, number> | null;
    score_value: number | null;
    score_level: string | null;
    combined_score: number | null;
    prediction_value: number | null;
    prediction_label: string | null;
    discrepancy_flag: boolean | null;
}

export interface CompareResponse {
    total: number;
    zones: CompareRow[];
}

export interface DashboardSummary {
    total_zones_analyzed: number;
    avg_score: number | null;
    top_zone: any;
    score_distribution: Record<string, number>;
}

export async function getZoneSummaryBff(zoneCode: string): Promise<ZoneSummary> {
    const res = await fetch(`${API_BASE}/api/bff/zone-summary/${zoneCode}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo obtener el resumen de la zona');
    return res.json();
}

export async function compareZones(codes: string[]): Promise<CompareResponse> {
    const param = encodeURIComponent(codes.join(','));
    const res = await fetch(`${API_BASE}/api/bff/compare?zones=${param}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo comparar las zonas');
    return res.json();
}

export async function dashboardSummary(executionId: string): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/api/bff/dashboard-summary?execution_id=${executionId}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo obtener el resumen del dashboard');
    return res.json();
}

export async function downloadRankingCsv(executionId: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/api/bff/export/ranking?execution_id=${executionId}&format=csv`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo exportar el ranking');
    return res.blob();
}

export async function downloadZoneReportJson(zoneCode: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/bff/export/zone-report/${zoneCode}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo exportar el reporte');
    return res.json();
}

export async function predictZones(zoneCodes: string[]): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/ml/api/v1/ml/predict`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ zone_codes: zoneCodes }),
    });
    if (!res.ok) throw new Error('No se pudo obtener la predicción');
    return res.json();
}

export async function getAuditEvents(params: {
    service?: string;
    user_id?: string;
    event_type?: string;
    limit?: number;
} = {}): Promise<any[]> {
    const search = new URLSearchParams();
    if (params.service) search.set('service', params.service);
    if (params.user_id) search.set('user_id', params.user_id);
    if (params.event_type) search.set('event_type', params.event_type);
    search.set('limit', String(params.limit ?? 200));
    const res = await fetch(`${API_BASE}/api/v1/audit/api/v1/events?${search.toString()}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo obtener el log de auditoría');
    return res.json();
}

export async function getConfigActive(): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/configuration/api/v1/config/scoring/active`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo obtener la configuración activa');
    return res.json();
}

export async function saveScoringConfig(payload: Record<string, number | string>): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/configuration/api/v1/config/scoring`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('No se pudo guardar la configuración');
    return res.json();
}

export interface LatestAnalysisResponse {
    execution_id: string;
    status: string;
    transformation_run_id?: string;
    configuration_id?: string;
    created_at?: string;
}

export async function getLatestAnalysis(): Promise<LatestAnalysisResponse> {
    const res = await fetch(`${API_BASE}/api/bff/latest-analysis`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('No se pudo obtener el último análisis');
    return res.json();
}

export async function downloadLatestReport(format: 'csv' | 'json' | 'xls'): Promise<Blob> {
    const res = await fetch(`${API_BASE}/api/bff/export/latest?format=${format}`, {
        headers: getAuthHeaders(),
    });
    if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'No se pudo descargar el reporte');
    }
    return res.blob();
}
