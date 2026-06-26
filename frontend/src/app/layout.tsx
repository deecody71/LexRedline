import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import Header from "./Header";

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
        <ClerkProvider>
          <AnalysisProvider>
            <Header />
            <main className="min-h-[calc(100vh-4rem)] bg-slate-50">
              {children}
            </main>
          </AnalysisProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
