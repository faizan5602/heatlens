import { AnalysisResponse } from '../types/heatlens';

// Reads from VITE_API_BASE_URL in production, falls back to localhost for local dev
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE = `${BASE_URL.replace(/\/$/, '')}/api`;

async function getApiError(res: Response, fallback: string): Promise<Error> {
  try {
    const payload = await res.json();
    return new Error(typeof payload.detail === 'string' ? payload.detail : fallback);
  } catch {
    return new Error(fallback);
  }
}

export async function runAnalysis(locationName: string): Promise<AnalysisResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 120000); // 2 minute timeout

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ location_name: locationName, use_cache: true }),
      signal: controller.signal,
    });

    if (!res.ok) {
      throw await getApiError(res, `Analysis failed: ${res.statusText}`);
    }

    return res.json();
  } finally {
    clearTimeout(timeout);
  }
}

export async function queryAiAnalyst(query: string, context: any): Promise<string> {
  const res = await fetch(`${API_BASE}/ai/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, analysis_context: context }),
  });

  if (!res.ok) {
    throw await getApiError(res, `AI query failed: ${res.statusText}`);
  }

  const data = await res.json();
  return data.response;
}