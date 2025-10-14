// TypeScript types for the Healthcare Symptom Checker

export interface SymptomCheckRequest {
  symptoms: string;
  age?: number;
  sex?: 'male' | 'female' | 'other';
  duration_days?: number;
  severity?: 'mild' | 'moderate' | 'severe';
  context?: string;
}

export interface Condition {
  condition: string;
  confidence: number;
  rationale: string;
}

export interface NextStep {
  type: 'self_care' | 'see_physician' | 'urgent_care';
  text: string;
}

export interface SymptomCheckResponse {
  probable_conditions: Condition[];
  recommended_next_steps: NextStep[];
  red_flags: string[];
  disclaimer: string;
  timestamp: string;
}

export interface QueryHistory {
  id: number;
  symptoms: string;
  age?: number;
  sex?: string;
  duration_days?: number;
  severity?: string;
  context?: string;
  response: SymptomCheckResponse;
  created_at: string;
}

export interface HistoryResponse {
  queries: QueryHistory[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  error: string;
  message: string;
  disclaimer: string;
}
