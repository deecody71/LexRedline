"use client";

import { useClerk, SignOutButton } from "@clerk/nextjs";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";

export default function Header() {
  const { user } = useClerk();
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setIsSignedIn(!!user);
  }, [user]);

  const navLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/upload", label: "Upload" },
    { href: "/profile", label: "Profile" },
    { href: "/help", label: "Help" },
  ];

  return (
    <header className="bg-navy text-white shadow-md">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="text-xl font-bold tracking-tight" onClick={() => setMobileOpen(false)}>
            Lex<span className="text-accent-blue">Redline</span>
          </Link>
          <div className="hidden md:flex space-x-6">
            {navLinks.map(link => (
              <Link key={link.href} href={link.href} className="hover:text-blue-300 transition-colors">{link.label}</Link>
            ))}
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {isSignedIn ? (
            <div className="flex items-center gap-2 sm:gap-4">
              <span className="hidden sm:inline text-sm font-medium text-slate-300">
                {(user?.unsafeMetadata as any)?.profile?.screenName || user?.firstName || "User"}
              </span>
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden p-2 hover:bg-navy/80 rounded"
                aria-label="Toggle menu"
              >
                {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              <SignOutButton>
                <button className="bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded text-xs font-bold transition-colors">
                  Sign Out
                </button>
              </SignOutButton>
            </div>
          ) : (
            <>
              <Link href="/sign-up" className="bg-accent-blue hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-bold transition-colors">Get Started</Link>
              <Link href="/sign-in" className="text-white hover:text-blue-300 px-3 py-2 text-sm font-medium transition-colors">Sign In</Link>
            </>
          )}
        </div>
      </nav>

      {/* Mobile menu */}
      {isSignedIn && mobileOpen && (
        <div className="md:hidden bg-navy border-t border-slate-700">
          <div className="px-4 py-3 space-y-1">
            {navLinks.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className="block px-3 py-2.5 text-white hover:bg-navy/80 rounded text-sm font-medium transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <div className="pt-2 pb-1 border-t border-slate-700 mt-2">
              <span className="block px-3 py-1 text-xs text-slate-400">
                Signed in as {user?.firstName || "User"}
              </span>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
