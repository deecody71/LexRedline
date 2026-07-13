"use client";

import { useState, useEffect } from "react";
import { useUser, useClerk } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { Check, Save, Loader2, User, Trash2, AlertTriangle } from "lucide-react";
import preferences from "@/lib/profile_preferences.json";

const INDUSTRIES = ["Legal", "Finance", "Tech", "IT Services", "Products", "Healthcare", "Manufacturing", "Other"];
const ROLES = ["Reviewer/Signer", "Creator", "Both"];

export default function ProfilePage() {
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();
  const router = useRouter();
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setIsSaveSuccess] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    screenName: "",
    industry: "",
    role: "",
    reviewerPrefs: [] as string[],
    creatorPrefs: [] as string[],
    otherNotes: "",
  });

  useEffect(() => {
    if (isLoaded && user) {
      const profile = (user.unsafeMetadata as any)?.profile || JSON.parse(localStorage.getItem("lexredline_profile_data") || "null");
      if (profile) {
        setFormData({
          firstName: profile.firstName || user.firstName || "",
          lastName: profile.lastName || user.lastName || "",
          screenName: profile.screenName || "",
          industry: profile.industry || "",
          role: profile.role || "",
          reviewerPrefs: profile.reviewerPrefs || [],
          creatorPrefs: profile.creatorPrefs || [],
          otherNotes: profile.otherNotes || "",
        });
      } else {
        setFormData(prev => ({
          ...prev,
          firstName: user.firstName || "",
          lastName: user.lastName || "",
        }));
      }
    }
  }, [isLoaded, user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setIsSaving(true);
    setIsSaveSuccess(false);

    try {
      await user.update({
        unsafeMetadata: {
          ...(user.unsafeMetadata || {}),
          profile: formData,
        },
      });
        await user.reload();
      localStorage.setItem("lexredline_profile_complete", "true");
      localStorage.setItem("lexredline_profile_data", JSON.stringify(formData));
      setIsSaveSuccess(true);

      // Redirect to dashboard after saving
      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (err) {
      console.error("Failed to save profile:", err);
      alert("Failed to save profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const togglePref = (type: "reviewer" | "creator", id: string) => {
    const key = type === "reviewer" ? "reviewerPrefs" : "creatorPrefs";
    setFormData(prev => {
      const current = prev[key];
      if (current.includes(id)) {
        return { ...prev, [key]: current.filter(i => i !== id) };
      } else {
        return { ...prev, [key]: [...current, id] };
      }
    });
  };

  const handleDeleteAccount = async () => {
    if (!user) return;
    setIsDeleting(true);
    try {
      // Call server API to delete the Clerk user account
      const res = await fetch("/api/delete-account", { method: "POST" });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Failed to delete account");
      }
      // Clear all local data
      localStorage.clear();
      // Sign out
      await signOut();
      router.push("/");
    } catch (err) {
      console.error("Failed to delete account:", err);
      alert("Failed to delete account. Please try again.");
      setIsDeleting(false);
    }
  };

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <Loader2 className="animate-spin h-12 w-12 text-accent-blue" />
      </div>
    );
  }

  if (!user) {
    router.push("/sign-up");
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="bg-navy p-6 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/10 p-2 rounded-lg">
              <User size={24} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Your Profile</h1>
              <p className="text-slate-300 text-sm">Tell us about your contract review needs</p>
            </div>
          </div>
          {saveSuccess && (
            <div className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 animate-in fade-in">
              <Check size={14} /> Saved Successfully
            </div>
          )}
        </div>

        <form onSubmit={handleSave} className="p-8 space-y-8">
          {/* Basic Info */}
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">First Name</label>
              <input
                type="text"
                required
                value={formData.firstName}
                onChange={e => setFormData({ ...formData, firstName: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Last Name</label>
              <input
                type="text"
                required
                value={formData.lastName}
                onChange={e => setFormData({ ...formData, lastName: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Screen Name (Public)</label>
              <input
                type="text"
                required
                placeholder="e.g. LegalPro_John"
                value={formData.screenName}
                onChange={e => setFormData({ ...formData, screenName: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Industry</label>
              <select
                required
                value={formData.industry}
                onChange={e => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all appearance-none bg-white"
              >
                <option value="" disabled>Select your industry</option>
                {INDUSTRIES.map(ind => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-4 text-center text-lg">I am a contract...</label>
            <div className="grid grid-cols-3 gap-4">
              {ROLES.map(role => (
                <button
                  key={role}
                  type="button"
                  onClick={() => setFormData({ ...formData, role })}
                  className={`py-4 px-2 rounded-xl border-2 transition-all font-bold text-sm text-center ${
                    formData.role === role
                      ? "border-accent-blue bg-blue-50 text-accent-blue shadow-md"
                      : "border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          {/* Conditional Preferences */}
          {(formData.role === "Reviewer/Signer" || formData.role === "Both") && (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
              <h2 className="text-md font-bold text-navy border-b border-slate-100 pb-2">Reviewer Priorities</h2>
              <p className="text-sm text-slate-500">What risks should we prioritize flagging for you?</p>
              <div className="grid md:grid-cols-2 gap-3">
                {preferences.reviewer_preferences.map((pref: any) => (
                  <label
                    key={pref.id}
                    className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.reviewerPrefs.includes(pref.id)
                        ? "border-accent-blue/30 bg-blue-50/50"
                        : "border-slate-100 hover:border-slate-200"
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mt-1 h-4 w-4 text-accent-blue border-slate-300 rounded"
                      checked={formData.reviewerPrefs.includes(pref.id)}
                      onChange={() => togglePref("reviewer", pref.id)}
                    />
                    <div>
                      <div className="text-sm font-bold text-slate-800">{pref.label}</div>
                      <div className="text-xs text-slate-500 leading-tight mt-1">{pref.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {(formData.role === "Creator" || formData.role === "Both") && (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
              <h2 className="text-md font-bold text-navy border-b border-slate-100 pb-2">Drafting Priorities</h2>
              <p className="text-sm text-slate-500">What standard protections should we ensure are present?</p>
              <div className="grid md:grid-cols-2 gap-3">
                {preferences.creator_preferences.map((pref: any) => (
                  <label
                    key={pref.id}
                    className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.creatorPrefs.includes(pref.id)
                        ? "border-accent-blue/30 bg-blue-50/50"
                        : "border-slate-100 hover:border-slate-200"
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mt-1 h-4 w-4 text-accent-blue border-slate-300 rounded"
                      checked={formData.creatorPrefs.includes(pref.id)}
                      onChange={() => togglePref("creator", pref.id)}
                    />
                    <div>
                      <div className="text-sm font-bold text-slate-800">{pref.label}</div>
                      <div className="text-xs text-slate-500 leading-tight mt-1">{pref.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          <hr className="border-slate-100" />

          {/* Other Notes */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Additional Review Preferences</label>
            <textarea
              rows={4}
              placeholder="e.g. Always flag any mention of specific competitors, or prioritize Net 45 payment terms..."
              value={formData.otherNotes}
              onChange={e => setFormData({ ...formData, otherNotes: e.target.value })}
              className="w-full px-4 py-2 border border-slate-300 rounded-md focus:ring-2 focus:ring-accent-blue focus:border-transparent outline-none transition-all"
            />
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="bg-navy hover:bg-slate-800 text-white px-8 py-3 rounded-lg font-bold transition-all flex items-center gap-2 shadow-lg shadow-slate-200 disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="animate-spin" size={20} /> : <Save size={20} />}
              {isSaving ? "Saving..." : "Save Profile"}
            </button>
          </div>
        </form>

        {/* Delete Account */}
        <div className="mt-12 p-6 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-bold text-red-900">Delete Account</h3>
              <p className="text-xs text-red-700 mt-1 mb-4">
                Permanently delete your account and all stored contracts. This action cannot be undone.
              </p>
              {showDeleteConfirm ? (
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isDeleting}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-xs font-bold transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {isDeleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
                    {isDeleting ? "Deleting..." : "Yes, delete my account"}
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="text-xs font-bold text-slate-600 hover:text-slate-800 transition-colors"
                    disabled={isDeleting}
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="text-xs font-bold text-red-600 hover:text-red-800 transition-colors underline underline-offset-2"
                >
                  Delete my account and all data
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
