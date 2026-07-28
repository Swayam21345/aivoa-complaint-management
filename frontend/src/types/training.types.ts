export interface QuizQuestionRead {
  id: string;
  quiz_id: string;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  explanation?: string;
  display_order: number;
}

export interface QuizQuestionCreate {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: string;
  explanation?: string;
  display_order?: number;
}

export interface QuizCreate {
  title: string;
  passing_score: number;
  randomize_questions: boolean;
  time_limit_minutes: number;
  questions: QuizQuestionCreate[];
}

export interface QuizRead {
  id: string;
  course_id: string;
  title: string;
  passing_score: number;
  randomize_questions: boolean;
  time_limit_minutes: number;
  created_at: string;
  questions: QuizQuestionRead[];
}

export interface TrainingCourseRead {
  id: string;
  course_number: string;
  title: string;
  description?: string;
  category: string;
  training_type: string;
  duration_minutes: number;
  passing_score: number;
  validity_days: number;
  status: 'DRAFT' | 'ACTIVE' | 'RETIRED';
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  quizzes: QuizRead[];
}

export interface TrainingCourseCreate {
  title: string;
  description?: string;
  category: string;
  training_type: string;
  duration_minutes: number;
  passing_score: number;
  validity_days: number;
}

export interface TrainingCourseUpdate {
  title?: string;
  description?: string;
  category?: string;
  training_type?: string;
  duration_minutes?: number;
  passing_score?: number;
  validity_days?: number;
  status?: string;
}

export interface TrainingAssignmentRead {
  id: string;
  course_id: string;
  user_id: string;
  assigned_by: string;
  assigned_date: string;
  due_date: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'OVERDUE';
  completion_date?: string;
  score?: number;
  attempts: number;
  electronic_signature_id?: string;
  course?: TrainingCourseRead;
  user_email?: string;
  user_full_name?: string;
}

export interface QuizAttemptRead {
  id: string;
  quiz_id: string;
  user_id: string;
  score: number;
  passed: boolean;
  attempted_at: string;
}

export interface CompetencyRead {
  id: string;
  user_id: string;
  skill: string;
  level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';
  verified_by: string;
  verified_at: string;
  user_full_name?: string;
}

export interface TrainingDashboardRead {
  total_courses: number;
  active_courses: number;
  total_assignments: number;
  completed_assignments: number;
  overdue_assignments: number;
  in_progress_assignments: number;
  completion_rate_percentage: number;
  average_quiz_score: number;
  department_compliance: Record<string, number>;
  status_distribution: Record<string, number>;
  by_category: Record<string, number>;
  top_failed_courses: Array<{ course_number: string; title: string }>;
}

export interface TrainingReportRead {
  total_records: number;
  completed_count: number;
  overdue_count: number;
  expired_certifications_count: number;
  competency_matrix: CompetencyRead[];
  assignments: TrainingAssignmentRead[];
}
