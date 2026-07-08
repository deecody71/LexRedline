import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-navy">Create Your Account</h1>
          <p className="text-slate-500 mt-2">Sign up with Google or email to get started</p>
        </div>
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <SignUp afterSignUpUrl="/dashboard" />
        </div>
      </div>
    </div>
  );
}
