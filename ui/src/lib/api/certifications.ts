import { ApiClient } from './client';

export interface Certification {
	id: number;
	name: string;
	organization: string;
	credential_id?: string;
	credential_url?: string;
	issued_date?: string;
	expiry_date?: string;
	does_not_expire: boolean;
	description?: string;
	created_at: string;
	updated_at: string;
}

export interface CertificationCreateUpdate {
	name: string;
	organization: string;
	credential_id?: string;
	credential_url?: string;
	issued_date?: string;
	expiry_date?: string;
	does_not_expire: boolean;
	description?: string;
}

export async function getMyCertifications(): Promise<Certification[]> {
	return ApiClient.get<Certification[]>('/profile/certifications/');
}

export async function getCertificationById(certificationId: number): Promise<Certification> {
	return ApiClient.get<Certification>(`/profile/certifications/${certificationId}/`);
}

export async function addCertification(
	data: CertificationCreateUpdate
): Promise<Certification> {
	return ApiClient.post<Certification>('/profile/certifications/', data);
}

export async function updateCertification(
	certificationId: number,
	data: CertificationCreateUpdate
): Promise<Certification> {
	return ApiClient.put<Certification>(`/profile/certifications/${certificationId}/`, data);
}

export async function patchCertification(
	certificationId: number,
	data: Partial<CertificationCreateUpdate>
): Promise<Certification> {
	return ApiClient.patch<Certification>(`/profile/certifications/${certificationId}/`, data);
}

export async function deleteCertification(certificationId: number): Promise<void> {
	return ApiClient.delete(`/profile/certifications/${certificationId}/`);
}
