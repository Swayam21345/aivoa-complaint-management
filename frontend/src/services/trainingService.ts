import apiClient from './apiClient';
import type {
  CompetencyRead,
  QuizAttemptRead,
  QuizCreate,
  QuizRead,
  TrainingAssignmentRead,
  TrainingCourseCreate,
  TrainingCourseRead,
  TrainingCourseUpdate,
  TrainingDashboardRead,
  TrainingReportRead,
} from '@/types/training.types';

export async function fetchCourseList(params?: {
  status?: string;
  category?: string;
  training_type?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<{ items: TrainingCourseRead[]; total: number; page: number; page_size: number }> {
  const { data } = await apiClient.get('/api/training', { params });
  return data;
}

export async function fetchCourseDetail(id: string): Promise<TrainingCourseRead> {
  const { data } = await apiClient.get<TrainingCourseRead>(`/api/training/${id}`);
  return data;
}

export async function createCourse(payload: TrainingCourseCreate): Promise<TrainingCourseRead> {
  const { data } = await apiClient.post<TrainingCourseRead>('/api/training', payload);
  return data;
}

export async function updateCourse(
  id: string,
  payload: TrainingCourseUpdate,
): Promise<TrainingCourseRead> {
  const { data } = await apiClient.patch<TrainingCourseRead>(`/api/training/${id}`, payload);
  return data;
}

export async function deleteCourse(id: string): Promise<void> {
  await apiClient.delete(`/api/training/${id}`);
}

export async function assignCourse(
  courseId: string,
  userId: string,
  dueDays: number = 30,
): Promise<TrainingAssignmentRead> {
  const { data } = await apiClient.post<TrainingAssignmentRead>(`/api/training/${courseId}/assign`, {
    user_id: userId,
    due_days: dueDays,
  });
  return data;
}

export async function bulkAssignCourse(
  courseId: string,
  userIds: string[],
  dueDays: number = 30,
): Promise<TrainingAssignmentRead[]> {
  const { data } = await apiClient.post<TrainingAssignmentRead[]>(`/api/training/${courseId}/bulk-assign`, {
    user_ids: userIds,
    due_days: dueDays,
  });
  return data;
}

export async function addCourseQuiz(courseId: string, payload: QuizCreate): Promise<QuizRead> {
  const { data } = await apiClient.post<QuizRead>(`/api/training/${courseId}/quiz`, payload);
  return data;
}

export async function submitQuizAttempt(
  courseId: string,
  answers: Array<{ question_id: string; selected_option: string }>,
): Promise<QuizAttemptRead> {
  const { data } = await apiClient.post<QuizAttemptRead>(`/api/training/${courseId}/complete`, {
    answers,
  });
  return data;
}

export async function verifyCompetency(
  userId: string,
  skill: string,
  level: string,
): Promise<CompetencyRead> {
  const { data } = await apiClient.post<CompetencyRead>('/api/training/competency', {
    user_id: userId,
    skill,
    level,
  });
  return data;
}

export async function fetchCompetencyMatrix(): Promise<CompetencyRead[]> {
  const { data } = await apiClient.get<CompetencyRead[]>('/api/training/matrix');
  return data;
}

export async function fetchTrainingDashboard(): Promise<TrainingDashboardRead> {
  const { data } = await apiClient.get<TrainingDashboardRead>('/api/training/dashboard');
  return data;
}

export async function fetchTrainingReport(): Promise<TrainingReportRead> {
  const { data } = await apiClient.get<TrainingReportRead>('/api/training/report');
  return data;
}
