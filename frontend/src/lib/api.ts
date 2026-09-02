const BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || '/api/v1';

let authToken: string | undefined = undefined;

export const setAuthToken = (token: string | undefined) => {
  authToken = token;
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
  
  const response = await fetch(url, { ...options, headers });
  
  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.status} ${response.statusText}`);
  }
  
  // Some endpoints like 202 or 204 might return empty body
  const text = await response.text();
  return text ? JSON.parse(text) : ({} as T);
}

export const api = {
  getDashboardSummary: () => request<any>('/dashboard/summary'),
  getProjects: () => request<any>('/projects'),
  getProject: (id: string) => request<any>(`/projects/${id}`),
  getProjectIntelligence: (id: string) => request<any>(`/projects/${id}/intelligence`),
  getProjectRisk: (id: string) => request<any>(`/projects/${id}/risk`),
  getProjectTimeline: (id: string) => request<any>(`/projects/${id}/timeline`),
  getProjectFinancials: (id: string) => request<any>(`/projects/${id}/financials`),
  getProjectInspections: (id: string) => request<any>(`/projects/${id}/inspections`),
  getProjectMedia: (id: string) => request<any>(`/projects/${id}/media`),
  getAlerts: () => request<any>('/alerts'),
  acknowledgeAlert: (id: string) => request<any>(`/alerts/${id}/acknowledge`, { method: 'PATCH' }),
  queryInvestigation: (payload: any) => request<any>('/investigation/query', { method: 'POST', body: JSON.stringify(payload) }),
  presignUpload: (payload: { project_id: string, stage: string, filename: string, content_type: string }) => 
    request<any>('/uploads/presign', { method: 'POST', body: JSON.stringify(payload) }),
  completeUpload: (payload: { project_id: string, stage: string, object_key: string }) => 
    request<any>('/uploads/complete', { method: 'POST', body: JSON.stringify(payload) }),
};
