import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-navy">Welcome Back</h1>
          <p className="text-slate-500 mt-2">Sign in to LexRedline to review your contracts</p>
        </div>
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <SignIn
            appearance={{
              elements: {
                formButtonPrimary: "bg-accent-blue hover:bg-blue-700",
                card: "shadow-none border-0 p-0",
                headerTitle: "hidden",
                headerSubtitle: "hidden",
                socialButtonsBlockButton: "border-slate-200 hover:bg-slate-50 text-sm py-3",
                formFieldInput: "border-slate-300 focus:ring-accent-blue",
                dividerLine: "bg-slate-200",
                dividerText: "text-slate-400 text-xs",
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}