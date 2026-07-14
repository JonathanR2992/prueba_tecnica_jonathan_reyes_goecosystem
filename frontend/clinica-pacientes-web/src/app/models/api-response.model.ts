export interface ApiErrorResponse {
  error: string;
  message: string;
  details?: Record<string, string>;
}

export interface ApiMessageResponse {
  message: string;
}