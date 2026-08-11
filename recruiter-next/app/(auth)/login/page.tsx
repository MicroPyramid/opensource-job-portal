import type { Metadata } from "next";
import Link from "next/link";
import {
  Briefcase,
  Users,
  BarChart3,
  MessageSquare,
  Shield,
  Clock,
  CheckCircle,
} from "lucide-react";
import { Card } from "@/components/ui";
import { AuthMain, AUTH_MAIN_WIDE } from "@/components/auth/AuthMain";
import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = {
  title: "Login - PeelJobs Recruiter",
  description:
    "Sign in to your PeelJobs employer account to manage job postings and connect with top talent.",
};

const stats = [
  { value: "100k+", label: "Active Job Seekers", box: "bg-primary/5 border-primary/20", text: "text-primary" },
  { value: "1000+", label: "Daily Applications", box: "bg-success-light border-success/20", text: "text-success" },
  { value: "500+", label: "Companies Trust Us", box: "bg-primary/5 border-primary/20", text: "text-primary" },
  { value: "24/7", label: "Expert Support", box: "bg-warning-light border-warning/20", text: "text-warning" },
];

const features = [
  { icon: Briefcase, bg: "bg-primary/10", fg: "text-primary", title: "Manage Your Jobs", body: "View and manage all your active job postings in one place" },
  { icon: Users, bg: "bg-success-light", fg: "text-success", title: "Review Applicants", body: "Access qualified candidates and their detailed profiles" },
  { icon: BarChart3, bg: "bg-primary/10", fg: "text-primary", title: "Track Performance", body: "Monitor job views, applications, and hiring metrics" },
  { icon: MessageSquare, bg: "bg-warning-light", fg: "text-warning", title: "Connect with Talent", body: "Message and schedule interviews with candidates" },
];

const trustIndicators = [
  { icon: Shield, label: "SSL Encrypted" },
  { icon: CheckCircle, label: "GDPR Compliant" },
  { icon: Clock, label: "24/7 Support" },
];

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ redirect?: string }>;
}) {
  // Ports the load() in +page.server.ts — carries the post-login destination.
  const redirectTo = (await searchParams).redirect || "/dashboard/";

  return (
    <AuthMain containerClass="max-w-6xl" mainClass={AUTH_MAIN_WIDE}>
      <div className="w-full">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left Column: Marketing Content */}
          <div className="space-y-8 lg:sticky lg:top-8 hidden lg:block">
            <div>
              <h1 className="text-3xl xl:text-4xl font-semibold text-black mb-4 leading-tight">
                Welcome Back to PeelJobs
              </h1>
              <p className="text-base xl:text-lg text-muted leading-relaxed">
                Continue managing your job postings and connecting with top
                talent across India.
              </p>
            </div>

            {/* Key Statistics */}
            <div className="grid grid-cols-2 gap-4">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className={`${stat.box} border rounded-lg p-5 text-center`}
                >
                  <div className={`text-2xl font-semibold ${stat.text} mb-1`}>
                    {stat.value}
                  </div>
                  <p className="text-sm text-muted font-medium">{stat.label}</p>
                </div>
              ))}
            </div>

            {/* Dashboard Features */}
            <Card padding="lg" className="shadow-md">
              <h3 className="text-xl font-semibold text-black mb-6 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Your Dashboard Awaits
              </h3>
              <div className="space-y-5">
                {features.map(({ icon: Icon, ...feature }) => (
                  <div key={feature.title} className="flex items-start gap-4">
                    <div className={`${feature.bg} rounded-full p-2.5 flex-shrink-0`}>
                      <Icon className={`w-5 h-5 ${feature.fg}`} />
                    </div>
                    <div>
                      <h4 className="font-medium text-black text-sm mb-0.5">
                        {feature.title}
                      </h4>
                      <p className="text-sm text-muted leading-relaxed">
                        {feature.body}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Right Column: Login Form */}
          <Card padding="lg" className="shadow-lg">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold text-black">Welcome Back</h2>
              <p className="text-muted mt-2">Sign in to your employer account</p>
            </div>

            <LoginForm redirectTo={redirectTo} />

            <p className="mt-6 text-center text-sm text-muted">
              Don&apos;t have an account?{" "}
              <Link
                href="/signup/"
                className="font-medium text-primary hover:text-primary-hover transition-colors"
              >
                Sign up for free
              </Link>
            </p>

            <div className="mt-5 pt-5 border-t border-border">
              <p className="text-center text-sm text-muted">
                Looking for a job?{" "}
                <a
                  href="https://peeljobs.com/login/"
                  className="font-medium text-primary hover:text-primary-hover transition-colors"
                >
                  Job Seeker Login
                </a>
              </p>
            </div>

            <div className="mt-5 pt-5 border-t border-border">
              <div className="flex justify-center flex-wrap gap-4 text-xs text-muted">
                {trustIndicators.map(({ icon: Icon, label }) => (
                  <div key={label} className="flex items-center gap-1.5">
                    <Icon className="w-3.5 h-3.5" />
                    <span>{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AuthMain>
  );
}
