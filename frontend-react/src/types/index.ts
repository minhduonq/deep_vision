// API Types
export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

// Task Types
export type TaskType = 'deblur' | 'inpaint' | 'beauty_enhance';
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Task {
    task_id: string;
    status: TaskStatus;
    progress: number;
    result_url?: string;
    error?: string;
    message?: string;
    created_at?: string;
    updated_at?: string;
}

export interface EnhancementRequest {
    file: File;
    task_type: TaskType;
    description?: string;
}

export type AspectRatio = '1:1' | '3:4' | '4:3' | '16:9' | '9:16';

export interface GenerationRequest {
    prompt: string;
    negative_prompt?: string;
    aspect_ratio?: AspectRatio;
    num_inference_steps?: number;
    guidance_scale?: number;
    seed?: number;
}

// Health Check
export interface HealthCheck {
    status: string;
    version: string;
    gpu_available?: boolean;
    gpu_info?: {
        device_count: number;
        current_device: number;
        device_name: string;
        memory_allocated_gb: number;
        memory_reserved_gb: number;
    };
    device: string;
    active_tasks: number;
    total_tasks: number;
}

// History Item
export interface HistoryItem {
    id: string;
    taskType: TaskType;
    originalImage: string;
    resultImage?: string;
    status: TaskStatus;
    createdAt: Date;
    completedAt?: Date;
    processingTime?: number;
    metadata?: Record<string, unknown>;
}

// UI Types
export interface UploadedFile {
    file: File;
    preview: string;
    id: string;
}

export interface ToastMessage {
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    duration?: number;
}
