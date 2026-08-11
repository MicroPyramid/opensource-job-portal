import type { Metadata } from "next";
import { Plus, Archive } from "lucide-react";
import { Button } from "@/components/ui";
import { JobsBrowser } from "@/components/jobs/JobsBrowser";
import { listJobs } from "@/lib/api/jobs";
import type { JobFilters, JobStatus } from "@/lib/types";

export const metadata: Metadata = {
  title: "Jobs - PeelJobs Recruiter",
};

/**
 * Ports (dashboard)/dashboard/jobs/+page.{server.ts,svelte}.
 *
 * The original's load() hit `http://localhost:8000/...` directly and re-checked
 * auth cookies by hand; both now come from `listJobs()` and the layout's
 * `requireAuth()`. Its 401 branch is likewise gone — proxy renews, the DAL
 * redirects.
 */
export default async function JobsPage({
  searchParams,
}: {
  searchParams: Promise<{
    page?: string;
    status?: string;
    search?: string;
    page_size?: string;
  }>;
}) {
  const params = await searchParams;

  const page = Number(params.page) || 1;
  const status = params.status ?? "";
  const search = params.search ?? "";

  const filters: JobFilters = {
    page,
    page_size: Number(params.page_size) || 20,
    ordering: "-created_on",
  };
  if (status && status !== "all") filters.status = status as JobStatus;
  if (search) filters.search = search;

  const data = await listJobs(filters);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-black">Jobs</h1>
          <p className="text-muted mt-1">Manage your job postings</p>
        </div>
        <div className="flex gap-3">
          <Button href="/dashboard/jobs/inactive/" variant="secondary">
            <Archive className="w-4 h-4" />
            Inactive Jobs
          </Button>
          <Button href="/dashboard/jobs/new/">
            <Plus className="w-4 h-4" />
            Post New Job
          </Button>
        </div>
      </div>

      <JobsBrowser
        jobs={data.results}
        count={data.count}
        next={data.next}
        previous={data.previous}
        currentPage={page}
        filters={{ status: status || "all", search }}
      />
    </div>
  );
}
