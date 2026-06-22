import { AnalysisResult } from "./api";

const STORAGE_KEY = "lexredline_contracts";

export interface StoredContract {
  id: string;
  name: string;
  date: string;
  risk: string;
  riskColor: string;
  status: string;
  result: AnalysisResult;
}

export function saveAnalysisResult(name: string, result: AnalysisResult): StoredContract {
  const contracts = getStoredContracts();
  
  const newContract: StoredContract = {
    id: result.job_id,
    name: name,
    date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
    risk: result.overall_risk,
    riskColor: getRiskColorClass(result.overall_risk),
    status: "Complete",
    result: result
  };
  
  contracts.unshift(newContract);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(contracts));
  return newContract;
}

export function getStoredContracts(): StoredContract[] {
  if (typeof window === "undefined") return [];
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
}

export function getStoredContractById(id: string): StoredContract | null {
  const contracts = getStoredContracts();
  return contracts.find(c => c.id === id) || null;
}

function getRiskColorClass(risk: string): string {
  switch (risk.toUpperCase()) {
    case "HIGH":
    case "CRITICAL":
      return "risk-badge-high";
    case "MEDIUM":
      return "risk-badge-med";
    case "LOW":
      return "risk-badge-low";
    default:
      return "risk-badge-low";
  }
}
