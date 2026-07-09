const API_BASE_URL = '/api/v1';

export interface AnalysisResult {
  job_id: string;
  filename: string;
  file_type: string;
  page_count: number;
  sections: Section[];
  full_text: string;
  clauses: Clause[];
  risk_scores: RiskScore[];
  overall_risk: string;
  overall_risk_score: number;
  redlines: RedlineSuggestion[];
  clause_count: number;
  analysis_time_ms: number;
  contract_metadata: Record<string, any>;
  parsed_at: string | null;
  expectation_match?: ExpectationMatchResult;
  profile?: ProfileInfo | null;
}

export interface ProfileInfo {
  applied: boolean;
  role: string | null;
  preferences: string[];
  modifications: string[];
}

export interface ExpectationMatchResult {
  total_expectations: number;
  matched: Array<{ keyword: string; phrase: string; status: string; expected_types: string[] }>;
  unmatched: Array<{ keyword: string; phrase: string; status: string; expected_types: string[] }>;
  match_percentage: number;
  matched_types: string[];
  recommendations: string[];
}

export interface Section {
  heading: string;
  level: number;
  content: string;
  subsections: Section[];
  start_page: number;
  end_page: number;
}

export interface Clause {
  clause_type: string;
  section_ref: string | null;
  text: string;
  confidence: number;
  metadata: Record<string, any>;
}

export interface RiskScore {
  clause_type: string;
  risk_level: string;
  score: number;
  reasoning: string;
  flags: string[];
}

export interface RedlineSuggestion {
  clause_type: string;
  original_text: string;
  suggested_text: string;
  risk_reason: string;
  priority: number;
}

export interface UserProfile {
  role: 'reviewer' | 'creator' | 'both';
  preference_ids: string[];
  custom_preferences?: string;
}

export interface ContractSummary {
  id: string;
  filename: string;
  created_at: string;
}

export interface QAResponse {
  answer: string;
  model_used?: string;
}

export interface HelpResponse {
  answer: string;
  source?: string;
  related_questions: string[];
  model_used?: string;
}

async function getAuthToken(): Promise<string | null> {
  try {
    if (typeof window !== 'undefined' && (window as any).Clerk?.session) {
      return await (window as any).Clerk.session.getToken();
    }
  } catch {}
  return null;
}

async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getAuthToken();
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return fetch(url, { ...options, headers });
}

export async function analyzeFile(
  file: File,
  expectations?: string
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);

  if (expectations && expectations.trim()) {
    formData.append('expectations', expectations.trim());
  }

  const response = await authFetch(`${API_BASE_URL}/analyze/file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
  }

  return response.json();
}

export async function analyzeText(
  text: string,
  filename: string = 'contract.txt',
  expectations?: string,
  profile?: UserProfile
): Promise<AnalysisResult> {
  const response = await authFetch(`${API_BASE_URL}/analyze/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, filename, expectations, profile }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Analysis failed with status ${response.status}`);
  }

  return response.json();
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
}

export async function listClauseTypes(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/clauses`);
  return response.json();
}

export async function getAvailableProfiles(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/profiles`);
  return response.json();
}

export async function getUserContracts(): Promise<ContractSummary[]> {
  const response = await authFetch(`${API_BASE_URL}/contracts`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to fetch contracts: ${response.status}`);
  }
  return response.json();
}

export async function getContract(id: string): Promise<AnalysisResult> {
  const response = await authFetch(`${API_BASE_URL}/contracts/${id}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Failed to fetch contract: ${response.status}`);
  }
  return response.json();
}

export async function askQuestion(question: string, analysisId?: string): Promise<QAResponse> {
  const response = await authFetch(`${API_BASE_URL}/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, analysis_id: analysisId }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to get answer' }));
    throw new Error(errorData.detail || 'Failed to get answer');
  }

  return response.json();
}

export async function getHelpAnswer(question: string): Promise<HelpResponse> {
  const response = await fetch(`${API_BASE_URL}/help`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch help content' }));
    throw new Error(errorData.detail || 'Failed to fetch help content');
  }

  return response.json();
}
