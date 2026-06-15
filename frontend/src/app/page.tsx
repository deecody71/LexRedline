import Link from "next/link";
import { FileText, Eye, AlertCircle, CheckCircle2, Clock } from "lucide-react";

const contracts = [
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
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-navy">Contract Reviews</h1>
          <p className="text-slate-500">Monitor and manage your contract risk assessments</p>
        </div>
        <Link href="/upload" className="btn-primary flex items-center space-x-2">
          <span>Upload Contract</span>
        </Link>
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
                  <Link
                    href={`/review/${contract.id}`}
                    className="text-accent-blue hover:text-blue-800 flex items-center justify-end space-x-1"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View</span>
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
