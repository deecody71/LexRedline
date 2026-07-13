"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { FileText, Eye, AlertCircle, CheckCircle2, Clock, Archive, Trash2, Undo2 } from "lucide-react";
import { getStoredContracts, getActiveContracts, getArchivedContracts, toggleArchiveContract, deleteContract, StoredContract } from "@/lib/storage";

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
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const loadContracts = () => {
    const stored = showArchived ? getArchivedContracts() : getActiveContracts();
    const formattedStored = stored.map(c => ({
      ...c,
      statusIcon: <CheckCircle2 className="w-4 h-4 text-green-500" />
    }));
    setContracts([...formattedStored, ...sampleContracts]);
  };

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/sign-in");
       } else if (!(user.unsafeMetadata as any)?.profile && !localStorage.getItem("lexredline_profile_complete")) {
        router.push("/profile");
      }
    }

    if (isLoaded && user && ((user.unsafeMetadata as any)?.profile || localStorage.getItem("lexredline_profile_complete"))) {
      loadContracts();
    }
  }, [user, isLoaded, router, showArchived]);

  const handleToggleArchive = (id: string) => {
    toggleArchiveContract(id);
    loadContracts();
  };

  const handleDelete = (id: string) => {
    deleteContract(id);
    setDeleteConfirm(null);
    loadContracts();
  };

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-blue"></div>
      </div>
    );
  }
  const clearHistory = () => {
    localStorage.removeItem("lexredline_contracts");
    setContracts([...sampleContracts]);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">Contract Reviews</h1>
          <p className="text-slate-500">Monitor and manage your contract risk assessments</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="bg-slate-100 rounded-lg p-1 flex">
            <button
              onClick={() => setShowArchived(false)}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-colors ${!showArchived ? 'bg-white shadow-sm text-navy' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Active
            </button>
            <button
              onClick={() => setShowArchived(true)}
              className={`px-3 py-1.5 rounded text-xs font-bold transition-colors ${showArchived ? 'bg-white shadow-sm text-navy' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Archived
            </button>
          </div>
          <button 
            onClick={clearHistory}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
          >
            Clear History
          </button>
          <Link href="/upload" className="btn-primary flex items-center space-x-2">
            <span>Upload Contract</span>
          </Link>
        </div>
      </div>

      <div className="bg-white shadow-sm border border-slate-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Contract Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Date Uploaded
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Risk Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {contracts.map((contract) => (
              <tr key={contract.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-slate-400 mr-3" />
                    <span className="text-sm font-medium text-slate-900">{contract.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                  {contract.date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`risk-badge ${contract.riskColor}`}>
                    {contract.risk}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center space-x-2 text-sm text-slate-700">
                    {contract.statusIcon}
                    <span>{contract.status}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-1">
                    <Link
                      href={`/review/${contract.id}`}
                      className="text-accent-blue hover:text-blue-800 flex items-center space-x-1 p-1"
                      title="View"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => handleToggleArchive(contract.id)}
                      className="text-slate-400 hover:text-amber-600 p-1 transition-colors"
                      title={contract.archived ? "Unarchive" : "Archive"}
                    >
                      {contract.archived ? <Undo2 className="w-4 h-4" /> : <Archive className="w-4 h-4" />}
                    </button>
                    {deleteConfirm === contract.id ? (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => handleDelete(contract.id)}
                          className="text-red-600 hover:text-red-800 text-xs font-bold px-2 py-1 bg-red-50 rounded transition-colors"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(null)}
                          className="text-slate-400 hover:text-slate-600 text-xs px-1"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirm(contract.id)}
                        className="text-slate-400 hover:text-red-600 p-1 transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
