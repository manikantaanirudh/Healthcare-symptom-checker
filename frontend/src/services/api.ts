import axios, { AxiosResponse } from 'axios';
import { SymptomCheckRequest, SymptomCheckResponse, HistoryResponse, QueryHistory } from '../types';

// Configure axios base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('Response error:', error);
    
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.message || error.response.data?.detail || 'An error occurred';
      throw new Error(errorMessage);
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to the server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export const checkSymptoms = async (request: SymptomCheckRequest): Promise<SymptomCheckResponse> => {
  try {
    const response: AxiosResponse<SymptomCheckResponse> = await api.post('/api/v1/check', request);
    return response.data;
  } catch (error) {
    console.error('Error checking symptoms:', error);
    throw error;
  }
};

export const getQueryHistory = async (page: number = 1, pageSize: number = 10): Promise<HistoryResponse> => {
  try {
    const response: AxiosResponse<HistoryResponse> = await api.get('/api/v1/history', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting query history:', error);
    throw error;
  }
};

export const getQueryById = async (id: number): Promise<QueryHistory> => {
  try {
    const response: AxiosResponse<QueryHistory> = await api.get(`/api/v1/history/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error getting query by ID:', error);
    throw error;
  }
};

export const deleteQuery = async (id: number): Promise<void> => {
  try {
    await api.delete(`/api/v1/history/${id}`);
  } catch (error) {
    console.error('Error deleting query:', error);
    throw error;
  }
};

export const healthCheck = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};
