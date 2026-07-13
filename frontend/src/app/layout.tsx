import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { AnalysisProvider } from "@/context/AnalysisContext";
import Header from "./Header";
import HelpWidget from "./HelpWidget";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LexRedline - AI Contract Review",
  description: "AI-powered contract review engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      signInFallbackRedirectUrl="/dashboard"
      signUpFallbackRedirectUrl="/dashboard"
      signInForceRedirectUrl="/dashboard"
      signUpForceRedirectUrl="/dashboard"
    >
      <html lang="en">
        <body className={inter.className}>
          <AnalysisProvider>
            <Header />
            <main className="min-h-[calc(100vh-4rem)] bg-slate-50">
              {children}
            </main>
            <footer className="bg-navy text-slate-400 text-xs py-6 px-4">
              <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
                <p>© {new Date().getFullYear()} LexRedline. AI-powered contract analysis.</p>
                <div className="flex items-center gap-4">
                  <Link href="/terms" className="hover:text-white transition-colors">Terms & Disclaimer</Link>
                  <Link href="/help" className="hover:text-white transition-colors">Help</Link>
                </div>
              </div>
            </footer>
            <HelpWidget />
          </AnalysisProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}