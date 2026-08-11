"use server";

import { revalidatePath } from "next/cache";
import { unstable_rethrow } from "next/navigation";
import { closeJob, deleteJob, publishJob } from "@/lib/api/jobs";
import { ApiError } from "@/lib/api/client";
import { requireAuth } from "@/lib/auth/dal";

export interface JobActionState {
  success: boolean;
  error?: string;
}

/**
 * Job list mutations. Port the three form actions in
 * (dashboard)/dashboard/jobs/+page.server.ts.
 *
 * Every one starts with `requireAuth()`. Server Actions are reachable by direct
 * POST, not only through this app's UI, so the proxy having run says nothing
 * about whether *this* request is authorised. The originals relied on the hooks
 * guard and checked nothing themselves.
 *
 * On success they `revalidatePath` instead of the client calling
 * `invalidateAll()` — the refresh is part of the mutation rather than something
 * the caller has to remember.
 */

const JOBS_PATH = "/dashboard/jobs";

function jobIdFrom(formData: FormData): number | null {
  const raw = formData.get("jobId")?.toString();
  if (!raw) return null;
  const id = Number(raw);
  return Number.isInteger(id) && id > 0 ? id : null;
}

async function runJobAction(
  formData: FormData,
  fallbackError: string,
  mutate: (jobId: number) => Promise<unknown>,
): Promise<JobActionState> {
  await requireAuth(JOBS_PATH + "/");

  const jobId = jobIdFrom(formData);
  if (jobId === null) {
    return { success: false, error: "Job ID is required" };
  }

  try {
    await mutate(jobId);
  } catch (error) {
    unstable_rethrow(error);
    if (error instanceof ApiError) {
      return { success: false, error: error.message };
    }
    return { success: false, error: fallbackError };
  }

  revalidatePath(JOBS_PATH);
  return { success: true };
}

export async function publishJobAction(
  _prevState: JobActionState,
  formData: FormData,
): Promise<JobActionState> {
  return runJobAction(formData, "Failed to publish job", publishJob);
}

export async function closeJobAction(
  _prevState: JobActionState,
  formData: FormData,
): Promise<JobActionState> {
  return runJobAction(formData, "Failed to close job", closeJob);
}

export async function deleteJobAction(
  _prevState: JobActionState,
  formData: FormData,
): Promise<JobActionState> {
  // `force=true` matches the original, which always hard-deleted from this list.
  return runJobAction(formData, "Failed to delete job", (jobId) =>
    deleteJob(jobId, true),
  );
}
