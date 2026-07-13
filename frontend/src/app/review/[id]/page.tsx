"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { ChevronRight, ChevronDown, AlertTriangle, CheckCircle, Info, ArrowRight, FileText, Trash2, Printer, Download, FileDown, Layers, Loader2 } from "lucide-react";
import { useAnalysis } from "@/context/AnalysisContext";
import { useUser } from "@clerk/nextjs";
import { useParams, useRouter } from "next/navigation";
import { SAMPLE_DATA } from "@/lib/sampleData";
import { getStoredContractById, StoredContract } from "@/lib/storage";
import { Document, Packer, Paragraph, TextRun } from "docx";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export default function ReviewPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user, isLoaded } = useUser();
  const { result: contextResult } = useAnalysis();
  const [result, setResult] = useState<any>(null);
  const [expandedId, setExpandedId] = useState<number | null>(0);
  const [acceptedRedlines, setAcceptedRedlines] = useState<Set<number>>(new Set());
  const [dismissedRedlines, setDismissedRedlines] = useState<Set<number>>(new Set());
  const [isExporting, setIsExporting] = useState(false);
  const textContainerRef = useRef<HTMLDivElement>(null);
  const annotatedContainerRef = useRef<HTMLDivElement>(null);

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

  // Document view for Annotated PDF (Accepted=Green, Pending=Yellow, Dismissed=Strikethrough)
  const annotatedSegments = useMemo(() => {
    if (!result) return [];
    
    let text = result.full_text;
    const segments: { text: string; type?: 'accepted' | 'pending' | 'dismissed'; index?: number }[] = [];
    
    const sortedRedlines = result.redlines
      .map((rl: any, idx: number) => ({ ...rl, originalIndex: idx, pos: text.indexOf(rl.original_text) }))
      .filter((rl: any) => rl.pos !== -1)
      .sort((a: any, b: any) => a.pos - b.pos);
    
    let lastIndex = 0;
    for (const rl of sortedRedlines) {
      if (rl.pos > lastIndex) {
        segments.push({ text: text.substring(lastIndex, rl.pos) });
      }
      
      const isAccepted = acceptedRedlines.has(rl.originalIndex);
      const isDismissed = dismissedRedlines.has(rl.originalIndex);
      
      if (isAccepted) {
        segments.push({ text: rl.suggested_text, type: 'accepted', index: rl.originalIndex });
      } else if (isDismissed) {
        segments.push({ text: rl.original_text, type: 'dismissed', index: rl.originalIndex });
      } else {
        segments.push({ text: rl.original_text, type: 'pending', index: rl.originalIndex });
      }
      
      lastIndex = rl.pos + rl.original_text.length;
    }
    
    if (lastIndex < text.length) {
      segments.push({ text: text.substring(lastIndex) });
    }
    
    return segments;
  }, [result, acceptedRedlines, dismissedRedlines]);

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

  const handleAnnotatedPDFExport = async () => {
    if (!result || !annotatedContainerRef.current) return;
    
    setIsExporting(true);
    try {
      const element = annotatedContainerRef.current;
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const finalWidth = imgWidth * ratio;
      const finalHeight = imgHeight * ratio;
      
      pdf.addImage(imgData, 'PNG', 0, 0, finalWidth, finalHeight);
      pdf.save(`LexRedline_Annotated_${result.filename.split('.')[0]}.pdf`);
    } catch (err) {
      console.error("Annotated PDF Export failed", err);
      alert("Failed to generate annotated PDF. Please try the basic print option.");
    } finally {
      setIsExporting(false);
    }
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

  const handleAdvancedWordExport = async () => {
    if (!result) return;
    
    setIsExporting(true);
    try {
      const children: any[] = [
        new Paragraph({
          children: [
            new TextRun({ text: "LexRedline Redlined Contract", bold: true, size: 32 }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun({ text: `Contract: ${result.filename}`, size: 24 }),
          ],
        }),
        new Paragraph({
          children: [
            new TextRun({ text: `Exported on: ${new Date().toLocaleString()}`, size: 20 }),
          ],
        }),
        new Paragraph({ text: "" }), // Spacer
      ];

      // Document processing
      let text = result.full_text;
      const sortedRedlines = result.redlines
        .map((rl: any, idx: number) => ({ ...rl, originalIndex: idx, pos: text.indexOf(rl.original_text) }))
        .filter((rl: any) => rl.pos !== -1)
        .sort((a: any, b: any) => a.pos - b.pos);

      let lastIndex = 0;
      const runChildren: any[] = [];
      
      for (const rl of sortedRedlines) {
        if (rl.pos > lastIndex) {
          runChildren.push(new TextRun({ text: text.substring(lastIndex, rl.pos) }));
        }

        const isAccepted = acceptedRedlines.has(rl.originalIndex);
        
        if (isAccepted) {
          // Word Track Changes Markup (Manual simulation)
          runChildren.push(new TextRun({ 
            text: rl.original_text, 
            strike: true,
            color: "FF0000" // Red for deletion
          }));
          runChildren.push(new TextRun({ 
            text: " " + rl.suggested_text, 
            bold: true,
            color: "00B050", // Green for insertion
            underline: {}
          }));
        } else {
          runChildren.push(new TextRun({ text: rl.original_text }));
        }

        lastIndex = rl.pos + rl.original_text.length;
      }

      if (lastIndex < text.length) {
        runChildren.push(new TextRun({ text: text.substring(lastIndex) }));
      }

      children.push(new Paragraph({ children: runChildren }));

      const doc = new Document({
        sections: [{
          properties: {},
          children: children,
        }],
      });

      const blob = await Packer.toBlob(doc);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `LexRedline_Redlined_${result.filename.split('.')[0]}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Word Export failed", err);
      alert("Failed to generate redlined Word document.");
    } finally {
      setIsExporting(false);
    }
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
    <div className="flex flex-col lg:flex-row h-auto lg:h-[calc(100vh-4rem)]">
      {/* Left Pane - Document View */}
      <div className="w-full lg:flex-1 overflow-y-auto bg-slate-100 p-4 min-h-[50vh] lg:min-h-full">
        <div className="bg-white shadow-lg border border-slate-200 rounded-sm p-4 sm:p-6 lg:p-8 font-serif leading-relaxed">
          <div className="flex justify-between items-center mb-4 pb-3 border-b border-slate-100">
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
            className="whitespace-pre-wrap font-serif text-base sm:text-lg text-black leading-8"
            style={{ color: '#000000 !important', fontSize: '18px' }}
          >
            {processedTextSegments.length > 0 ? (
              processedTextSegments.map((segment, i) => (
              <span 
                key={i} 
                className={segment.isAccepted ? "bg-green-100 text-green-900 px-1 rounded border-b border-green-300" : ""}
                data-original-text={segment.index !== undefined ? result.redlines[segment.index].original_text : undefined}
              >
                {segment.text}
              </span>
            ))
          ) : (
            <div className="text-black break-words" style={{ color: '#000000' }}>
              {result.full_text || "No contract text available."}
            </div>
          )}
          </div>
          
          <div className="mt-12 pt-8 border-t border-slate-200 text-slate-400 text-xs italic font-sans text-center">
            [END OF DOCUMENT]
          </div>
        </div>
      </div>

      {/* Right Pane - Annotations */}
      <div className="w-full lg:w-[450px] border-t lg:border-t-0 lg:border-l border-slate-200 bg-white overflow-y-auto">
                <div className="p-4 lg:p-6 border-b border-slate-200 bg-slate-50 sticky top-0 z-10">
                  <div className="flex justify-between items-center mb-1">
                    <h2 className="text-sm font-bold text-navy flex items-center">
                      <AlertTriangle className="w-3.5 h-3.5 text-risk-high mr-1.5" />
                      Analysis
                    </h2>
                    <div className="flex gap-0.5">
                      <button
                        onClick={handleExportPDF}
                        className="p-1 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded transition-colors"
                        title="Print Report"
                      >
                        <Printer className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={handleAnnotatedPDFExport}
                        className="p-1 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded transition-colors"
                        disabled={isExporting}
                        title="Annotated PDF"
                      >
                        {isExporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
                      </button>
                      <button
                        onClick={handleExportWord}
                        className="p-1 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded transition-colors"
                        title="Word Report"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={handleAdvancedWordExport}
                        className="p-1 text-slate-400 hover:text-accent-blue hover:bg-blue-50 rounded transition-colors"
                        disabled={isExporting}
                        title="Redlined Word Doc"
                      >
                        {isExporting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileDown className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-[10px] text-slate-500">{result.redlines.length} flagged</p>
                    <div className={`risk-badge ${
                      result.overall_risk === 'HIGH' ? 'risk-badge-high' :
                      result.overall_risk === 'MEDIUM' ? 'risk-badge-med' : 'risk-badge-low'
                    }`}>
                      {result.overall_risk}
                    </div>
                  </div>
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

      {/* Annotated Document View for PDF Export (Hidden) */}
      <div className="fixed -left-[9999px] top-0 no-print" aria-hidden="true">
        <div 
          ref={annotatedContainerRef}
          className="w-[800px] bg-white p-12 font-serif text-slate-800 leading-relaxed"
        >
          <div className="border-b-2 border-navy pb-4 mb-8">
            <h1 className="text-2xl font-bold text-navy">Annotated Contract: {result.filename}</h1>
            <p className="text-sm text-slate-500 mt-1 uppercase tracking-widest font-sans">
              LexRedline AI Analysis • {new Date().toLocaleDateString()}
            </p>
          </div>
          
          <div className="whitespace-pre-wrap text-base">
            {annotatedSegments.map((segment, i) => {
              let className = "px-0.5 rounded-sm ";
              if (segment.type === 'accepted') className += "bg-green-100 text-green-900 border-b border-green-300";
              if (segment.type === 'pending') className += "bg-yellow-100 text-yellow-900 border-b border-yellow-300";
              if (segment.type === 'dismissed') className += "line-through text-slate-400";
              
              return (
                <span key={i} className={className}>
                  {segment.text}
                </span>
              );
            })}
          </div>

          <div className="mt-12 pt-6 border-t border-slate-100 text-[10px] text-slate-400 text-center font-sans">
            LEGEND: <span className="bg-green-100 px-1 border-b border-green-300">Accepted Redline</span> | 
            <span className="bg-yellow-100 px-1 border-b border-yellow-300 ml-2">Pending Review</span> | 
            <span className="line-through ml-2">Dismissed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
