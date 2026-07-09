"use client";

import { useClerk, SignOutButton } from "@clerk/nextjs";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Header() {
  const { user } = useClerk();
  const [isSignedIn, setIsSignedIn] = useState(false);

  useEffect(() => {
    setIsSignedIn(!!user);
  }, [user]);

  return (
    <header className="bg-navy text-white shadow-md">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/" className="text-xl font-bold tracking-tight">
            Lex<span className="text-accent-blue">Redline</span>
          </Link>
          <div className="hidden md:flex space-x-6">
            <Link href="/dashboard" className="hover:text-blue-300 transition-colors">Dashboard</Link>
            <Link href="/upload" className="hover:text-blue-300 transition-colors">Upload</Link>
            <Link href="/profile" className="hover:text-blue-300 transition-colors">Profile</Link>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {isSignedIn ? (
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-slate-300">
                {(user?.unsafeMetadata as any)?.profile?.screenName || user?.firstName || "User"}
              </span>
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
    </header>
  );
}
