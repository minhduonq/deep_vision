import { useState, useRef } from 'react';
import { Sparkles, Upload, X, Image as ImageIcon, Wand2, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiClient } from '@/api/client';

interface TaskStatus {
    taskId: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    result_url?: string;  // Match backend snake_case
    error?: string;
}

const Enhancement = () => {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [customPrompt, setCustomPrompt] = useState('');
    const [useQuickOptions, setUseQuickOptions] = useState(true);
    const [quickOptions, setQuickOptions] = useState({
        deblur: false,
        superResolution: false,
        beautyFilter: false
    });
    const [isProcessing, setIsProcessing] = useState(false);
    const [tasks, setTasks] = useState<TaskStatus[]>([]);
    const [selectedLoRA, setSelectedLoRA] = useState('Super-Fusion');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const LORA_STYLES = [
        'Super-Fusion',
        'AI-Film-Gen',
        'HighFashion-Fusion',
        'StyAlta',
        'Holo-Neon',
        'Candy-Flash',
        'Super-Realism',
        'Neon-Anime'
    ];

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        // Validate file types and sizes
        const validFiles = files.filter(file => {
            if (!file.type.startsWith('image/')) {
                toast.error(`${file.name} is not an image`);
                return false;
            }
            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                toast.error(`${file.name} is too large (max 10MB)`);
                return false;
            }
            return true;
        });

        setSelectedFiles(prev => [...prev, ...validFiles]);
        toast.success(`Added ${validFiles.length} image(s)`);

        // Reset input
        if (e.target) e.target.value = '';
    };

    const removeFile = (index: number) => {
        setSelectedFiles(prev => prev.filter((_, i) => i !== index));
        toast.success('Image removed');
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        const files = Array.from(e.dataTransfer.files);
        const imageFiles = files.filter(f => f.type.startsWith('image/'));

        if (imageFiles.length > 0) {
            setSelectedFiles(prev => [...prev, ...imageFiles]);
            toast.success(`Added ${imageFiles.length} image(s)`);
        }
    };

    const handleStartEnhancement = async () => {
        if (selectedFiles.length === 0) {
            toast.error('Please select at least one image');
            return;
        }

        let prompt = '';

        if (useQuickOptions) {
            const selectedOptions = Object.entries(quickOptions)
                .filter(([_, value]) => value)
                .map(([key]) => key);

            if (selectedOptions.length === 0) {
                toast.error('Please select at least one enhancement option');
                return;
            }

            // Build prompt from quick options
            const optionPrompts = {
                deblur: 'Remove blur and make sharper',
                superResolution: 'Enhance resolution and details',
                beautyFilter: 'Enhance facial features and skin tone'
            };

            prompt = selectedOptions.map(opt => optionPrompts[opt as keyof typeof optionPrompts]).join(', ');
        } else {
            if (!customPrompt.trim()) {
                toast.error('Please enter a custom prompt');
                return;
            }
            prompt = customPrompt.trim();
        }

        setIsProcessing(true);
        setTasks([]);

        try {
            // Logic: 1 image -> Fast Edit, 2+ images -> LoRA Fusion
            if (selectedFiles.length === 1) {
                // Single image - use Fast Edit
                await processFastEdit(selectedFiles[0], prompt);
            } else if (selectedFiles.length === 2) {
                // Two images - use LoRA Fusion
                await processFusionEdit(selectedFiles[0], selectedFiles[1], prompt);
            } else {
                // Multiple images - process pairs with LoRA Fusion
                toast(`Processing ${selectedFiles.length} images in batches...`);
                await processMultipleImages(selectedFiles, prompt);
            }
        } catch (error) {
            console.error('Enhancement error:', error);
            toast.error('Enhancement failed. Please try again.');
        } finally {
            setIsProcessing(false);
        }
    };

    const processFastEdit = async (file: File, prompt: string) => {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', prompt);
            formData.append('guidance_scale', '1.0');
            formData.append('steps', '8');

            const response = await apiClient.post<{ task_id: string; status: string }>('/api/v1/edit/fast', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const taskId = response.task_id;
            toast.success('Fast edit started!');

            // Add to tasks list
            setTasks([{ taskId, status: 'pending', progress: 0 }]);

            // Poll for result
            await pollTaskStatus(taskId);
        } catch (error: any) {
            console.error('Fast edit error:', error);
            toast.error(error.response?.data?.detail || 'Fast edit failed');
        }
    };

    const processFusionEdit = async (image1: File, image2: File, prompt: string) => {
        try {
            const formData = new FormData();
            formData.append('image_1', image1);
            formData.append('image_2', image2);
            formData.append('prompt', prompt);
            formData.append('lora_adapter', selectedLoRA);
            formData.append('guidance_scale', '1.0');
            formData.append('steps', '4');

            const response = await apiClient.post<{ task_id: string; status: string }>('/api/v1/edit/fusion', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const taskId = response.task_id;
            toast.success('Fusion edit started!');

            setTasks([{ taskId, status: 'pending', progress: 0 }]);

            await pollTaskStatus(taskId);
        } catch (error: any) {
            console.error('Fusion edit error:', error);
            toast.error(error.response?.data?.detail || 'Fusion edit failed');
        }
    };

    const processMultipleImages = async (files: File[], prompt: string) => {
        // Process first image with Fast Edit
        toast(`Processing first image...`);
        await processFastEdit(files[0], prompt);

        // Process remaining images in pairs with first image as reference
        for (let i = 1; i < files.length; i++) {
            toast(`Processing image ${i + 1} of ${files.length}...`);
            await processFusionEdit(files[0], files[i], prompt);
        }

        toast.success('All images processed!');
    };

    const pollTaskStatus = async (taskId: string, maxAttempts = 60) => {
        for (let i = 0; i < maxAttempts; i++) {
            try {
                const status = await apiClient.get<TaskStatus>(`/api/v1/status/${taskId}`);

                console.log(`[Poll ${i + 1}] Task ${taskId}:`, {
                    status: status.status,
                    progress: status.progress,
                    result_url: status.result_url,
                    fullStatus: status
                });

                setTasks(prev => {
                    const updated = prev.map(t =>
                        t.taskId === taskId ? { ...t, ...status } : t
                    );
                    console.log('Updated tasks:', updated);
                    return updated;
                });

                if (status.status === 'completed') {
                    console.log('✅ Task completed! Result URL:', status.result_url);
                    toast.success('Enhancement completed!');

                    // Force a re-render by updating tasks again
                    setTimeout(() => {
                        setTasks(prev => [...prev]);
                    }, 100);

                    return;
                } else if (status.status === 'failed') {
                    toast.error(`Task failed: ${status.error || 'Unknown error'}`);
                    return;
                }

                // Wait 2 seconds before next poll
                await new Promise(resolve => setTimeout(resolve, 2000));
            } catch (error) {
                console.error('Poll error:', error);
            }
        }

        toast.error('Task timeout - please check status later');
    };

    const downloadResult = async (taskId: string, resultUrl: string) => {
        try {
            const blob = await apiClient.downloadResult(resultUrl);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `enhanced_${taskId}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            toast.success('Downloaded!');
        } catch (error) {
            console.error('Download error:', error);
            toast.error('Download failed');
        }
    };

    const getPreviewUrl = (file: File) => {
        return URL.createObjectURL(file);
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                    <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Image Enhancement
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Enhance your images with AI-powered processing
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid lg:grid-cols-2 gap-8">
                {/* Upload Section */}
                <div className="space-y-6">
                    {/* Upload Area */}
                    <div
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        className="p-8 rounded-2xl bg-white dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
                    >
                        <div className="text-center space-y-4">
                            <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <Upload className="w-10 h-10 text-white" />
                            </div>

                            <div>
                                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                    Upload Your Images
                                </h3>
                                <p className="text-gray-600 dark:text-gray-400">
                                    Drag and drop or click to select multiple images
                                </p>
                            </div>

                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                multiple
                                onChange={handleFileSelect}
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="inline-block px-6 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold cursor-pointer hover:shadow-lg transition-all"
                            >
                                Choose Images
                            </label>

                            {selectedFiles.length > 0 && (
                                <div className="pt-4">
                                    <p className="text-sm text-gray-600 dark:text-gray-400">
                                        {selectedFiles.length} image(s) selected
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Selected Images Preview */}
                    {selectedFiles.length > 0 && (
                        <div className="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                            <div className="flex items-center justify-between mb-3">
                                <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                                    Selected Images ({selectedFiles.length})
                                </h3>
                                <button
                                    onClick={() => setSelectedFiles([])}
                                    className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 font-medium"
                                >
                                    Clear All
                                </button>
                            </div>
                            <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
                                {selectedFiles.map((file, index) => (
                                    <div key={index} className="relative group">
                                        <img
                                            src={getPreviewUrl(file)}
                                            alt={file.name}
                                            className="w-full h-24 object-cover rounded-lg"
                                        />
                                        <button
                                            onClick={() => removeFile(index)}
                                            className="absolute top-1 right-1 p-1 rounded-full bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                        <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 rounded-b-lg truncate">
                                            {file.name}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Mode Toggle */}
                    <div className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                Enhancement Mode
                            </h3>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setUseQuickOptions(true)}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${useQuickOptions
                                        ? 'bg-primary-500 text-white'
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                        }`}
                                >
                                    Quick Options
                                </button>
                                <button
                                    onClick={() => setUseQuickOptions(false)}
                                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${!useQuickOptions
                                        ? 'bg-primary-500 text-white'
                                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                        }`}
                                >
                                    Custom Prompt
                                </button>
                            </div>
                        </div>

                        {useQuickOptions ? (
                            /* Quick Options */
                            <div className="space-y-3">
                                <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={quickOptions.deblur}
                                        onChange={(e) => setQuickOptions({ ...quickOptions, deblur: e.target.checked })}
                                        className="w-4 h-4 text-primary-600 rounded"
                                    />
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 dark:text-white">Deblur</p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Remove blur from images</p>
                                    </div>
                                </label>

                                <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={quickOptions.superResolution}
                                        onChange={(e) => setQuickOptions({ ...quickOptions, superResolution: e.target.checked })}
                                        className="w-4 h-4 text-primary-600 rounded"
                                    />
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 dark:text-white">Super Resolution</p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Increase image resolution</p>
                                    </div>
                                </label>

                                <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={quickOptions.beautyFilter}
                                        onChange={(e) => setQuickOptions({ ...quickOptions, beautyFilter: e.target.checked })}
                                        className="w-4 h-4 text-primary-600 rounded"
                                    />
                                    <div className="flex-1">
                                        <p className="font-medium text-gray-900 dark:text-white">Beauty Filter</p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">Enhance facial features</p>
                                    </div>
                                </label>
                            </div>
                        ) : (
                            /* Custom Prompt */
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                        <Wand2 className="w-4 h-4 inline mr-1" />
                                        Custom Enhancement Prompt
                                    </label>
                                    <textarea
                                        value={customPrompt}
                                        onChange={(e) => setCustomPrompt(e.target.value)}
                                        placeholder="Describe how you want to enhance your images... (e.g., 'Make the colors more vibrant and increase brightness')"
                                        className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[100px] resize-none"
                                    />
                                </div>
                                <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                                    <p className="text-xs text-blue-800 dark:text-blue-200">
                                        <strong>Tips:</strong> Be specific about what you want. Examples: "Remove background", "Change to oil painting style", "Make brighter and sharper"
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* LoRA Style Selector - only show when multiple images */}
                        {selectedFiles.length >= 2 && (
                            <div className="mt-4 p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    🎨 LoRA Style (for multi-image fusion)
                                </label>
                                <select
                                    value={selectedLoRA}
                                    onChange={(e) => setSelectedLoRA(e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                >
                                    {LORA_STYLES.map(style => (
                                        <option key={style} value={style}>{style}</option>
                                    ))}
                                </select>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                    Used for fusion between multiple images
                                </p>
                            </div>
                        )}

                        <button
                            onClick={handleStartEnhancement}
                            disabled={selectedFiles.length === 0 || isProcessing}
                            className="w-full mt-4 px-6 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all flex items-center justify-center gap-2"
                        >
                            {isProcessing ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    Start Enhancement
                                </>
                            )}
                        </button>
                    </div>

                    {/* Task Status */}
                    {tasks.length > 0 && (
                        <div className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                                Processing Status
                            </h3>
                            <div className="space-y-3">
                                {tasks.map((task, index) => (
                                    <div key={task.taskId} className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                                Task {index + 1}
                                            </span>
                                            {task.status === 'completed' && (
                                                <CheckCircle className="w-5 h-5 text-green-500" />
                                            )}
                                            {task.status === 'failed' && (
                                                <AlertCircle className="w-5 h-5 text-red-500" />
                                            )}
                                            {(task.status === 'pending' || task.status === 'processing') && (
                                                <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
                                            )}
                                        </div>

                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 transition-all duration-300"
                                                    style={{ width: `${task.progress}%` }}
                                                />
                                            </div>
                                            <span className="text-xs text-gray-600 dark:text-gray-400">
                                                {task.progress}%
                                            </span>
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                                                {task.status}
                                            </span>
                                            {task.status === 'completed' && task.result_url && (
                                                <button
                                                    onClick={() => downloadResult(task.taskId, task.result_url!)}
                                                    className="text-xs px-3 py-1 rounded-lg bg-primary-500 text-white hover:bg-primary-600 transition-colors"
                                                >
                                                    Download
                                                </button>
                                            )}
                                        </div>

                                        {task.error && (
                                            <p className="text-xs text-red-500 mt-2">{task.error}</p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Preview Section */}
                <div className="space-y-6">
                    <div className="p-8 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                            {tasks.length > 0 && tasks.some(t => t.status === 'completed') ? '✨ Result' : 'Preview'}
                        </h3>

                        {/* Show completed results if available */}
                        {tasks.length > 0 && tasks.some(t => t.status === 'completed' && t.result_url) ? (
                            <div className="space-y-4">
                                <div className="grid grid-cols-1 gap-4">
                                    {tasks.filter(t => t.status === 'completed' && t.result_url).map((task, index) => {
                                        const imageUrl = `http://localhost:8000${task.result_url}`;
                                        console.log('Rendering result image:', imageUrl);

                                        return (
                                            <div key={task.taskId} className="relative group">
                                                <div className="aspect-video rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-700 border-2 border-green-500">
                                                    <img
                                                        src={imageUrl}
                                                        alt={`Result ${index + 1}`}
                                                        className="w-full h-full object-contain"
                                                        onLoad={() => console.log('Image loaded:', imageUrl)}
                                                        onError={(e) => console.error('Image load error:', imageUrl, e)}
                                                    />
                                                </div>
                                                <div className="absolute top-2 left-2 px-2 py-1 rounded bg-green-500 text-white text-xs font-semibold">
                                                    Result {index + 1}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ) : selectedFiles.length > 0 ? (
                            <div className="space-y-4">
                                {/* Main preview */}
                                <div className="aspect-video rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-700">
                                    <img
                                        src={getPreviewUrl(selectedFiles[0])}
                                        alt="Preview"
                                        className="w-full h-full object-contain"
                                    />
                                </div>

                                {/* Thumbnails */}
                                {selectedFiles.length > 1 && (
                                    <div className="grid grid-cols-4 gap-2">
                                        {selectedFiles.slice(0, 4).map((file, index) => (
                                            <div key={index} className="aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
                                                <img
                                                    src={getPreviewUrl(file)}
                                                    alt={`Thumb ${index}`}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                        ))}
                                        {selectedFiles.length > 4 && (
                                            <div className="aspect-square rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                                                <span className="text-sm font-semibold text-gray-600 dark:text-gray-400">
                                                    +{selectedFiles.length - 4}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="aspect-video rounded-xl bg-gray-100 dark:bg-gray-700 flex flex-col items-center justify-center">
                                <ImageIcon className="w-16 h-16 text-gray-400 dark:text-gray-500 mb-2" />
                                <p className="text-gray-500 dark:text-gray-400">
                                    No images selected
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Info Card */}
                    {selectedFiles.length > 0 && (
                        <div className="p-6 rounded-xl bg-gradient-to-br from-primary-50 to-accent-50 dark:from-primary-900/20 dark:to-accent-900/20 border border-primary-200 dark:border-primary-800">
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                                🚀 Ready to enhance
                            </h4>
                            <div className="space-y-1 text-sm text-gray-600 dark:text-gray-300">
                                <p>• {selectedFiles.length} image(s) selected</p>
                                <p>• Mode: {useQuickOptions ? 'Quick Options' : 'Custom Prompt'}</p>
                                {useQuickOptions && (
                                    <p>• Options: {Object.entries(quickOptions).filter(([_, v]) => v).map(([k]) => k).join(', ') || 'None'}</p>
                                )}
                                <p className="pt-2 border-t border-primary-200 dark:border-primary-700 font-medium">
                                    API: {selectedFiles.length === 1 ? '⚡ Fast Edit (8 steps)' : `🎨 LoRA Fusion (${selectedLoRA})`}
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Enhancement;
