import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LexRedline - AI Contract Review",
  description: "AI-powered contract review engine",
};

import { AnalysisProvider } from "@/context/AnalysisContext";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AnalysisProvider>
          <header className="bg-navy text-white shadow-md">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
              <div className="flex items-center space-x-8">
                <Link href="/" className="text-xl font-bold tracking-tight">
                  Lex<span className="text-accent-blue">Redline</span>
                </Link>
                <div className="hidden md:flex space-x-6">
                  <Link href="/dashboard" className="hover:text-blue-300 transition-colors">
                    Dashboard
                  </Link>
                  <Link href="/upload" className="hover:text-blue-300 transition-colors">
                    Upload
                  </Link>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Link href="/login" className="text-sm font-medium hover:text-blue-300 transition-colors">
                  Sign In
                </Link>
                <Link 
                  href="/signup" 
                  className="bg-accent-blue hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-bold transition-all"
                >
                  Get Started
                </Link>
              </div>
            </nav>
          </header>
          <main className="min-h-[calc(100vh-4rem)] bg-slate-50">
            {children}
          </main>
        </AnalysisProvider>
      </body>
    </html>
  );
}
