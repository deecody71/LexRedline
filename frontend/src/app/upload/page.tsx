"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@clerk/nextjs";
import { Upload as UploadIcon, File, X, Check, AlertCircle } from "lucide-react";
import { analyzeFile } from "@/lib/api";
import { useAnalysis } from "@/context/AnalysisContext";
import { saveAnalysisResult } from "@/lib/storage";

export default function UploadPage() {
  const { user, isLoaded } = useUser();
  const [file, setFile] = useState<File | null>(null);
  const [contractName, setContractName] = useState("");
  const [expectations, setExpectations] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const { setResult } = useAnalysis();

  useEffect(() => {
    if (isLoaded) {
      if (!user) {
        router.push("/sign-up");
      } else if (!(user.unsafeMetadata as any)?.profile && !localStorage.getItem("lexredline_profile_complete")) {
        router.push("/profile");
      }
    }
  }, [user, isLoaded, router]);

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-blue"></div>
      </div>
    );
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      if (!contractName) {
        setContractName(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    
    try {
      const result = await analyzeFile(file, expectations);
      saveAnalysisResult(contractName || file.name, result);
      setResult(result);
      router.push(`/review/${result.job_id}`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred during upload. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-navy mb-2">Upload Contract</h1>
        <p className="text-slate-500">
          Upload your legal document for AI-powered risk analysis and redlining suggestions.
        </p>
      </div>

      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700 space-x-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Contract Name
          </label>
          <input
            type="text"
            value={contractName}
            onChange={(e) => setContractName(e.target.value)}
            placeholder="e.g. Master Services Agreement - Acme Corp"
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Contract Expectations <span className="text-slate-400 font-normal">(optional)</span>
          </label>
          <textarea
            value={expectations}
            onChange={(e) => setExpectations(e.target.value)}
            placeholder={"Describe what you expect from this contract, e.g.:\n• I need 30-day termination for convenience\n• Liability cap should be at least $1M\n• Must include data privacy protections\n• No non-compete clause"}
            rows={5}
            className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all resize-y text-sm"
          />
          <p className="mt-1 text-xs text-slate-400">
            We'll analyze how well the contract matches your stated requirements.
          </p>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all ${
            file
              ? "border-accent-blue bg-blue-50"
              : "border-slate-300 hover:border-slate-400 bg-slate-50"
          }`}
         {!file && (
            <input
              type="file"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf,.doc,.docx"
            />
          )}
          
          {file ? (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-accent-blue/10 rounded-full flex items-center justify-center mb-4">
                <File className="w-8 h-8 text-accent-blue" />
              </div>
              <p className="text-lg font-semibold text-slate-900 mb-1">{file.name}</p>
              <p className="text-sm text-slate-500 mb-4">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="text-red-500 hover:text-red-700 text-sm font-medium flex items-center space-x-1"
              >
                <X className="w-4 h-4" />
                <span>Remove file</span>
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-slate-200 rounded-full flex items-center justify-center mb-4">
                <UploadIcon className="w-8 h-8 text-slate-500" />
              </div>
              <p className="text-lg font-semibold text-slate-900 mb-1">
                Drop contract here or click to browse
              </p>
              <p className="text-sm text-slate-500">
                Supported formats: PDF, DOCX, DOC (Max 20MB)
              </p>
            </div>
          )}
        </div>

        <div className="mt-8">
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className={`w-full py-3 rounded-lg font-bold text-white transition-all flex items-center justify-center space-x-2 ${
              !file || isUploading
                ? "bg-slate-300 cursor-not-allowed"
                : "bg-accent-blue hover:bg-blue-700 shadow-lg shadow-blue-200"
            }`}
          >
            {isUploading ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Analyzing Document...</span>
              </>
            ) : (
              <>
                <Check className="w-5 h-5" />
                <span>Start Review</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
