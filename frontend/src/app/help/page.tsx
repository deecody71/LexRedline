"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, MessageSquare, BookOpen, ChevronRight, HelpCircle, Loader2 } from "lucide-react";
import { getHelpAnswer, HelpResponse } from "@/lib/api";

const FEATURED_FAQS = [
  {
    question: "What is LexRedline?",
    answer: "LexRedline is an AI-powered contract review engine that scans contracts, flags risky clauses, and suggests redlines in minutes instead of days."
  },
  {
    question: "How do I upload a contract?",
    answer: "Go to the Upload page, select a PDF or DOCX file from your computer, optionally add expectations about what you want to see in the contract, and click 'Analyze'. The analysis takes just seconds."
  },
  {
    question: "What file formats are supported?",
    answer: "LexRedline supports PDF (.pdf), Word (.docx), and plain text files. PDF files are parsed using PyMuPDF, and DOCX files using python-docx."
  }
];

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HelpResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await getHelpAnswer(searchQuery);
      setResult(response);
    } catch (err: any) {
      setError(err.message || "Failed to get help answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-navy mb-4">How can we help?</h1>
        <p className="text-slate-500 text-lg">Search our FAQ or ask a question about LexRedline.</p>
        
        <form onSubmit={handleSearch} className="mt-8 max-w-2xl mx-auto relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Ask a question (e.g., 'How do I export results?')"
            className="w-full px-6 py-4 rounded-full border border-slate-200 shadow-sm focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all pr-16"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-2 top-2 bottom-2 px-4 bg-accent-blue text-white rounded-full hover:bg-blue-700 transition-colors disabled:bg-slate-300"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
          </button>
        </form>
      </div>

      {result && (
        <div className="mb-12 bg-white rounded-2xl border border-blue-100 shadow-lg p-8 animate-in fade-in slide-in-from-top-4">
          <h2 className="text-sm font-bold text-accent-blue uppercase tracking-widest mb-4">Answer</h2>
          <div className="prose prose-slate max-w-none">
            <p className="text-lg text-slate-800 leading-relaxed">{result.answer}</p>
          </div>
          {result.source === 'faq' && (
            <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-xs text-slate-400">
              <HelpCircle className="w-3.5 h-3.5 mr-1" />
              Source: Built-in FAQ
            </div>
          )}
          {result.related_questions && result.related_questions.length > 0 && (
            <div className="mt-8 pt-6 border-t border-slate-100">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Related Questions</h3>
              <div className="space-y-3">
                {result.related_questions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setSearchQuery(q);
                      // In a real app we'd trigger handleSearch here, but state update is async
                    }}
                    className="flex items-center text-slate-600 hover:text-accent-blue transition-colors text-left"
                  >
                    <ChevronRight className="w-4 h-4 mr-2 text-accent-blue" />
                    <span>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mb-12 p-4 bg-red-50 border border-red-100 text-red-700 rounded-xl flex items-center gap-3">
          <HelpCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-8 mb-16">
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-blue-50 text-accent-blue rounded-xl flex items-center justify-center mb-6">
            <BookOpen className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-navy mb-2">User Guide</h2>
          <p className="text-slate-500 mb-6">Complete documentation on how to use LexRedline, from upload to export.</p>
          <Link href="/guide" className="text-accent-blue font-bold flex items-center hover:gap-2 transition-all">
            Read the guide <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-6">
            <MessageSquare className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-navy mb-2">AI Assistant</h2>
          <p className="text-slate-500 mb-6">Have a specific question about your contract analysis? Ask our AI expert.</p>
          <Link href="/dashboard" className="text-accent-blue font-bold flex items-center hover:gap-2 transition-all">
            Go to dashboard <ChevronRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      </div>

      <div className="mb-16">
        <h2 className="text-2xl font-bold text-navy mb-8">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {FEATURED_FAQS.map((faq, i) => (
            <div key={i} className="bg-white p-6 rounded-xl border border-slate-100">
              <h3 className="text-lg font-bold text-slate-800 mb-2">{faq.question}</h3>
              <p className="text-slate-600 leading-relaxed">{faq.answer}</p>
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <p className="text-slate-400">Can't find what you're looking for? Use the search bar above.</p>
        </div>
      </div>
    </div>
  );
}
