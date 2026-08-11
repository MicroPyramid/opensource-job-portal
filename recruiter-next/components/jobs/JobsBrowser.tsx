"use client";

import { useActionState, useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Plus,
  Search,
  Filter,
  Eye,
  Users,
  Edit,
  XCircle,
  ExternalLink,
  Calendar,
  MapPin,
  Briefcase,
  Send,
  Archive,
  Copy,
} from "lucide-react";
import { Button, Card, Badge } from "@/components/ui";
import type { JobListItem, JobStatus } from "@/lib/types";
import {
  closeJobAction,
  deleteJobAction,
  publishJobAction,
  type JobActionState,
} from "@/app/(dashboard)/dashboard/jobs/actions";

/**
 * The interactive half of the jobs list.
 *
 * `viewMode` is client-only state shared by the toolbar and the results, so both
 * live inside this one boundary. The data itself is still fetched on the server
 * and handed down as props — nothing here calls Django.
 */

const filterOptions = [
  { value: "all", label: "All Jobs" },
  { value: "Live", label: "Active" },
  { value: "Draft", label: "Drafts" },
  { value: "Disabled", label: "Closed" },
  { value: "Expired", label: "Expired" },
];

function statusVariant(
  status: JobStatus,
): "success" | "warning" | "error" | "neutral" {
  switch (status) {
    case "Live":
      return "success";
    case "Draft":
      return "neutral";
    case "Disabled":
      return "error";
    case "Expired":
      return "warning";
    default:
      return "neutral";
  }
}

type JobAction = (
  prevState: JobActionState,
  formData: FormData,
) => Promise<JobActionState>;

const initialActionState: JobActionState = { success: true };

/**
 * One job mutation, as a real <form> so it works without JS.
 *
 * The original surfaced delete failures with `alert()` but left publish/close
 * errors entirely invisible — the action returned `{success:false, error}` into
 * the `form` prop, which the page never rendered. Reporting all three the same
 * way is the small deliberate improvement here.
 */
function JobActionForm({
  jobId,
  action,
  title,
  className,
  formClassName,
  confirmMessage,
  children,
}: {
  jobId: number;
  action: JobAction;
  title?: string;
  className: string;
  formClassName?: string;
  confirmMessage?: string;
  children: ReactNode;
}) {
  const [state, formAction, isPending] = useActionState(
    action,
    initialActionState,
  );

  useEffect(() => {
    if (state.error) window.alert(state.error);
  }, [state]);

  return (
    <form
      action={formAction}
      className={formClassName}
      onSubmit={(event) => {
        if (confirmMessage && !window.confirm(confirmMessage)) {
          event.preventDefault();
        }
      }}
    >
      <input type="hidden" name="jobId" value={jobId} />
      <button
        type="submit"
        disabled={isPending}
        className={className}
        title={title}
      >
        {children}
      </button>
    </form>
  );
}

export interface JobsBrowserProps {
  jobs: JobListItem[];
  count: number;
  next: string | null;
  previous: string | null;
  currentPage: number;
  filters: { status: string; search: string };
}

export function JobsBrowser({
  jobs,
  count,
  next,
  previous,
  currentPage,
  filters,
}: JobsBrowserProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState(filters.search);
  const [selectedFilter, setSelectedFilter] = useState<JobStatus | "all">(
    filters.status as JobStatus | "all",
  );
  const [viewMode, setViewMode] = useState<"grid" | "list">("list");

  /**
   * Overrides are passed explicitly rather than read from state: `setState` is
   * async, so a select's onChange handler would otherwise navigate with the
   * previous value.
   */
  function updateFilters(
    overrides: { status?: JobStatus | "all"; search?: string } = {},
  ) {
    const status = overrides.status ?? selectedFilter;
    const search = overrides.search ?? searchQuery;

    const params = new URLSearchParams();
    params.set("page", "1"); // Reset to page 1 on filter change
    if (status !== "all") params.set("status", status);
    if (search.trim()) params.set("search", search.trim());
    router.push(`?${params.toString()}`, { scroll: false });
  }

  /** Paginate against the filters actually applied to this page, not unsubmitted input. */
  function goToPage(pageNum: number) {
    const params = new URLSearchParams();
    params.set("page", pageNum.toString());
    if (filters.status && filters.status !== "all")
      params.set("status", filters.status);
    if (filters.search) params.set("search", filters.search);
    router.push(`?${params.toString()}`, { scroll: false });
  }

  return (
    <>
      {/* Filters and Search */}
      <Card padding="md">
        <form
          onSubmit={(event) => {
            event.preventDefault();
            updateFilters();
          }}
          className="flex flex-col md:flex-row gap-4"
        >
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              onBlur={() => updateFilters()}
              placeholder="Search jobs by title..."
              className="w-full pl-10 pr-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>

          {/* Filter */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
              <select
                value={selectedFilter}
                onChange={(event) => {
                  const status = event.target.value as JobStatus | "all";
                  setSelectedFilter(status);
                  updateFilters({ status });
                }}
                className="pl-9 pr-8 py-2 border border-border rounded-lg bg-white focus:ring-2 focus:ring-primary/20 focus:border-primary appearance-none cursor-pointer"
              >
                {filterOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex border border-border rounded-lg overflow-hidden">
              <button
                type="button"
                onClick={() => setViewMode("list")}
                className={`px-3 py-2 ${
                  viewMode === "list"
                    ? "bg-primary/10 text-primary"
                    : "bg-white text-muted"
                } hover:bg-surface transition-colors`}
                aria-label="List view"
                aria-pressed={viewMode === "list"}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("grid")}
                className={`px-3 py-2 ${
                  viewMode === "grid"
                    ? "bg-primary/10 text-primary"
                    : "bg-white text-muted"
                } hover:bg-surface transition-colors`}
                aria-label="Grid view"
                aria-pressed={viewMode === "grid"}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM13 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2h-2z" />
                </svg>
              </button>
            </div>
          </div>
        </form>
      </Card>

      {/* Empty State */}
      {jobs.length === 0 ? (
        <Card padding="lg" className="text-center">
          <Briefcase className="w-12 h-12 text-muted mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-black mb-2">
            No jobs found
          </h3>
          <p className="text-muted mb-6">
            {searchQuery || selectedFilter !== "all"
              ? "Try adjusting your filters or search query"
              : "Get started by posting your first job"}
          </p>
          <Button href="/dashboard/jobs/new/">
            <Plus className="w-4 h-4" />
            Post New Job
          </Button>
        </Card>
      ) : viewMode === "list" ? (
        /* List View */
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface border-b border-border">
                <tr>
                  {[
                    "Job Details",
                    "Status",
                    "Posted",
                    "Expires",
                    "Performance",
                    "Actions",
                  ].map((heading) => (
                    <th
                      key={heading}
                      className="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-surface transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <Briefcase className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <Link
                            href={`/dashboard/jobs/${job.id}/${
                              job.status === "Draft" ? "" : "applicants/"
                            }`}
                            className="font-medium text-black hover:text-primary transition-colors"
                          >
                            {job.title}
                          </Link>
                          <div className="flex items-center gap-3 mt-1 text-sm text-muted">
                            <span>{job.company_name}</span>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {job.location_display}
                            </span>
                            <span>•</span>
                            <span>{job.job_type}</span>
                          </div>
                          {job.is_expiring_soon && (
                            <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-warning-light text-warning text-xs font-medium rounded">
                              <Calendar className="w-3 h-3" />
                              Expires in {job.days_until_expiry} days
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={statusVariant(job.status)}>
                        {job.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted">
                      {job.time_ago}
                    </td>
                    <td className="px-6 py-4 text-sm text-muted">
                      {job.days_until_expiry !== null &&
                      job.days_until_expiry !== undefined
                        ? `${job.days_until_expiry} days left`
                        : "Expired"}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1 text-muted">
                          <Eye className="w-4 h-4" />
                          {job.views_count.toLocaleString()}
                        </div>
                        <Link
                          href={`/dashboard/jobs/${job.id}/applicants/`}
                          className="flex items-center gap-1 text-primary hover:text-primary-hover font-medium transition-colors"
                        >
                          <Users className="w-4 h-4" />
                          {job.applicants_count}
                        </Link>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {job.status === "Draft" && (
                          <JobActionForm
                            jobId={job.id}
                            action={publishJobAction}
                            title="Publish"
                            className="p-2 text-success hover:bg-success-light rounded-lg transition-colors disabled:opacity-50"
                          >
                            <Send className="w-4 h-4" />
                          </JobActionForm>
                        )}
                        {job.status === "Live" && (
                          <JobActionForm
                            jobId={job.id}
                            action={closeJobAction}
                            title="Close"
                            className="p-2 text-warning hover:bg-warning-light rounded-lg transition-colors disabled:opacity-50"
                          >
                            <Archive className="w-4 h-4" />
                          </JobActionForm>
                        )}
                        {job.status === "Draft" && (
                          <Link
                            href={`/dashboard/jobs/${job.id}/edit/`}
                            className="p-2 text-muted hover:bg-surface rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                        )}
                        <Link
                          href={`/dashboard/jobs/${job.id}/`}
                          className="p-2 text-muted hover:bg-surface rounded-lg transition-colors"
                          title="View"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                        <Link
                          href={`/dashboard/jobs/new/?copy_from=${job.id}`}
                          className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
                          title="Copy Job"
                        >
                          <Copy className="w-4 h-4" />
                        </Link>
                        {job.status === "Draft" && (
                          <JobActionForm
                            jobId={job.id}
                            action={deleteJobAction}
                            title="Delete"
                            confirmMessage={`Are you sure you want to delete "${job.title}"?`}
                            className="p-2 text-error hover:bg-error-light rounded-lg transition-colors disabled:opacity-50"
                          >
                            <XCircle className="w-4 h-4" />
                          </JobActionForm>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        /* Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Card key={job.id} hover padding="md">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Briefcase className="w-6 h-6 text-primary" />
                </div>
                <Badge variant={statusVariant(job.status)}>{job.status}</Badge>
              </div>

              <Link
                href={`/dashboard/jobs/${job.id}/${
                  job.status === "Draft" ? "" : "applicants/"
                }`}
                className="block mb-3"
              >
                <h3 className="text-lg font-semibold text-black hover:text-primary transition-colors line-clamp-2">
                  {job.title}
                </h3>
              </Link>

              <div className="space-y-2 text-sm text-muted mb-4">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  {job.location_display}
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Posted {job.time_ago}
                </div>
              </div>

              {job.is_expiring_soon && (
                <div className="mb-4">
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-warning-light text-warning text-xs font-medium rounded">
                    <Calendar className="w-3 h-3" />
                    Expires in {job.days_until_expiry} days
                  </span>
                </div>
              )}

              <div className="flex items-center justify-between mb-4 pt-4 border-t border-border">
                <div className="flex items-center gap-1 text-sm text-muted">
                  <Eye className="w-4 h-4" />
                  {job.views_count.toLocaleString()}
                </div>
                <Link
                  href={`/dashboard/jobs/${job.id}/applicants/`}
                  className="flex items-center gap-1 text-sm text-primary hover:text-primary-hover font-medium transition-colors"
                >
                  <Users className="w-4 h-4" />
                  {job.applicants_count} applicants
                </Link>
              </div>

              <div className="flex items-center gap-2">
                {job.status === "Draft" ? (
                  <JobActionForm
                    jobId={job.id}
                    action={publishJobAction}
                    formClassName="flex-1"
                    className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 bg-success rounded-full text-sm font-medium text-white hover:opacity-90 transition-opacity"
                  >
                    <Send className="w-4 h-4" />
                    Publish
                  </JobActionForm>
                ) : job.status === "Live" ? (
                  <JobActionForm
                    jobId={job.id}
                    action={closeJobAction}
                    formClassName="flex-1"
                    className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 bg-warning rounded-full text-sm font-medium text-white hover:opacity-90 transition-opacity"
                  >
                    <Archive className="w-4 h-4" />
                    Close
                  </JobActionForm>
                ) : null}
                {job.status === "Draft" && (
                  <Button
                    href={`/dashboard/jobs/${job.id}/edit/`}
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                )}
                <Button
                  href={`/dashboard/jobs/${job.id}/`}
                  size="sm"
                  className="flex-1"
                >
                  View
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {jobs.length > 0 && (next || previous) && (
        <Card padding="md">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted">
              Showing {jobs.length} of {count} jobs
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => goToPage(currentPage - 1)}
                disabled={!previous}
              >
                Previous
              </Button>
              <span className="text-sm text-muted px-2">
                Page {currentPage}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => goToPage(currentPage + 1)}
                disabled={!next}
              >
                Next
              </Button>
            </div>
          </div>
        </Card>
      )}
    </>
  );
}

export default JobsBrowser;
