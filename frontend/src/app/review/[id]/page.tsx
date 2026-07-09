"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { ChevronRight, ChevronDown, AlertTriangle, CheckCircle, Info, ArrowRight, FileText, Trash2, Printer, Download } from "lucide-react";
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
      } else if (!(user.publicMetadata as any)?.profile) {
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
    if (!result) return;
    
    const htmlContent = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset='utf-8'><title>Analysis Report - ${result.filename}</title>
      <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #334155; }
        .header { border-bottom: 2px solid #1e293b; padding-bottom: 10px; margin-bottom: 20px; }
        .title { font-size: 24pt; font-weight: bold; color: #1e293b; margin-bottom: 5px; }
        .meta { font-size: 10pt; color: #64748b; }
        .section { margin-bottom: 30px; }
        .section-title { font-size: 16pt; font-weight: bold; color: #2563eb; border-bottom: 1px solid #e2e8f0; margin-bottom: 15px; padding-bottom: 5px; }
        .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 9999px; font-size: 10pt; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
        .risk-high { background: #fef2f2; color: #ef4444; border: 1px solid #fee2e2; }
        .risk-med { background: #fffbeb; color: #f59e0b; border: 1px solid #fef3c7; }
        .risk-low { background: #f0fdf4; color: #22c55e; border: 1px solid #dcfce7; }
        .clause { margin-bottom: 20px; padding: 15px; background: #f8fafc; border-left: 4px solid #cbd5e1; border-radius: 0 4px 4px 0; }
        .clause-title { font-weight: bold; text-transform: uppercase; font-size: 11pt; color: #1e293b; margin-bottom: 5px; }
        .priority { font-size: 9pt; color: #64748b; font-weight: normal; margin-left: 10px; }
        .reason { font-size: 10pt; color: #475569; margin: 10px 0; }
        .redline-box { background: white; border: 1px solid #e2e8f0; padding: 10px; border-radius: 4px; margin-top: 10px; }
        .label { font-size: 8pt; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px; }
        .original { color: #64748b; text-decoration: line-through; }
        .suggested { color: #2563eb; font-weight: bold; }
        .match-score { font-size: 18pt; font-weight: bold; color: #2563eb; }
        .list { margin: 10px 0; padding-left: 20px; }
        .list-item { margin-bottom: 5px; font-size: 10pt; }
        .recommendations { background: #eff6ff; padding: 15px; border-radius: 8px; border: 1px solid #dbeafe; }
      </style>
      </head>
      <body>
        <div class="header">
          <div class="title">LexRedline Analysis Report</div>
          <div class="meta">
            <strong>Contract:</strong> ${result.filename}<br>
            <strong>Date Analyzed:</strong> ${new Date(result.parsed_at || Date.now()).toLocaleString()}<br>
            <strong>Overall Risk Level:</strong> <span class="risk-${result.overall_risk.toLowerCase()}">${result.overall_risk}</span>
          </div>
        </div>

        ${result.expectation_match ? `
        <div class="section">
          <div class="section-title">Contract Expectations Match</div>
          <div class="match-score">${result.expectation_match.match_percentage}% Match</div>
          
          <div class="label">Met Expectations</div>
          <ul class="list">
            ${result.expectation_match.matched.map((item: string) => `<li class="list-item">✅ ${item}</li>`).join('')}
          </ul>

          <div class="label">Missing / Concerns</div>
          <ul class="list">
            ${result.expectation_match.unmatched.map((item: string) => `<li class="list-item">❌ ${item}</li>`).join('')}
          </ul>

          <div class="recommendations">
            <div class="label" style="color: #2563eb">AI Recommendations</div>
            <ul class="list" style="margin-bottom: 0">
              ${result.expectation_match.recommendations.map((item: string) => `<li class="list-item" style="color: #1e40af">• ${item}</li>`).join('')}
            </ul>
          </div>
        </div>
        ` : ''}

        <div class="section">
          <div class="section-title">Detailed Risk Analysis</div>
          ${result.redlines.map((rl: any) => `
            <div class="clause">
              <div class="clause-title">
                ${rl.clause_type.replace(/_/g, ' ')}
                <span class="priority">Priority ${rl.priority}</span>
              </div>
              <div class="reason"><strong>Issue:</strong> ${rl.risk_reason}</div>
              <div class="redline-box">
                <div class="label">Current Text</div>
                <div class="original">${rl.original_text}</div>
                <div class="label" style="margin-top: 10px">Suggested Redline</div>
                <div class="suggested">${rl.suggested_text}</div>
              </div>
            </div>
          `).join('')}
        </div>

        <div style="margin-top: 50px; font-size: 8pt; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 20px;">
          This report was generated by LexRedline AI. It is intended for informational purposes and does not constitute legal advice.
        </div>
      </body>
      </html>
    `;

    const blob = new Blob(['\ufeff', htmlContent], {
      type: 'application/msword'
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `LexRedline_Analysis_${result.filename.split('.')[0]}.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
      <div className="flex-1 overflow-y-auto bg-slate-100 p-8 no-print">
        <div className="max-w-3xl mx-auto bg-white shadow-lg border border-slate-200 rounded-sm p-12 min-h-full font-serif text-slate-800 leading-relaxed">
          <div className="flex justify-between items-center mb-8 pb-4 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-accent-blue" />
              <span className="text-sm font-bold text-slate-500 uppercase tracking-widest">{result.filename}</span>
            </div>
            <span className="text-xs text-slate-400 font-sans tracking-tighter">Parsed at: {result.parsed_at ? new Date(result.parsed_at).toLocaleString() : 'N/A'}</span>
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
      <div className="w-[450px] border-l border-slate-200 bg-white overflow-y-auto no-print">
        <div className="p-6 border-b border-slate-200 bg-slate-50 sticky top-0 z-10">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-navy flex items-center">
              <AlertTriangle className="w-5 h-5 text-risk-high mr-2" />
              Risk Analysis
            </h2>
            <div className="flex gap-2">
              <button 
                onClick={handleExportPDF}
                className="p-1.5 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded-md transition-colors"
                title="Export PDF (Print)"
              >
                <Printer className="w-4 h-4" />
              </button>
              <button 
                onClick={handleExportWord}
                className="p-1.5 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded-md transition-colors"
                title="Export Word"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="flex justify-between items-center">
            <p className="text-xs text-slate-500">Detected {result.redlines.length} items requiring review</p>
            <div className={`risk-badge ${
              result.overall_risk === 'HIGH' ? 'risk-badge-high' : 
              result.overall_risk === 'MEDIUM' ? 'risk-badge-med' : 'risk-badge-low'
            }`}>
              Overall: {result.overall_risk}
            </div>
          </div>
        </div>

        {result.expectation_match && (
          <div className="p-6 border-b border-slate-200 bg-white">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-base font-bold text-navy flex items-center">
                <CheckCircle className="w-5 h-5 text-accent-blue mr-2" />
                Expectation Match
              </h2>
              <div className={`risk-badge ${
                result.expectation_match.match_percentage >= 80 ? 'risk-badge-low' : 
                result.expectation_match.match_percentage >= 50 ? 'risk-badge-med' : 'risk-badge-high'
              }`}>
                {result.expectation_match.match_percentage}% Match
              </div>
            </div>

            <div className="space-y-4">
              {result.expectation_match.matched.length > 0 && (
                <div>
                  <h3 className="text-[10px] font-bold text-green-600 uppercase tracking-widest mb-2 flex items-center">
                    ✅ Met Expectations
                  </h3>
                  <ul className="space-y-1.5">
                    {result.expectation_match.matched.map((item: string, i: number) => (
                      <li key={i} className="text-xs text-slate-700 flex items-start gap-2">
                        <span className="text-green-500 mt-0.5">•</span> {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.expectation_match.unmatched.length > 0 && (
                <div>
                  <h3 className="text-[10px] font-bold text-risk-high uppercase tracking-widest mb-2 flex items-center">
                    ❌ Missing / Needs Attention
                  </h3>
                  <ul className="space-y-1.5">
                    {result.expectation_match.unmatched.map((item: string, i: number) => (
                      <li key={i} className="text-xs text-slate-700 flex items-start gap-2">
                        <span className="text-risk-high mt-0.5">•</span> {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.expectation_match.recommendations.length > 0 && (
                <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
                  <h4 className="text-[11px] font-bold text-accent-blue mb-2 flex items-center">
                    <Info className="w-3.5 h-3.5 mr-1" /> Recommendations
                  </h4>
                  <ul className="space-y-1.5">
                    {result.expectation_match.recommendations.map((item: string, i: number) => (
                      <li key={i} className="text-[11px] text-slate-700 leading-tight flex items-start gap-2">
                        <ArrowRight className="w-3 h-3 text-accent-blue mt-0.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
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

      {/* Printable Report (hidden on screen) */}
      <div className="print-only p-8 bg-white text-slate-900">
        <div className="border-b-2 border-navy pb-4 mb-8">
          <h1 className="text-3xl font-bold text-navy">LexRedline Analysis Report</h1>
          <div className="mt-2 text-sm text-slate-600">
            <p><strong>Contract:</strong> {result.filename}</p>
            <p><strong>Date Analyzed:</strong> {new Date(result.parsed_at || Date.now()).toLocaleString()}</p>
            <p><strong>Overall Risk:</strong> {result.overall_risk}</p>
          </div>
        </div>

        {result.expectation_match && (
          <div className="mb-10">
            <h2 className="text-xl font-bold text-accent-blue border-b border-slate-200 mb-4 pb-2">Contract Expectations Match</h2>
            <div className="text-2xl font-bold text-accent-blue mb-4">{result.expectation_match.match_percentage}% Match</div>
            
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Met Expectations</h3>
                <ul className="space-y-1">
                  {result.expectation_match.matched.map((item: string, i: number) => (
                    <li key={i} className="text-sm text-slate-700">✅ {item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Missing / Concerns</h3>
                <ul className="space-y-1">
                  {result.expectation_match.unmatched.map((item: string, i: number) => (
                    <li key={i} className="text-sm text-slate-700">❌ {item}</li>
                  ))}
                </ul>
              </div>
            </div>

            {result.expectation_match.recommendations.length > 0 && (
              <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h3 className="text-sm font-bold text-accent-blue uppercase tracking-wider mb-2">AI Recommendations</h3>
                <ul className="space-y-1">
                  {result.expectation_match.recommendations.map((item: string, i: number) => (
                    <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                      <span className="text-accent-blue">•</span> {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div>
          <h2 className="text-xl font-bold text-accent-blue border-b border-slate-200 mb-6 pb-2">Identified Risks & Redlines</h2>
          <div className="space-y-8">
            {result.redlines.map((item: any, i: number) => (
              <div key={i} className="bg-slate-50 border-l-4 border-slate-300 p-6 rounded-r-lg" style={{ pageBreakInside: 'avoid' }}>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-navy uppercase">{item.clause_type.replace(/_/g, ' ')}</h3>
                  <span className="text-xs font-bold px-2 py-1 bg-white border border-slate-200 rounded">PRIORITY {item.priority}</span>
                </div>
                <p className="text-sm text-slate-700 mb-4"><strong>Issue:</strong> {item.risk_reason}</p>
                <div className="grid grid-cols-1 gap-4 mt-4">
                  <div className="bg-white p-4 border border-slate-200 rounded">
                    <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Current Text</span>
                    <p className="text-sm text-slate-500 italic line-through">"{item.original_text}"</p>
                  </div>
                  <div className="bg-white p-4 border border-blue-200 rounded border-l-4 border-l-accent-blue">
                    <span className="text-[10px] font-bold text-accent-blue uppercase block mb-1">Suggested Redline</span>
                    <p className="text-sm text-slate-800 font-medium">"{item.suggested_text}"</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-20 pt-8 border-t border-slate-100 text-center text-[10px] text-slate-400">
          This report was generated by LexRedline AI. It is intended for informational purposes and does not constitute legal advice.
        </div>
      </div>
    </div>
  );
}
