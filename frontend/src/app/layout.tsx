import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { AnalysisProvider } from "@/context/AnalysisContext";
import Header from "./Header";
import HelpWidget from "./HelpWidget";

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
    >
      <html lang="en">
        <body className={inter.className}>
          <AnalysisProvider>
            <Header />
            <main className="min-h-[calc(100vh-4rem)] bg-slate-50">
              {children}
            </main>
            <HelpWidget />
          </AnalysisProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}