import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { Task, EnhancementRequest, GenerationRequest, HealthCheck } from '@/types';

class ApiClient {
    private client: AxiosInstance;

    constructor() {
        this.client = axios.create({
            baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
            timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Request interceptor
        this.client.interceptors.request.use(
            config => {
                // Add auth token if available
                const token = localStorage.getItem('auth_token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }

                // Log request for debugging
                console.log('API Request:', {
                    url: config.url,
                    method: config.method,
                    data: config.data,
                    headers: config.headers
                });

                return config;
            },
            error => Promise.reject(error)
        );

        // Response interceptor
        this.client.interceptors.response.use(
            response => {
                console.log('API Response:', {
                    url: response.config.url,
                    status: response.status,
                    data: response.data
                });
                return response;
            },
            (error: AxiosError) => {
                console.error('API Error:', {
                    url: error.config?.url,
                    status: error.response?.status,
                    data: error.response?.data,
                    message: error.message
                });

                // Handle common errors
                if (error.response?.status === 401) {
                    // Unauthorized - redirect to login or refresh token
                    localStorage.removeItem('auth_token');
                }
                return Promise.reject(error);
            }
        );
    }

    // Health Check
    async healthCheck(): Promise<HealthCheck> {
        const response = await this.client.get<HealthCheck>('/api/v1/health');
        return response.data;
    }

    // Image Enhancement
    async enhanceImage(request: EnhancementRequest): Promise<Task> {
        const formData = new FormData();
        formData.append('file', request.file);
        formData.append('task_type', request.task_type);
        if (request.description) {
            formData.append('description', request.description);
        }

        const response = await this.client.post<Task>('/api/v1/enhance', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    }

    // Get Task Status
    async getTaskStatus(taskId: string): Promise<Task> {
        const response = await this.client.get<Task>(`/api/v1/status/${taskId}`);
        return response.data;
    }

    // Image Generation
    async generateImage(request: GenerationRequest): Promise<Task> {
        const response = await this.client.post<Task>('/api/v1/generate', request);
        return response.data;
    }

    // Download Result
    async downloadResult(url: string): Promise<Blob> {
        const fullUrl = url.startsWith('http') ? url : `${this.client.defaults.baseURL}${url}`;
        const response = await this.client.get(fullUrl, {
            responseType: 'blob',
        });
        return response.data;
    }

    // Generic GET request
    async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
        const response = await this.client.get<T>(url, config);
        return response.data;
    }

    // Generic POST request
    async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
        const response = await this.client.post<T>(url, data, config);
        return response.data;
    }

    // Generic PUT request
    async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
        const response = await this.client.put<T>(url, data, config);
        return response.data;
    }

    // Generic DELETE request
    async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
        const response = await this.client.delete<T>(url, config);
        return response.data;
    }
}

export const apiClient = new ApiClient();
export default apiClient;
