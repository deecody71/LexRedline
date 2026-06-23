import Link from "next/link";
import { Shield, Zap, FileText, CheckCircle, ArrowRight, UserPlus, Users, Search, Edit3 } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="bg-navy text-white py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 tracking-tight">
            AI-Powered <span className="text-accent-blue">Contract Review</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 mb-10 max-w-3xl mx-auto leading-relaxed">
            LexRedline turns the legal review bottleneck into a speed advantage. Scan contracts, flag risky clauses, and generate redlines in minutes instead of days.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link 
              href="/signup" 
              className="bg-accent-blue hover:bg-blue-700 text-white px-8 py-4 rounded-md font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2"
            >
              Try It Now <ArrowRight size={20} />
            </Link>
            <Link 
              href="/signup" 
              className="bg-white text-navy hover:bg-slate-100 px-8 py-4 rounded-md font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2"
            >
              Upload Your First Contract
            </Link>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-16 items-start">
            {/* For Contract Creators */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 text-accent-blue font-bold uppercase tracking-wider text-sm">
                <UserPlus size={18} /> For Contract Creators
              </div>
              <h2 className="text-3xl font-bold text-navy">Draft faster with confidence</h2>
              <p className="text-lg text-slate-600">
                Accelerate your deal flow by automating the tedious parts of drafting and review.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Faster Turnaround:</strong> Cut review time by 75% without sacrificing quality.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Consistent Clause Libraries:</strong> Ensure standard language across all your agreements.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Reduced Liability Risk:</strong> Catch non-standard terms before they become problems.</span>
                </li>
              </ul>
            </div>

            {/* For Contract Signers */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 text-amber-600 font-bold uppercase tracking-wider text-sm">
                <Users size={18} /> For Contract Signers
              </div>
              <h2 className="text-3xl font-bold text-navy">Know exactly what you're signing</h2>
              <p className="text-lg text-slate-600">
                Protect your interests by instantly surfacing risks in contracts provided by third parties.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Understand Every Clause:</strong> Get plain-English explanations of complex legal terms.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Flag Hidden Risks:</strong> AI-powered detection surfaces "silent" dangers in fine print.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-green-100 text-green-600 rounded-full p-1"><CheckCircle size={16} /></div>
                  <span className="text-slate-700"><strong>Negotiate Better Terms:</strong> Use data-driven insights to push back on aggressive clauses.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-slate-50 border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-navy mb-4">How It Works</h2>
            <p className="text-lg text-slate-600">The most advanced legal AI, simplified into three steps.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-white border-2 border-accent-blue/20 rounded-full flex items-center justify-center mx-auto text-accent-blue shadow-sm">
                <FileText size={32} />
              </div>
              <h3 className="text-xl font-bold text-navy">1. Upload</h3>
              <p className="text-slate-600 leading-relaxed">
                Drop your PDF or DOCX contract into our secure analyzer. We support NDAs, SaaS, Service Agreements, and more.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-white border-2 border-accent-blue/20 rounded-full flex items-center justify-center mx-auto text-accent-blue shadow-sm">
                <Search size={32} />
              </div>
              <h3 className="text-xl font-bold text-navy">2. AI Analysis</h3>
              <p className="text-slate-600 leading-relaxed">
                Our engine scans for 33+ clause types and scores risk levels against market standards in under 5 milliseconds.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-20 h-20 bg-white border-2 border-accent-blue/20 rounded-full flex items-center justify-center mx-auto text-accent-blue shadow-sm">
                <Edit3 size={32} />
              </div>
              <h3 className="text-xl font-bold text-navy">3. Review & Accept</h3>
              <p className="text-slate-600 leading-relaxed">
                Review AI-detected risks and accept suggested redlines with a single click to finalize your document.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-navy rounded-2xl p-12 text-white overflow-hidden relative">
            <div className="relative z-10 grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold mb-6">Unrivaled Legal Intelligence</h2>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <div className="text-4xl font-bold text-accent-blue mb-1">33+</div>
                    <div className="text-slate-300">Clause Types Detected</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-accent-blue mb-1">5ms</div>
                    <div className="text-slate-300">Analysis Time</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-accent-blue mb-1">85%</div>
                    <div className="text-slate-300">Detection Accuracy</div>
                  </div>
                  <div>
                    <div className="text-4xl font-bold text-accent-blue mb-1">4-Tier</div>
                    <div className="text-slate-300">Risk Scoring</div>
                  </div>
                </div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                   <Zap className="text-yellow-400" size={20} /> Smart Redline Suggestions
                </h3>
                <p className="text-slate-300 mb-6 leading-relaxed">
                  Our system doesn't just find problems—it solves them. LexRedline provides expert-vetted replacement language that balances legal protection with commercial speed.
                </p>
                <div className="space-y-2">
                  <div className="h-2 w-full bg-white/20 rounded-full overflow-hidden">
                    <div className="h-full bg-accent-blue w-full"></div>
                  </div>
                  <div className="h-2 w-3/4 bg-white/20 rounded-full overflow-hidden">
                    <div className="h-full bg-accent-blue w-full"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-slate-50 border-t border-slate-200">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-navy mb-6">
            Ready to accelerate your contract review?
          </h2>
          <p className="text-xl text-slate-600 mb-10 leading-relaxed">
            Join the firms that are reducing their review time by over 75% while increasing consistency and compliance.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link 
              href="/signup" 
              className="bg-navy hover:bg-slate-800 text-white px-8 py-4 rounded-md font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2"
            >
              Access Dashboard <CheckCircle size={20} />
            </Link>
            <Link 
              href="/signup" 
              className="bg-transparent border border-navy text-navy hover:bg-navy hover:text-white px-8 py-4 rounded-md font-bold text-lg transition-all flex items-center justify-center gap-2"
            >
              Start Uploading
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 px-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:row justify-between items-center gap-8">
          <div className="text-xl font-bold text-white">
            Lex<span className="text-accent-blue">Redline</span>
          </div>
          <div className="flex gap-8">
            <Link href="/login" className="hover:text-white transition-colors">Sign In</Link>
            <Link href="/signup" className="hover:text-white transition-colors">Sign Up</Link>
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
          <div className="text-sm">
            &copy; 2026 LexRedline AI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
