import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-start sm:items-center justify-start sm:justify-center bg-slate-50 px-2 sm:px-4 pt-8 sm:pt-0">
      <div className="w-full max-w-md">
        <div className="text-left sm:text-center mb-6 sm:mb-8 px-2 sm:px-0">
          <h1 className="text-2xl sm:text-3xl font-bold text-navy">Create Your Account</h1>
          <p className="text-slate-500 mt-2">Sign up with Google or email to get started</p>
        </div>
        <div className="bg-white p-4 sm:p-8 rounded-xl shadow-sm border border-slate-200">
          <SignUp />
        </div>
      </div>
    </div>
  );
}
