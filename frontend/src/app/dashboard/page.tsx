"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { FileText, Eye, AlertCircle, CheckCircle2, Clock, Archive, ArchiveRestore, Trash2 } from "lucide-react";
import { getStoredContracts, archiveContract, unarchiveContract, deleteContract, StoredContract } from "@/lib/storage";

const sampleContracts = [
  {
    id: "saas-acme",
    name: "SaaS Agreement - Acme Corp",
    date: "Jun 15, 2026",
    risk: "HIGH",
    riskColor: "risk-badge-high",
    status: "Complete",
    statusIcon: <CheckCircle2 className="w-4 h-4 text-green-500" />,
  },
  {
    id: "nda-beta",
    name: "NDA - Beta Partners",
    date: "Jun 14, 2026",
    risk: "LOW",
    riskColor: "risk-badge-low",
    status: "Complete",
    statusIcon: <CheckCircle2 className="w-4 h-4 text-green-500" />,
  },
  {
    id: "psa-gamma",
    name: "PSA - Gamma LLC",
    date: "Jun 13, 2026",
    risk: "MEDIUM",
    riskColor: "risk-badge-med",
    status: "In Review",
    statusIcon: <Clock className="w-4 h-4 text-amber-500" />,
  },
];

export default function Dashboard() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [contracts, setContracts] = useState<any[]>([]);
  const [showArchived, setShowArchived] = useState(false);

  const refreshContracts = () => {
    if (isLoaded && user && ((user.publicMetadata as any)?.profile || (user.unsafeMetadata as any)?.profile)) {
      const stored = getStoredContracts();
      const formattedStored = stored.map(c => ({
        ...c,
        statusIcon: <CheckCircle2 className="w-4 h-4 text-green-500" />
      }));
      // Keep sample contracts non-archived for display
      const samples = sampleContracts.map(s => ({ ...s, archived: false }));
      setContracts([...formattedStored, ...samples]);
    }
  };

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/sign-up");
      } else if (!(user.publicMetadata as any)?.profile && !(user.unsafeMetadata as any)?.profile) {
        router.push("/profile");
      }
    }
    refreshContracts();
  }, [user, isLoaded, router]);

  const handleArchive = (id: string) => {
    archiveContract(id);
    refreshContracts();
  };

  const handleUnarchive = (id: string) => {
    unarchiveContract(id);
    refreshContracts();
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this contract?")) {
      deleteContract(id);
      refreshContracts();
    }
  };

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-blue"></div>
      </div>
    );
  }

  const clearHistory = () => {
    if (confirm("This will clear all uploaded contracts. Sample data will remain. Continue?")) {
      localStorage.removeItem("lexredline_contracts");
      refreshContracts();
    }
  };

  const displayedContracts = contracts.filter(c => showArchived ? c.archived : !c.archived);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">Contract Reviews</h1>
          <p className="text-slate-500">Monitor and manage your contract risk assessments</p>
          
          <div className="mt-4 flex items-center space-x-1 bg-slate-100 p-1 rounded-lg w-fit">
            <button 
              onClick={() => setShowArchived(false)}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${!showArchived ? 'bg-white shadow-sm text-navy' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Active
            </button>
            <button 
              onClick={() => setShowArchived(true)}
              className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${showArchived ? 'bg-white shadow-sm text-navy' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Archived
            </button>
          </div>
        </div>
        <div className="flex space-x-4">
          <button 
            onClick={clearHistory}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-red-600 transition-colors"
          >
            Clear History
          </button>
          <Link href="/upload" className="btn-primary flex items-center space-x-2 shadow-lg shadow-blue-100">
            <span>Upload Contract</span>
          </Link>
        </div>
      </div>

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        {displayedContracts.length === 0 ? (
          <div className="py-20 text-center">
            <FileText className="w-12 h-12 text-slate-200 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900">No {showArchived ? 'archived' : 'active'} contracts</h3>
            <p className="text-slate-500">
              {showArchived 
                ? "You haven't archived any contracts yet." 
                : "Upload a contract to get started with your first analysis."}
            </p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-4 text-left text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Contract Name
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Date Uploaded
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Risk Score
                </th>
                <th className="px-6 py-4 text-left text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Status
                </th>
                <th className="px-6 py-4 text-right text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {displayedContracts.map((contract) => (
                <tr key={contract.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-slate-300 mr-3 group-hover:text-accent-blue transition-colors" />
                      <span className="text-sm font-semibold text-navy">{contract.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-medium">
                    {contract.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`risk-badge ${contract.riskColor}`}>
                      {contract.risk}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-tight text-slate-500">
                      {contract.statusIcon}
                      <span>{contract.status}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-3">
                      <Link
                        href={`/review/${contract.id}`}
                        className="text-slate-400 hover:text-accent-blue transition-colors p-1"
                        title="View Analysis"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      
                      {contract.id.startsWith('saas-') || contract.id.startsWith('nda-') || contract.id.startsWith('psa-') ? null : (
                        <>
                          {contract.archived ? (
                            <button 
                              onClick={() => handleUnarchive(contract.id)}
                              className="text-slate-400 hover:text-green-600 transition-colors p-1"
                              title="Unarchive"
                            >
                              <ArchiveRestore className="w-4 h-4" />
                            </button>
                          ) : (
                            <button 
                              onClick={() => handleArchive(contract.id)}
                              className="text-slate-400 hover:text-amber-600 transition-colors p-1"
                              title="Archive"
                            >
                              <Archive className="w-4 h-4" />
                            </button>
                          )}
                          <button 
                            onClick={() => handleDelete(contract.id)}
                            className="text-slate-400 hover:text-red-600 transition-colors p-1"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
