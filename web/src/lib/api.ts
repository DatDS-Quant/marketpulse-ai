
import { ChartResponse, InsightSeed, PaginatedResponse, SystemStatus, KPIResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function fetchApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      next: { revalidate: 0 }, // no-cache for analytics dashboard by default
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // Ignore json parse error for non-json responses
      }
      throw new ApiError(errorMessage, response.status);
    }

    return response.json() as Promise<T>;
  } catch (error) {
    console.error(`API Fetch Error [${path}]:`, error);
    throw error;
  }
}

export const api = {
  getSystemStatus: () => fetchApi<SystemStatus>("/api/v1/status"),
  
  getMetrics: () => fetchApi<KPIResponse>("/api/v1/metrics"),
  
  getTopTrends: () => fetchApi<ChartResponse>("/api/v1/trends/top"),
  
  getTrendMetrics: (keyword?: string) => {
    const url = new URL(`${API_BASE_URL}/api/v1/trends/metrics`);
    if (keyword) url.searchParams.append("keyword", keyword);
    return fetchApi<ChartResponse>(url.pathname + url.search);
  },
  
  getSources: () => fetchApi<ChartResponse>("/api/v1/sources"),
  
  getArticles: (page = 1, size = 10, source?: string, keyword?: string) => {
    const url = new URL(`${API_BASE_URL}/api/v1/articles`);
    url.searchParams.append("page", page.toString());
    url.searchParams.append("size", size.toString());
    if (source) url.searchParams.append("source", source);
    if (keyword) url.searchParams.append("keyword", keyword);
    return fetchApi<PaginatedResponse>(url.pathname + url.search);
  },
  
  getInsightSeeds: () => fetchApi<{ data: InsightSeed[] }>("/api/v1/insights/seeds"),
};
