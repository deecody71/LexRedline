"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, Lock, Mail, User, Building } from "lucide-react";

export default function SignupPage() {
  const [formData, setFormData] = useState({
    fullName: "",
    company: "",
    email: "",
    password: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Logic for signup (to be implemented)
    window.location.href = "/dashboard";
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12 bg-slate-50">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-navy mb-2">Create Account</h1>
          <p className="text-slate-500">Start reviewing contracts with AI today</p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <User size={18} />
                </div>
                <input
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                  placeholder="John Doe"
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Company / Firm
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Building size={18} />
                </div>
                <input
                  type="text"
                  required
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                  placeholder="Lex Corp"
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail size={18} />
                </div>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="name@company.com"
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock size={18} />
                </div>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
                />
              </div>
              <p className="mt-1 text-[10px] text-slate-400">Must be at least 8 characters long.</p>
            </div>

            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="terms"
                  type="checkbox"
                  required
                  className="h-4 w-4 text-accent-blue focus:ring-accent-blue border-slate-300 rounded"
                />
              </div>
              <label htmlFor="terms" className="ml-2 block text-xs text-slate-600">
                I agree to the{" "}
                <Link href="#" className="text-accent-blue hover:underline">Terms of Service</Link>
                {" "}and{" "}
                <Link href="#" className="text-accent-blue hover:underline">Privacy Policy</Link>.
              </label>
            </div>

            <button
              type="submit"
              className="w-full bg-accent-blue hover:bg-blue-700 text-white py-3 rounded-lg font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200"
            >
              Create Account <ArrowRight size={18} />
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <p className="text-sm text-slate-600">
              Already have an account?{" "}
              <Link href="/login" className="text-accent-blue font-semibold hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
