export interface DashboardKPIs {
  total_complaints: number;
  new_count: number;
  under_review_count: number;
  in_progress_count: number;
  resolved_count: number;
  closed_count: number;
  critical_priority_count: number;
  high_risk_count: number;
  created_today_count: number;
  created_this_month_count: number;
}

export interface DistributionItem {
  label: string;
  count: number;
}

export interface MonthlyTrendItem {
  month: string;
  count: number;
}

export interface DashboardTrends {
  by_status: DistributionItem[];
  by_category: DistributionItem[];
  by_risk_level: DistributionItem[];
  by_priority: DistributionItem[];
  monthly_trend: MonthlyTrendItem[];
}
