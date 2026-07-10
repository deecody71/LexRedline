import Link from "next/link";
import { ChevronLeft, Upload, Shield, Target, User, Download, HelpCircle } from "lucide-react";

export default function UserGuidePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="mb-12">
        <Link href="/help" className="text-accent-blue flex items-center hover:underline mb-8">
          <ChevronLeft className="w-4 h-4 mr-1" /> Back to Help
        </Link>
        <h1 className="text-4xl font-bold text-navy">User Guide</h1>
        <p className="text-slate-500 mt-2">Master LexRedline with our comprehensive guide.</p>
      </div>

      <div className="space-y-16">
        <section id="upload">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-blue-100 text-accent-blue rounded-lg flex items-center justify-center">
              <Upload className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-bold text-navy">How to upload a contract</h2>
          </div>
          <div className="prose prose-slate max-w-none text-slate-600">
            <p>LexRedline makes it easy to analyze your contracts in seconds. Follow these steps:</p>
            <ol className="list-decimal pl-6 space-y-2 mt-4">
              <li>Navigate to the <strong>Upload</strong> page.</li>
              <li>Drag and drop your file (PDF, DOCX, or TXT) into the upload area, or click to browse your computer.</li>
              <li>Give your contract a name for easy reference in your dashboard.</li>
              <li>(Optional) Add your <strong>Expectations</strong> to tell the AI what you're looking for.</li>
              <li>Click <strong>Start Review</strong> and wait for the analysis to complete.</li>
            </ol>
          </div>
        </section>

        <section id="risk-scores">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-red-100 text-risk-high rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-bold text-navy">Understanding Risk Scores</h2>
          </div>
          <div className="prose prose-slate max-w-none text-slate-600">
            <p>Our engine categorizes clauses into four distinct risk levels based on market standards and legal best practices:</p>
            <div className="grid sm:grid-cols-2 gap-4 mt-6">
              <div className="p-4 bg-green-50 border border-green-100 rounded-xl">
                <span className="text-xs font-bold text-green-600 uppercase tracking-widest">Low Risk</span>
                <p className="text-sm mt-1">Standard language with no major concerns. Typical for market-standard agreements.</p>
              </div>
              <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl">
                <span className="text-xs font-bold text-amber-600 uppercase tracking-widest">Medium Risk</span>
                <p className="text-sm mt-1">Contains language that deviates slightly from standard terms or needs clarification.</p>
              </div>
              <div className="p-4 bg-red-50 border border-red-100 rounded-xl">
                <span className="text-xs font-bold text-red-600 uppercase tracking-widest">High Risk</span>
                <p className="text-sm mt-1">Aggressive language that could create significant liability or unfavorable obligations.</p>
              </div>
              <div className="p-4 bg-red-900/5 border border-red-900/10 rounded-xl">
                <span className="text-xs font-bold text-red-900 uppercase tracking-widest">Critical Risk</span>
                <p className="text-sm mt-1">Highly one-sided terms that are often non-standard and require immediate attention.</p>
              </div>
            </div>
          </div>
        </section>

        <section id="expectations">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-bold text-navy">Using Expectations</h2>
          </div>
          <div className="prose prose-slate max-w-none text-slate-600">
            <p>Expectations allow you to guide the AI toward what you specifically need in a contract. For example:</p>
            <blockquote className="border-l-4 border-purple-200 pl-4 py-2 italic bg-purple-50 rounded-r-lg mt-4">
              "Must include mutual indemnification, 30-day notice for termination, and New York governing law."
            </blockquote>
            <p className="mt-4">The engine will parse your request and provide an <strong>Expectation Match Score</strong>, showing you exactly what was found and what is missing.</p>
          </div>
        </section>

        <section id="profile">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-slate-100 text-slate-600 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-bold text-navy">Profile Preferences</h2>
          </div>
          <div className="prose prose-slate max-w-none text-slate-600">
            <p>Set up your profile to tell LexRedline who you are and what you care about. We use this to tailor the risk analysis:</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Reviewer:</strong> Focused on spotting risks in incoming contracts from third parties.</li>
              <li><strong>Creator:</strong> Focused on ensuring your own outgoing contracts are fair and standard.</li>
              <li><strong>Both:</strong> A balanced approach for versatile legal teams.</li>
            </ul>
            <p className="mt-4">You can also select specific focus areas like <strong>Liability & Financial Caps</strong> or <strong>Data Privacy</strong>.</p>
          </div>
        </section>

        <section id="export">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-10 h-10 bg-accent-blue/10 text-accent-blue rounded-lg flex items-center justify-center">
              <Download className="w-5 h-5" />
            </div>
            <h2 className="text-2xl font-bold text-navy">Exporting Results</h2>
          </div>
          <div className="prose prose-slate max-w-none text-slate-600">
            <p>Once your review is complete, you can export the findings to share with your team or use in negotiations:</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>PDF:</strong> A professional report containing the summary, risk scores, and detailed analysis.</li>
              <li><strong>Word:</strong> A document you can open in Microsoft Word to use as a starting point for your manual redlines.</li>
            </ul>
            <p className="mt-4">Look for the export buttons in the top header of the <strong>Review Page</strong>.</p>
          </div>
        </section>

        <section id="faq-link" className="pt-8 border-t border-slate-100 text-center">
          <HelpCircle className="w-12 h-12 text-slate-200 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-navy mb-2">Still have questions?</h2>
          <p className="text-slate-500 mb-6">Our FAQ section covers more specific technical and billing questions.</p>
          <Link href="/help" className="btn-primary inline-flex items-center">
            Go to FAQ
          </Link>
        </section>
      </div>
    </div>
  );
}
