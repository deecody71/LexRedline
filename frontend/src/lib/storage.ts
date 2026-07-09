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
  archived?: boolean;
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

export function getActiveContracts(): StoredContract[] {
  return getStoredContracts().filter(c => !c.archived);
}

export function getArchivedContracts(): StoredContract[] {
  return getStoredContracts().filter(c => c.archived);
}

export function toggleArchiveContract(id: string): StoredContract[] {
  const contracts = getStoredContracts();
  const updated = contracts.map(c => {
    if (c.id === id) {
      return { ...c, archived: !c.archived };
    }
    return c;
  });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  return updated;
}

export function deleteContract(id: string): StoredContract[] {
  const contracts = getStoredContracts();
  const updated = contracts.filter(c => c.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  return updated;
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
