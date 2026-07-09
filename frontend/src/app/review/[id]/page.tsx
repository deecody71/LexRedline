"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { ChevronRight, ChevronDown, AlertTriangle, CheckCircle, Info, ArrowRight, FileText, Trash2, Download, Printer } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";
import { useUser } from "@clerk/nextjs";
import { useParams, useRouter } from "next/navigation";
import { SAMPLE_DATA } from "@/lib/sampleData";
import { getStoredContractById, StoredContract } from "@/lib/storage";

export default function ReviewPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { result: contextResult } = useAnalysis();
  const [result, setResult] = useState<any>(null);
  const [expandedId, setExpandedId] = useState<number | null>(0);
  const [acceptedRedlines, setAcceptedRedlines] = useState<Set<number>>(new Set());
  const [dismissedRedlines, setDismissedRedlines] = useState<Set<number>>(new Set());
  const textContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/sign-up");
        return;
        } else if (!(user.unsafeMetadata as any)?.profile && !localStorage.getItem("lexredline_profile_complete")) {
        router.push("/profile");
        return;
      }
    }

    // 1. Try context (from fresh upload)
    if (contextResult && (contextResult.job_id === id)) {
      setResult(contextResult);
      return;
    }

    // 2. Try sample data
    if (typeof id === 'string' && SAMPLE_DATA[id]) {
      setResult(SAMPLE_DATA[id]);
      return;
    }

    // 3. Try storage
    if (typeof id === 'string') {
      const stored = getStoredContractById(id);
      if (stored) {
        setResult(stored.result);
        return;
      }
    }
  }, [id, contextResult, isLoaded, user, router]);

  if (!isLoaded || !user) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-blue"></div>
      </div>
    );
  }

  // Derived state: the document text with accepted redlines
  const processedTextSegments = useMemo(() => {
    if (!result) return [];
    
    let text = result.full_text;
    const segments: { text: string; isAccepted?: boolean; index?: number }[] = [];
    
    // Sort redlines by their position in text to process linearly
    // Since we don't have indices, we'll find them
    const sortedRedlines = result.redlines
      .map((rl: any, idx: number) => ({ ...rl, originalIndex: idx, pos: text.indexOf(rl.original_text) }))
      .filter((rl: any) => rl.pos !== -1)
      .sort((a: any, b: any) => a.pos - b.pos);
    
    let lastIndex = 0;
    for (const rl of sortedRedlines) {
      // Add text before the redline
      if (rl.pos > lastIndex) {
        segments.push({ text: text.substring(lastIndex, rl.pos) });
      }
      
      const isAccepted = acceptedRedlines.has(rl.originalIndex);
      segments.push({ 
        text: isAccepted ? rl.suggested_text : rl.original_text, 
        isAccepted,
        index: rl.originalIndex
      });
      
      lastIndex = rl.pos + rl.original_text.length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      segments.push({ text: text.substring(lastIndex) });
    }
    
    return segments;
  }, [result, acceptedRedlines]);

  const scrollToText = (searchText: string) => {
    if (!textContainerRef.current) return;
    const container = textContainerRef.current;
    
    // Find the element containing the text
    const elements = container.querySelectorAll('[data-original-text]');
    for (const el of Array.from(elements)) {
      if (el.getAttribute('data-original-text') === searchText) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Highlight briefly
        el.classList.add('ring-4', 'ring-yellow-200', 'ring-opacity-50');
        setTimeout(() => {
          el.classList.remove('ring-4', 'ring-yellow-200', 'ring-opacity-50');
        }, 2000);
        return;
      }
    }
  };

  const handleAcceptRedline = (index: number) => {
    setAcceptedRedlines(prev => new Set(prev).add(index));
    setDismissedRedlines(prev => {
      const next = new Set(prev);
      next.delete(index);
      return next;
    });
    setExpandedId(null);
  };

  const handleDismissRedline = (index: number) => {
    setDismissedRedlines(prev => new Set(prev).add(index));
    setAcceptedRedlines(prev => {
      const next = new Set(prev);
      next.delete(index);
      return next;
    });
    setExpandedId(null);
  };

  const handleExportPDF = () => {
    window.print();
  };

  const handleExportWord = () => {
    const riskLevel = result?.overall_risk || 'N/A';
    const filename = result?.filename || 'contract';
    const clauses = result?.redlines || [];
    
    let html = `<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>LexRedline Report - ${filename}</title>
<style>
  body { font-family: 'Calibri', 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; color: #1e293b; line-height: 1.6; }
  h1 { font-size: 24px; border-bottom: 2px solid #2563eb; padding-bottom: 8px; }
  .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; }
  .risk-high { background: #fee2e2; color: #dc2626; }
  .risk-med { background: #fef3c7; color: #d97706; }
  .risk-low { background: #dcfce7; color: #16a34a; }
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 13px; }
  th { background: #f8fafc; font-weight: bold; color: #475569; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
  .clause-type { font-weight: bold; color: #1e293b; text-transform: uppercase; font-size: 12px; }
  .meta { color: #94a3b8; font-size: 11px; margin-top: 24px; padding-top: 12px; border-top: 1px solid #e2e8f0; }
</style>
</head>
<body>
  <h1>LexRedline Contract Review</h1>
  <p style="color:#64748b;">Document: <strong>${filename}</strong></p>
  <p>Overall Risk: <span class="risk-badge risk-${riskLevel.toLowerCase()}">${riskLevel}</span></p>
  <p>Clauses flagged: ${clauses.length}</p>
  <hr style="margin: 24px 0; border: none; border-top: 1px solid #e2e8f0;">
  <table>
    <tr><th>Clause</th><th>Risk</th><th>Issue</th></tr>`;
    
    clauses.forEach((c: any) => {
      const priority = c.priority || 0;
      const riskLabel = priority >= 3 ? 'High' : priority >= 2 ? 'Medium' : 'Low';
      html += `<tr>
        <td class="clause-type">${c.clause_type?.replace(/_/g, ' ') || 'Unknown'}</td>
        <td><span class="risk-badge ${priority >= 3 ? 'risk-high' : priority >= 2 ? 'risk-med' : 'risk-low'}">${riskLabel}</span></td>
        <td>${(c.risk_reason || '').substring(0, 120)}</td>
      </tr>`;
    });
    
    html += `</table>
  <div class="meta">
    <p>Generated by LexRedline on ${new Date().toLocaleDateString()}</p>
    <p>Disclaimer: This is an AI-assisted analysis and does not constitute legal advice.</p>
  </div>
</body>
</html>`;
    
    const blob = new Blob([html], { type: 'application/msword' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename.replace(/\.[^.]+$/, '')}_lexredline_report.doc`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-4rem)] bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent-blue mb-4"></div>
        <p className="text-slate-500 font-medium">Loading analysis result...</p>
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
            <div className="flex items-center space-x-2">
              <button
                onClick={handleExportPDF}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-accent-blue text-white rounded text-xs font-bold hover:bg-blue-700 transition-colors shadow-sm print:hidden"
                title="Export as PDF"
              >
                <Printer className="w-3.5 h-3.5" />
                PDF
              </button>
              <button
                onClick={handleExportWord}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-accent-blue text-accent-blue rounded text-xs font-bold hover:bg-blue-50 transition-colors print:hidden"
                title="Export as Word document"
              >
                <Download className="w-3.5 h-3.5" />
                Word
              </button>
              <span className="text-xs text-slate-400 font-sans tracking-tighter">Parsed at: {result.parsed_at ? new Date(result.parsed_at).toLocaleString() : 'N/A'}</span>
            </div>
          </div>
          
          <div 
            ref={textContainerRef}
            className="whitespace-pre-wrap font-serif text-base text-slate-800"
          >
            {processedTextSegments.map((segment, i) => (
              <span 
                key={i} 
                className={segment.isAccepted ? "bg-green-100 text-green-900 px-1 rounded border-b border-green-300" : ""}
                data-original-text={segment.index !== undefined ? result.redlines[segment.index].original_text : undefined}
              >
                {segment.text}
              </span>
            ))}
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

        {/* Expectation Match Section */}
        {result.expectation_match && (
          <div className="p-4 border-b border-slate-200 bg-white">
            <h3 className="text-sm font-bold text-navy mb-3 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Expectation Match
            </h3>
            <div className="flex items-center gap-3 mb-3">
              <div className={`text-2xl font-bold ${
                result.expectation_match.match_percentage >= 80 ? 'text-green-600' :
                result.expectation_match.match_percentage >= 50 ? 'text-amber-600' :
                'text-red-600'
              }`}>
                {Math.round(result.expectation_match.match_percentage)}%
              </div>
              <div className="text-xs text-slate-500">
                of expectations met
              </div>
            </div>
            {result.expectation_match.matched.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-semibold text-green-700 mb-1">✅ Met ({result.expectation_match.matched.length})</p>
                <ul className="text-xs text-slate-600 space-y-0.5">
                  {result.expectation_match.matched.map((m: any, i: number) => (
                    <li key={i} className="truncate">{m.expectation}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.expectation_match.unmatched.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-semibold text-red-700 mb-1">❌ Missing ({result.expectation_match.unmatched.length})</p>
                <ul className="text-xs text-slate-600 space-y-0.5">
                  {result.expectation_match.unmatched.map((u: any, i: number) => (
                    <li key={i} className="truncate">{u.expectation}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.expectation_match.recommendations.length > 0 && (
              <div className="mt-2 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
                <p className="font-semibold mb-0.5">Recommendations:</p>
                <ul className="list-disc list-inside space-y-0.5">
                  {result.expectation_match.recommendations.map((r: string, i: number) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="divide-y divide-slate-100">
          {result.redlines.map((item: any, index: number) => {
            const isAccepted = acceptedRedlines.has(index);
            const isDismissed = dismissedRedlines.has(index);
            
            return (
              <div 
                key={index} 
                className={`p-4 transition-colors ${expandedId === index ? 'bg-blue-50/30' : 'hover:bg-slate-50'} ${(isAccepted || isDismissed) ? 'opacity-50' : ''}`}
              >
                <button 
                  onClick={() => {
                    setExpandedId(expandedId === index ? null : index);
                    if (expandedId !== index) scrollToText(item.original_text);
                  }}
                  className="w-full text-left"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center">
                      {isAccepted && <CheckCircle className="w-4 h-4 text-green-500 mr-2" />}
                      {isDismissed && <Trash2 className="w-4 h-4 text-slate-400 mr-2" />}
                      <span className="font-bold text-navy text-sm uppercase tracking-tight">
                        {item.clause_type.replace(/_/g, ' ')}
                      </span>
                    </div>
                    {!isAccepted && !isDismissed && (
                      <span className={`risk-badge ${
                        item.priority >= 3 ? 'risk-badge-high' : 
                        item.priority >= 2 ? 'risk-badge-med' : 'risk-badge-low'
                      }`}>
                        P{item.priority}
                      </span>
                    )}
                  </div>
                  <p className={`text-xs text-slate-600 line-clamp-2 mb-2 italic p-2 rounded ${isAccepted ? 'bg-green-50' : 'bg-slate-100'}`}>
                    "{isAccepted ? item.suggested_text : item.original_text}"
                  </p>
                  
                  {!isAccepted && !isDismissed && (
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
                  )}
                  {isAccepted && <span className="text-[10px] text-green-600 font-bold uppercase">Accepted</span>}
                  {isDismissed && <span className="text-[10px] text-slate-400 font-bold uppercase">Dismissed</span>}
                </button>

                {expandedId === index && !isAccepted && !isDismissed && (
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
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAcceptRedline(index);
                        }}
                        className="flex-1 bg-accent-blue text-white py-2 rounded text-xs font-bold hover:bg-blue-700 transition-colors shadow-sm"
                      >
                        Accept Redline
                      </button>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDismissRedline(index);
                        }}
                        className="flex-1 border border-slate-200 text-slate-700 py-2 rounded text-xs font-bold hover:bg-slate-50 transition-colors shadow-sm"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
