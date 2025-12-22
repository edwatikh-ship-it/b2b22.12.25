const API_BASE = 'http://127.0.0.1:8001';

export interface ParsingRun {
  runId: string;
  requestId: number;
  status: 'queued' | 'running' | 'succeeded' | 'failed';
  createdAt: string;
  updatedAt: string;
  depth?: number;
  source?: string;
}

export interface ParsingRunsResponse {
  items: ParsingRun[];
  total: number;
}

export interface ParsingLog {
  timestamp: string;
  level: string;
  message: string;
}

export interface ParsingRunLogsResponse {
  runId: string;
  logs: ParsingLog[];
}

export interface ParsingResult {
  domain: string;
  urls: string[];
  status: string;
}

export interface ParsingResultsResponse {
  requestId: number;
  runId?: string;
  results: ParsingResult[];
}

export interface StartParsingPayload {
  depth: number;
  source: 'google' | 'yandex' | 'both';
}

export interface StartParsingResponse {
  runId: string;
  status: string;
  message?: string;
}

export interface Keyword {
  id: number;
  keyword: string;
  status: 'pending' | 'parsed' | 'failed';
  createdAt: string;
  updatedAt?: string;
}

export interface KeywordsResponse {
  items: Keyword[];
  total: number;
}

export interface Supplier {
  id: number;
  name: string;
  domain?: string;
  email?: string;
  phone?: string;
  status?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface SuppliersResponse {
  items: Supplier[];
  total: number;
}

export interface CreateSupplierPayload {
  name: string;
  domain?: string;
  email?: string;
  phone?: string;
}

export interface UpdateSupplierPayload {
  name?: string;
  domain?: string;
  email?: string;
  phone?: string;
  status?: string;
}

export interface PendingDomain {
  domain: string;
  hits: number;
  createdAt: string;
}

export interface PendingDomainsResponse {
  items: PendingDomain[];
  total: number;
}

export interface DomainDecision {
  domain: string;
  decision: 'approved' | 'rejected' | 'pending';
  reason?: string;
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
  }
  
  return response.json();
}

function buildQueryString(params?: Record<string, any>): string {
  if (!params) return '';
  
  const filtered = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => [key, String(value)]);
  
  if (filtered.length === 0) return '';
  
  return '?' + new URLSearchParams(filtered).toString();
}

export const api = {
  getParsingRuns: (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ParsingRunsResponse> => 
    fetchAPI(`/moderator/parsing-runs${buildQueryString(params)}`),
  
  getParsingRun: (runId: string): Promise<ParsingResultsResponse> => 
    fetchAPI(`/moderator/parsing-runs/${runId}`),
  
  getParsingRunLogs: (runId: string): Promise<ParsingRunLogsResponse> => 
    fetchAPI(`/moderator/parsing-runs/${runId}/logs`),
  
  getParsingResults: (requestId: number): Promise<ParsingResultsResponse> => 
    fetchAPI(`/moderator/requests/${requestId}/parsing-results`),
  
  startParsing: (requestId: number, payload: StartParsingPayload): Promise<StartParsingResponse> => 
    fetchAPI(`/moderator/requests/${requestId}/start-parsing`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  
  getKeywords: (params?: {
    q?: string;
    status?: 'pending' | 'parsed' | 'failed';
    limit?: number;
    offset?: number;
    sort?: 'keyword_asc' | 'keyword_desc' | 'created_at_desc' | 'created_at_asc';
  }): Promise<KeywordsResponse> => 
    fetchAPI(`/moderator/keywords${buildQueryString(params)}`),
  
  getSuppliers: (params?: {
    q?: string;
    limit?: number;
    offset?: number;
  }): Promise<SuppliersResponse> => 
    fetchAPI(`/moderator/suppliers${buildQueryString(params)}`),
  
  createSupplier: (payload: CreateSupplierPayload): Promise<Supplier> => 
    fetchAPI('/moderator/suppliers', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  
  getSupplier: (id: number): Promise<Supplier> => 
    fetchAPI(`/moderator/suppliers/${id}`),
  
  updateSupplier: (id: number, payload: UpdateSupplierPayload): Promise<Supplier> => 
    fetchAPI(`/moderator/suppliers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  
  getPendingDomains: (params?: {
    limit?: number;
    offset?: number;
    sortBy?: 'hits' | 'createdat' | 'domain';
  }): Promise<PendingDomainsResponse> => 
    fetchAPI(`/moderator/pending-domains${buildQueryString(params)}`),
  
  getDomainDecision: (domain: string): Promise<DomainDecision> => 
    fetchAPI(`/moderator/domains/${encodeURIComponent(domain)}/decision`),
  
  setDomainDecision: (domain: string, decision: 'approved' | 'rejected', reason?: string): Promise<DomainDecision> => 
    fetchAPI(`/moderator/domains/${encodeURIComponent(domain)}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, reason }),
    }),
};
