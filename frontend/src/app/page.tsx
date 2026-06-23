import Link from "next/link";
import { Shield, Zap, FileText, CheckCircle } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="bg-navy text-white py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 tracking-tight">
            Review contracts in <span className="text-accent-blue">minutes</span>, not days.
          </h1>
          <p className="text-xl md:text-2xl text-slate-300 mb-10 max-w-3xl mx-auto leading-relaxed">
            LexRedline turns the legal review bottleneck into a competitive advantage with AI-powered clause detection, risk scoring, and automated redlining.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link 
              href="/dashboard" 
              className="bg-accent-blue hover:bg-blue-700 text-white px-8 py-4 rounded-md font-bold text-lg transition-all shadow-lg"
            >
              Get Started for Free
            </Link>
            <Link 
              href="#features" 
              className="bg-transparent border border-slate-500 hover:bg-slate-800 text-white px-8 py-4 rounded-md font-bold text-lg transition-all"
            >
              Learn More
            </Link>
          </div>
        </div>
      </section>

      {/* Social Proof / Trusted By */}
      <section className="py-12 bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 font-medium uppercase tracking-widest text-sm">
          Trusted by mid-market firms and legal departments
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-navy mb-4">Powerful AI for Legal Professionals</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Our specialized engine understands legal language and identifies risks so you can focus on high-level strategy.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
              <div className="h-12 w-12 bg-blue-100 text-accent-blue rounded-lg flex items-center justify-center mb-6">
                <FileText size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3 text-navy">Clause Detection</h3>
              <p className="text-slate-600 leading-relaxed">
                Automatically identify 30+ clause types across NDAs, SaaS agreements, and service contracts with over 85% precision.
              </p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
              <div className="h-12 w-12 bg-amber-100 text-amber-600 rounded-lg flex items-center justify-center mb-6">
                <Shield size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3 text-navy">Risk Assessment</h3>
              <p className="text-slate-600 leading-relaxed">
                Instantly surface aggressive language and non-standard terms with our proprietary 4-tier risk scoring engine.
              </p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
              <div className="h-12 w-12 bg-green-100 text-green-600 rounded-lg flex items-center justify-center mb-6">
                <Zap size={24} />
              </div>
              <h3 className="text-xl font-bold mb-3 text-navy">Smart Redlining</h3>
              <p className="text-slate-600 leading-relaxed">
                Accept expert-vetted replacement language with one click to balance protection with speed-to-signature.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-navy mb-6">
            Ready to accelerate your contract review?
          </h2>
          <p className="text-xl text-slate-600 mb-10 leading-relaxed">
            Join the firms that are reducing their review time by over 75% while increasing consistency and compliance.
          </p>
          <Link 
            href="/dashboard" 
            className="inline-flex items-center gap-2 bg-navy hover:bg-slate-800 text-white px-8 py-4 rounded-md font-bold text-lg transition-all shadow-lg"
          >
            Access Dashboard <CheckCircle size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-12 px-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:row justify-between items-center gap-8">
          <div className="text-xl font-bold text-white">
            Lex<span className="text-accent-blue">Redline</span>
          </div>
          <div className="flex gap-8">
            <Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link>
            <Link href="/upload" className="hover:text-white transition-colors">Upload</Link>
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
