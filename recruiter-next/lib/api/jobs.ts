import "server-only";
import { api } from "@/lib/api/client";
import type {
  JobsListResponse,
  JobDetail,
  JobCreateData,
  JobUpdateData,
  JobApplicantsResponse,
  JobFormMetadata,
  JobFilters,
  DashboardStatsResponse,
  MutationResponse,
} from "@/lib/types";

/**
 * Job management API. Ports recruiter/src/lib/api/jobs.ts.
 *
 * The original hand-built a URLSearchParams for every filtered call; `api.get`
 * now takes a params object and drops undefined/null/empty values, so those
 * blocks collapse to one argument.
 *
 * This module replaces the 17 hardcoded `http://localhost:8000` call sites that
 * the SvelteKit job routes used instead of their own API layer (MIGRATION.md
 * debt #1) — every job route should import from here.
 */

/** Mutations return the job alongside the flat success envelope. */
export type JobMutationResponse = MutationResponse & { job: JobDetail };

export function getDashboardStats(period = "30d") {
  return api.get<DashboardStatsResponse>("/recruiter/dashboard/stats/", {
    period,
  });
}

export function listJobs(filters?: JobFilters) {
  return api.get<JobsListResponse>(
    "/recruiter/jobs/",
    filters as Record<string, unknown> | undefined,
  );
}

export function getJob(jobId: number) {
  return api.get<JobDetail>(`/recruiter/jobs/${jobId}/`);
}

export function createJob(data: JobCreateData) {
  return api.post<JobMutationResponse>("/recruiter/jobs/create/", data);
}

export function updateJob(jobId: number, data: JobUpdateData) {
  return api.patch<JobMutationResponse>(
    `/recruiter/jobs/${jobId}/update/`,
    data,
  );
}

export function deleteJob(jobId: number, force = false) {
  return api.delete<MutationResponse>(
    `/recruiter/jobs/${jobId}/delete/`,
    force ? { force: "true" } : undefined,
  );
}

export function publishJob(jobId: number) {
  return api.post<JobMutationResponse>(`/recruiter/jobs/${jobId}/publish/`, {});
}

export function closeJob(jobId: number) {
  return api.post<JobMutationResponse>(`/recruiter/jobs/${jobId}/close/`, {});
}

export function getJobApplicants(
  jobId: number,
  filters?: { status?: string; ordering?: string },
) {
  return api.get<JobApplicantsResponse>(
    `/recruiter/jobs/${jobId}/applicants/`,
    filters,
  );
}

/** Countries, states, cities, skills, industries, qualifications. */
export function getJobFormMetadata(filters?: {
  country_id?: number;
  state_id?: number;
  search?: string;
}) {
  return api.get<JobFormMetadata>("/recruiter/jobs/metadata/", filters);
}
