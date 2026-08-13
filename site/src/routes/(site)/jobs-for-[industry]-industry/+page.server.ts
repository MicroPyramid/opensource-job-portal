/**
 * /jobs-for-<industry>-industry/ — legacy alternate spelling of
 * /<industry>-industry-jobs/.
 *
 * Same story as `jobs-for-[skill]`: one view, two URLs. 301 to the canonical.
 */

import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, url }) => {
	const query = url.searchParams.toString();
	throw redirect(301, `/${params.industry}-industry-jobs/${query ? `?${query}` : ''}`);
};
