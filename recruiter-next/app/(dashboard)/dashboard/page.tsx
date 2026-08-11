import type { Metadata } from "next";
import Link from "next/link";
import { unstable_rethrow } from "next/navigation";
import {
  Briefcase,
  Users,
  Clock,
  FileText,
  Plus,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  type LucideIcon,
} from "lucide-react";
import { Button, Card, Badge } from "@/components/ui";
import { getDashboardStats } from "@/lib/api/jobs";
import type {
  ApplicantPipeline,
  DashboardRecentJob,
  DashboardStats,
  JobStatus,
} from "@/lib/types";

export const metadata: Metadata = {
  title: "Dashboard - PeelJobs Recruiter",
};

type BadgeVariant = "success" | "warning" | "error" | "neutral";

function jobStatusVariant(status: JobStatus | string): BadgeVariant {
  const variants: Record<string, BadgeVariant> = {
    Live: "success",
    Draft: "neutral",
    Disabled: "error",
    Expired: "warning",
  };
  return variants[status] ?? "neutral";
}

interface StatCard {
  label: string;
  value: string;
  icon: LucideIcon;
  trend: string;
  trendPositive: boolean;
  change?: string;
}

function buildStats(
  stats: DashboardStats | null,
  pipeline: ApplicantPipeline | null,
): StatCard[] {
  if (!stats) return [];

  return [
    {
      label: "Active Jobs",
      value: stats.live_jobs.toString(),
      icon: Briefcase,
      trend: `${stats.draft_jobs} drafts`,
      trendPositive: true,
    },
    {
      label: "Total Applicants",
      value: stats.total_applicants.toString(),
      icon: Users,
      trend: `${stats.new_applicants} new (30d)`,
      trendPositive: true,
      change: stats.applicants_trend,
    },
    {
      label: "Pending Review",
      value: pipeline ? pipeline.pending.toString() : "0",
      icon: Clock,
      trend: "Need action",
      trendPositive: false,
    },
    {
      label: "Hired",
      value: pipeline ? pipeline.hired.toString() : "0",
      icon: CheckCircle,
      trend: pipeline ? `${pipeline.conversion_rate}% conversion` : "0%",
      trendPositive: true,
    },
  ];
}

/**
 * Ports (dashboard)/dashboard/+page.{server.ts,svelte}.
 *
 * The load function's 401 branch is gone: an expired token is renewed by
 * `proxy.ts`, and a genuinely invalid session is caught by `requireAuth()` in the
 * layout, which runs before this page. What remains is the "Django is up but
 * unhappy" case, which degrades to the same empty state the original rendered.
 */
export default async function DashboardPage() {
  let stats: DashboardStats | null = null;
  let pipeline: ApplicantPipeline | null = null;
  let recentJobs: DashboardRecentJob[] = [];

  try {
    const data = await getDashboardStats("30d");
    stats = data.stats;
    pipeline = data.pipeline;
    recentJobs = data.recent_jobs ?? [];
  } catch (error) {
    // Next signals control flow (redirect, notFound, dynamic-rendering bailout)
    // by throwing. Swallowing those here would both spam the build log and, for
    // the dynamic bailout, risk this page being treated as static.
    unstable_rethrow(error);
    console.error("Dashboard load error:", error);
  }

  const statCards = buildStats(stats, pipeline);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-black">
            Dashboard
          </h1>
          <p className="text-muted mt-1">
            Welcome back! Here&apos;s what&apos;s happening today.
          </p>
        </div>
        <Button href="/dashboard/jobs/new/">
          <Plus className="w-4 h-4" />
          Post New Job
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} padding="md">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-muted">{stat.label}</p>
                  <p className="text-3xl font-bold text-black mt-2">
                    {stat.value}
                  </p>
                  <div className="flex items-center gap-1 mt-2">
                    {stat.change ? (
                      stat.change.startsWith("+") ? (
                        <>
                          <TrendingUp className="w-4 h-4 text-success" />
                          <span className="text-xs font-medium text-success">
                            {stat.change}
                          </span>
                        </>
                      ) : stat.change.startsWith("-") ? (
                        <>
                          <TrendingDown className="w-4 h-4 text-error" />
                          <span className="text-xs font-medium text-error">
                            {stat.change}
                          </span>
                        </>
                      ) : (
                        <span className="text-xs font-medium text-muted">
                          {stat.change}
                        </span>
                      )
                    ) : (
                      <p
                        className={`text-xs ${
                          stat.trendPositive ? "text-success" : "text-warning"
                        } font-medium`}
                      >
                        {stat.trend}
                      </p>
                    )}
                  </div>
                </div>
                <div
                  className={`w-12 h-12 rounded-lg ${
                    stat.trendPositive ? "bg-primary/10" : "bg-warning-light"
                  } flex items-center justify-center`}
                >
                  <Icon
                    className={`w-6 h-6 ${
                      stat.trendPositive ? "text-primary" : "text-warning"
                    }`}
                  />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Hiring Pipeline Overview */}
      {pipeline && (
        <Card padding="md">
          <h2 className="text-lg font-semibold text-black mb-4">
            Hiring Pipeline
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 rounded-lg bg-primary/5">
              <div className="text-3xl font-bold text-primary">
                {pipeline.pending}
              </div>
              <div className="text-sm text-muted mt-1">Pending Review</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-purple-50">
              <div className="text-3xl font-bold text-purple-600">
                {pipeline.shortlisted}
              </div>
              <div className="text-sm text-muted mt-1">Shortlisted</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-success-light">
              <div className="text-3xl font-bold text-success">
                {pipeline.hired}
              </div>
              <div className="text-sm text-muted mt-1">Hired</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-surface">
              <div className="text-3xl font-bold text-muted">
                {pipeline.rejected}
              </div>
              <div className="text-sm text-muted mt-1">Rejected</div>
            </div>
          </div>
        </Card>
      )}

      {/* Recent Jobs */}
      <Card padding="none">
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-black">Recent Jobs</h2>
            <Link
              href="/dashboard/jobs/"
              className="text-sm text-primary hover:text-primary-hover font-medium transition-colors"
            >
              View all jobs
            </Link>
          </div>
        </div>

        {recentJobs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface border-b border-border">
                <tr>
                  {["Job Title", "Applications", "New (7d)", "Pending", "Status"].map(
                    (heading) => (
                      <th
                        key={heading}
                        className="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider"
                      >
                        {heading}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {recentJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-surface transition-colors">
                    <td className="px-6 py-4">
                      <Link
                        href={`/dashboard/jobs/${job.id}/`}
                        className="text-sm font-medium text-primary hover:text-primary-hover transition-colors"
                      >
                        {job.title}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        {job.applicants_count || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {job.new_applicants > 0 ? (
                        <span className="inline-flex items-center gap-1 text-success font-medium">
                          <TrendingUp className="w-4 h-4" />
                          {job.new_applicants}
                        </span>
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {job.pending_review > 0 ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-warning-light text-warning font-medium">
                          <Clock className="w-3 h-3" />
                          {job.pending_review}
                        </span>
                      ) : (
                        <span className="text-muted">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <Badge variant={jobStatusVariant(job.status)}>
                        {job.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center">
            <Briefcase className="w-12 h-12 text-muted mx-auto mb-3" />
            <p className="text-muted mb-4">No jobs posted yet</p>
            <Button href="/dashboard/jobs/new/">
              <Plus className="w-4 h-4" />
              Post Your First Job
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
