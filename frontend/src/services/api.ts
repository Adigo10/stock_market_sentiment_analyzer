import axios from 'axios';
import type { CompaniesResponse, FetchRankResponse, EnrichResponse } from '@/types';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? 'http://localhost:8000' : '/api');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 240000, // 4 minutes for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  async getCompanies(): Promise<string[]> {
    const response = await api.get<CompaniesResponse>('/companies');
    return response.data.companies;
  },

  async fetchAndRank(companyName: string): Promise<FetchRankResponse> {
    const response = await api.post<FetchRankResponse>('/api/fetch-and-rank', {
      company_name: companyName,
    });
    return response.data;
  },

  async enrichWithAI(companyName: string): Promise<EnrichResponse> {
    const response = await api.post<EnrichResponse>('/api/enrich-with-ai', {
      company_name: companyName,
    });
    return response.data;
  },

  async healthCheck(): Promise<boolean> {
    try {
      await api.get('/health');
      return true;
    } catch {
      return false;
    }
  },
};
