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
  expectation_match?: {
    match_percentage: number;
    matched: string[];
    unmatched: string[];
    recommendations: string[];
  };
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

export async function analyzeFile(file: File, expectations?: string): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);
  if (expectations) {
    formData.append('expectations', expectations);
  }

  const response = await fetch(`${API_BASE_URL}/analyze/file`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
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
