export interface FiveWhyItem {
  step: number;
  question: string;
  answer: string;
}


export interface FishboneCategories {
  manpower?: string[];
  machine?: string[];
  material?: string[];
  method?: string[];
  measurement?: string[];
  milieu?: string[];
}

export interface FMEAAssessmentRead {
  id: string;
  rca_id: string;
  complaint_id: string;
  failure_mode: string;
  effect_of_failure: string;
  severity: number;
  occurrence: number;
  detection: number;
  rpn: number;
  risk_class: 'High' | 'Medium' | 'Low';
  recommended_action?: string;
  action_taken?: string;
  revised_severity?: number;
  revised_occurrence?: number;
  revised_detection?: number;
  revised_rpn?: number;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export interface FMEAAssessmentCreate {
  failure_mode: string;
  effect_of_failure: string;
  severity: number;
  occurrence: number;
  detection: number;
  recommended_action?: string;
}

export interface RCARead {
  id: string;
  complaint_id: string;
  complaint_number?: string;
  rca_number: string;
  methodology: 'FIVE_WHYS' | 'FISHBONE' | 'HYBRID';
  primary_root_cause: string;
  root_cause_category: string;
  five_whys?: FiveWhyItem[];
  fishbone?: FishboneCategories;
  contributing_factors?: string;
  status: 'DRAFT' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED';
  approved_by?: string;
  approved_at?: string;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
  fmea_items: FMEAAssessmentRead[];
}

export interface RCACreatePayload {
  complaint_id: string;
  primary_root_cause: string;
  root_cause_category?: string;
  methodology?: string;
  five_whys?: FiveWhyItem[];
  fishbone?: FishboneCategories;
  contributing_factors?: string;
  fmea_items?: FMEAAssessmentCreate[];
}

export interface RCAUpdatePayload {
  primary_root_cause?: string;
  root_cause_category?: string;
  methodology?: string;
  five_whys?: FiveWhyItem[];
  fishbone?: FishboneCategories;
  contributing_factors?: string;
  status?: string;
}

export interface RCAApprovePayload {
  password: string;
  reason: string;
}


export interface RCAListResponse {
  items: RCARead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RCADashboardRead {
  total_rcas: number;
  approved_rcas: number;
  pending_rcas: number;
  high_risk_fmea_count: number;
  average_rpn: number;
  by_category: Record<string, number>;
  by_methodology: Record<string, number>;
}
