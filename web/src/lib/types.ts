/* eslint-disable @typescript-eslint/no-explicit-any */

export interface ChartConfig {
  chart_type: string;
  title: string;
  x_axis_key: string;
  y_axis_keys: string[];
  labels: Record<string, string>;
  colors: Record<string, string>;
}

export interface ChartResponse {
  chart_config: ChartConfig;
  data: any[];
}

export interface KPICard {
  key: string;
  label: string;
  value: string | number;
  unit: string;
  status: string;
}

export interface KPIResponse {
  cards: KPICard[];
}

export interface Metric {
  title: string;
  value: string;
  change?: string;
  trend?: string;
  status?: string;
}

export interface SystemStatus {
  status: string;
  version: string;
  timestamp: string;
  uptime: number;
  environment: string;
  latest_run_at?: string;
  pipeline_metrics?: {
    total_processed_articles: number;
    quality_score: number;
  };
  components?: Record<string, any>;
  data_freshness?: string;
}

export interface InsightSeed {
  rule_id: string;
  category: string;
  severity: string;
  headline: string;
  description: string;
  metric_value?: number;
  threshold_used?: number;
  date_generated: string;
}

export interface PaginatedResponse {
  total: number;
  page: number;
  size: number;
  total_pages: number;
  data: any[];
}
