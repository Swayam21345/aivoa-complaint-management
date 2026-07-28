import apiClient from './apiClient';
import type { UploadResponse } from '@/types/api.types';
import type { InputType } from '@/types/complaint.types';

/**
 * Upload a file (PDF or image) or submit plain text for document ingestion.
 *
 * @param inputType        - The type of complaint source document.
 * @param file             - Binary file for pdf / image uploads.
 * @param text             - Raw text for email / text uploads.
 * @param onUploadProgress - Optional Axios progress callback (0–100).
 */
export async function analyzeComplaint(
  inputType: InputType,
  file?: File,
  text?: string,
  onUploadProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('input_type', inputType);

  if (file) {
    formData.append('file', file);
  }
  if (text) {
    formData.append('text', text);
  }

  const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onUploadProgress
      ? (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total,
            );
            onUploadProgress(percent);
          }
        }
      : undefined,
  });

  return response.data;
}
