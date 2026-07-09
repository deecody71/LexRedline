"use client";

import { useState, useEffect } from "react";
import { HelpCircle, X, Search, MessageSquare, Send, Loader2, ChevronRight } from "lucide-react";
import { getHelpAnswer, askQuestion, HelpResponse, QAResponse } from "@/lib/api";
import { usePathname } from "next/navigation";

export default function HelpWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setOpenMode] = useState<'search' | 'qa'>('search');
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HelpResponse | QAResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pathname = usePathname();

  // Close widget on navigation
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  const handleHelpSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    try {
      if (mode === 'search') {
        const res = await getHelpAnswer(query);
        setResult(res);
      } else {
        // Find analysis ID from URL if on review page
        const analysisId = pathname.startsWith('/review/') ? pathname.split('/').pop() : undefined;
        const res = await askQuestion(query, analysisId);
        setResult(res);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const toggleWidget = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setResult(null);
      setQuery("");
      setError(null);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen ? (
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-80 md:w-96 overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="bg-navy p-4 text-white flex justify-between items-center">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-accent-blue" />
              <span className="font-bold">LexRedline Help</span>
            </div>
            <button onClick={toggleWidget} className="hover:bg-white/10 p-1 rounded-full transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-slate-100">
            <button 
              onClick={() => { setOpenMode('search'); setResult(null); }}
              className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-colors ${mode === 'search' ? 'text-accent-blue border-b-2 border-accent-blue' : 'text-slate-400 hover:text-slate-600'}`}
            >
              <Search className="w-3.5 h-3.5" /> Search FAQ
            </button>
            <button 
              onClick={() => { setOpenMode('qa'); setResult(null); }}
              className={`flex-1 py-3 text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-colors ${mode === 'qa' ? 'text-accent-blue border-b-2 border-accent-blue' : 'text-slate-400 hover:text-slate-600'}`}
            >
              <MessageSquare className="w-3.5 h-3.5" /> AI Assistant
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 max-h-[400px] min-h-[200px] bg-slate-50">
            {!result && !loading && !error && (
              <div className="text-center py-8">
                <div className="w-12 h-12 bg-white rounded-full shadow-sm flex items-center justify-center mx-auto mb-4">
                  {mode === 'search' ? <Search className="w-6 h-6 text-slate-300" /> : <MessageSquare className="w-6 h-6 text-slate-300" />}
                </div>
                <p className="text-sm text-slate-500 px-4">
                  {mode === 'search' 
                    ? "Search our knowledge base for quick answers about LexRedline." 
                    : "Ask our AI specific questions about contract review or your results."}
                </p>
              </div>
            )}

            {loading && (
              <div className="flex flex-col items-center justify-center py-12 gap-3 text-slate-400">
                <Loader2 className="w-8 h-8 animate-spin text-accent-blue" />
                <p className="text-xs font-medium">Thinking...</p>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-xs text-center">
                {error}
              </div>
            )}

            {result && !loading && (
              <div className="animate-in fade-in slide-in-from-top-2">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                  <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">
                    {mode === 'search' ? 'Answer' : 'AI Assistant'}
                  </h4>
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {(result as any).answer}
                  </p>
                </div>
                
                {mode === 'search' && (result as HelpResponse).related_questions?.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 px-1">Related</h4>
                    <div className="space-y-1">
                      {(result as HelpResponse).related_questions.map((q, i) => (
                        <button 
                          key={i}
                          onClick={() => { setQuery(q); }}
                          className="w-full text-left p-2 text-xs text-slate-600 hover:text-accent-blue hover:bg-white rounded transition-colors flex items-center group"
                        >
                          <ChevronRight className="w-3 h-3 mr-1 text-slate-300 group-hover:text-accent-blue" />
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                <button 
                  onClick={() => { setResult(null); setQuery(""); }}
                  className="mt-6 w-full py-2 text-xs text-slate-400 hover:text-slate-600 transition-colors"
                >
                  Ask another question
                </button>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-100 bg-white">
            <form onSubmit={handleHelpSearch} className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={mode === 'search' ? "Search help..." : "Ask AI a question..."}
                className="w-full pl-4 pr-10 py-2.5 bg-slate-100 border-none rounded-lg text-sm focus:ring-2 focus:ring-accent-blue transition-all"
              />
              <button 
                type="submit"
                disabled={loading || !query.trim()}
                className="absolute right-2 top-1.5 bottom-1.5 px-2 text-accent-blue hover:text-blue-700 disabled:text-slate-300 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      ) : (
        <button
          onClick={toggleWidget}
          className="bg-accent-blue hover:bg-blue-700 text-white w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110 active:scale-95 group"
          title="Open Help"
        >
          <HelpCircle className="w-7 h-7" />
          <span className="absolute right-full mr-4 bg-navy text-white text-xs font-bold py-2 px-4 rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap">
            How can we help?
          </span>
        </button>
      )}
    </div>
  );
}
