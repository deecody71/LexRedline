"use client";

import { useState, useEffect } from "react";
import { ChevronRight, ChevronDown, AlertTriangle, CheckCircle, Info, ArrowRight, FileText } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";
import { useParams } from "next/navigation";

export default function ReviewPage() {
  const { id } = useParams();
  const { result } = useAnalysis();
  const [expandedId, setExpandedId] = useState<number | null>(0);

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mb-4"></div>
        <p className="text-slate-500 font-medium">Loading analysis result...</p>
        <p className="text-xs text-slate-400 mt-2">If this takes too long, please try uploading the file again.</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      {/* Left Pane - Document View */}
      <div className="flex-1 overflow-y-auto bg-slate-100 p-8">
        <div className="max-w-3xl mx-auto bg-white shadow-lg border border-slate-200 rounded-sm p-12 min-h-full font-serif text-slate-800 leading-relaxed">
          <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-accent-blue" />
              <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">{result.filename}</span>
            </div>
            <span className="text-xs text-slate-400 font-sans tracking-tighter">Parsed at: {result.parsed_at ? new Date(result.parsed_at).toLocaleString() : 'N/A'}</span>
          </div>
          
          <div className="whitespace-pre-wrap font-serif text-base text-slate-800">
            {result.full_text}
          </div>
          
          <div className="mt-12 pt-8 border-t border-slate-200 text-slate-400 text-xs italic font-sans text-center">
            [END OF DOCUMENT]
          </div>
        </div>
      </div>

      {/* Right Pane - Annotations */}
      <div className="w-[450px] border-l border-slate-200 bg-white overflow-y-auto">
        <div className="p-6 border-b border-slate-200 bg-slate-50 sticky top-0 z-10">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-lg font-bold text-navy flex items-center">
              <AlertTriangle className="w-5 h-5 text-risk-high mr-2" />
              Risk Analysis
            </h2>
            <div className={`risk-badge ${
              result.overall_risk === 'HIGH' ? 'risk-badge-high' : 
              result.overall_risk === 'MEDIUM' ? 'risk-badge-med' : 'risk-badge-low'
            }`}>
              Overall: {result.overall_risk}
            </div>
          </div>
          <p className="text-xs text-slate-500">Detected {result.redlines.length} items requiring review</p>
        </div>

        <div className="divide-y divide-slate-100">
          {result.redlines.map((item, index) => (
            <div key={index} className={`p-4 transition-colors ${expandedId === index ? 'bg-blue-50/30' : 'hover:bg-slate-50'}`}>
              <button 
                onClick={() => setExpandedId(expandedId === index ? null : index)}
                className="w-full text-left"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold text-navy text-sm">{item.clause_type.replace(/_/g, ' ').toUpperCase()}</span>
                  <span className={`risk-badge ${
                    item.priority >= 3 ? 'risk-badge-high' : 
                    item.priority >= 2 ? 'risk-badge-med' : 'risk-badge-low'
                  }`}>
                    P{item.priority}
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-2 mb-2 italic bg-slate-100 p-2 rounded">
                  "{item.original_text}"
                </p>
                <div className="flex items-center text-xs text-accent-blue font-medium">
                  {expandedId === index ? (
                    <>
                      <ChevronDown className="w-3 h-3 mr-1" />
                      Hide Details
                    </>
                  ) : (
                    <>
                      <ChevronRight className="w-3 h-3 mr-1" />
                      View Suggestions
                    </>
                  )}
                </div>
              </button>

              {expandedId === index && (
                <div className="mt-4 pt-4 border-t border-slate-100 animate-in fade-in slide-in-from-top-1">
                  <div className="mb-4">
                    <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-2">Issue / Risk</h4>
                    <div className="bg-white border border-slate-100 rounded p-3 text-xs text-slate-700 shadow-sm">
                      {item.risk_reason}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 mb-2">Suggested Redline</h4>
                    <div className="bg-white border border-blue-100 rounded p-3 text-xs text-slate-700 leading-relaxed shadow-sm border-l-4 border-l-accent-blue">
                      {item.suggested_text}
                    </div>
                  </div>

                  <div className="mt-4 flex space-x-2">
                    <button className="flex-1 bg-accent-blue text-white py-2 rounded text-xs font-bold hover:bg-blue-700 transition-colors shadow-sm">
                      Accept Redline
                    </button>
                    <button className="flex-1 border border-slate-200 text-slate-700 py-2 rounded text-xs font-bold hover:bg-slate-50 transition-colors shadow-sm">
                      Dismiss
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          
          {result.redlines.length === 0 && (
            <div className="p-12 text-center">
              <CheckCircle className="w-12 h-12 text-risk-low mx-auto mb-4 opacity-20" />
              <p className="text-slate-500 font-medium">No risks detected</p>
              <p className="text-xs text-slate-400 mt-1">This contract looks good based on standard policies.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
