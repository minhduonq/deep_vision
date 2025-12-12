import { useState } from 'react';
import { Wand2, Loader2, Download, AlertCircle } from 'lucide-react';
import { apiClient } from '@/api/client';
import type { Task, AspectRatio } from '@/types';

const Generation = () => {
    const [prompt, setPrompt] = useState('');
    const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1');
    const [steps, setSteps] = useState(8);  // FLUX.1-schnell max is 16
    const [guidance, setGuidance] = useState(3.5);  // FLUX uses lower guidance (1.0-10.0)

    const [isGenerating, setIsGenerating] = useState(false);
    const [task, setTask] = useState<Task | null>(null);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (!prompt.trim()) return;

        setIsGenerating(true);
        setError(null);
        setGeneratedImage(null);

        try {
            // Validate inputs
            const validatedRequest = {
                prompt: prompt.trim(),
                aspect_ratio: aspectRatio,
                num_inference_steps: Math.min(Math.max(steps, 1), 16),
                guidance_scale: Math.min(Math.max(guidance, 1.0), 10.0),
            };

            console.log('Sending generation request:', validatedRequest);

            // Call generation API
            const response = await apiClient.generateImage(validatedRequest);

            console.log('Generation response:', response);
            setTask(response);

            // Poll for status
            const pollInterval = setInterval(async () => {
                try {
                    const status = await apiClient.getTaskStatus(response.task_id);
                    setTask(status);

                    if (status.status === 'completed') {
                        clearInterval(pollInterval);
                        setIsGenerating(false);

                        if (status.result_url) {
                            // Construct full URL for the image
                            const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                            setGeneratedImage(`${baseUrl}${status.result_url}`);
                        }
                    } else if (status.status === 'failed') {
                        clearInterval(pollInterval);
                        setIsGenerating(false);
                        setError(status.error || 'Generation failed');
                    }
                } catch (err) {
                    console.error('Error polling status:', err);
                }
            }, 2000); // Poll every 2 seconds

            // Timeout after 5 minutes
            setTimeout(() => {
                clearInterval(pollInterval);
                if (isGenerating) {
                    setIsGenerating(false);
                    setError('Generation timeout - please try again');
                }
            }, 300000);

        } catch (err: any) {
            console.error('Generation error:', err);
            console.error('Error response:', err.response);

            // Better error message extraction
            let errorMessage = 'Failed to generate image';
            if (err.response?.data?.detail) {
                if (Array.isArray(err.response.data.detail)) {
                    // Pydantic validation errors
                    errorMessage = err.response.data.detail
                        .map((e: any) => `${e.loc.join('.')}: ${e.msg}`)
                        .join(', ');
                } else {
                    errorMessage = err.response.data.detail;
                }
            } else if (err.message) {
                errorMessage = err.message;
            }

            setError(errorMessage);
            setIsGenerating(false);
        }
    };

    const handleDownload = () => {
        if (!generatedImage) return;

        const link = document.createElement('a');
        link.href = generatedImage;
        link.download = `generated-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg">
                    <Wand2 className="w-6 h-6 text-white" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        AI Image Generation
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400">
                        Create stunning images from text descriptions
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="grid lg:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="space-y-6">
                    <div className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Describe Your Image
                        </h3>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Prompt
                            </label>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="A beautiful sunset over mountains, highly detailed, 4k..."
                                className="w-full h-32 px-4 py-3 rounded-lg bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Aspect Ratio
                            </label>
                            <div className="grid grid-cols-5 gap-2">
                                {(['1:1', '3:4', '4:3', '16:9', '9:16'] as AspectRatio[]).map((ratio) => (
                                    <button
                                        key={ratio}
                                        type="button"
                                        onClick={() => setAspectRatio(ratio)}
                                        className={`px-3 py-2 rounded-lg border-2 transition-all ${aspectRatio === ratio
                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-semibold'
                                                : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-500'
                                            }`}
                                    >
                                        {ratio}
                                    </button>
                                ))}
                            </div>
                            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                                {aspectRatio === '1:1' && 'Square (1024×1024)'}
                                {aspectRatio === '3:4' && 'Portrait (768×1024)'}
                                {aspectRatio === '4:3' && 'Landscape (1024×768)'}
                                {aspectRatio === '16:9' && 'Widescreen (1280×720)'}
                                {aspectRatio === '9:16' && 'Vertical (720×1280)'}
                            </p>
                        </div>

                        {/* Advanced Settings */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Steps (1-16)
                                </label>
                                <input
                                    type="number"
                                    value={steps}
                                    onChange={(e) => setSteps(Number(e.target.value))}
                                    min={1}
                                    max={16}
                                    step={1}
                                    className="w-full px-4 py-2 rounded-lg bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Guidance (1.0-10.0)
                                </label>
                                <input
                                    type="number"
                                    value={guidance}
                                    onChange={(e) => setGuidance(Number(e.target.value))}
                                    min={1.0}
                                    max={10.0}
                                    step={0.5}
                                    className="w-full px-4 py-2 rounded-lg bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                                />
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                            </div>
                        )}

                        {/* Status Message */}
                        {task && isGenerating && (
                            <div className="flex items-center gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                                <div className="flex-1">
                                    <p className="text-sm text-blue-600 dark:text-blue-400">
                                        {task.status === 'pending' ? 'Starting generation...' : 'Generating image...'}
                                    </p>
                                    {task.progress > 0 && (
                                        <div className="mt-1 h-1.5 bg-blue-200 dark:bg-blue-800 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-blue-500 transition-all duration-300"
                                                style={{ width: `${task.progress}%` }}
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        <button
                            onClick={handleGenerate}
                            disabled={!prompt.trim() || isGenerating}
                            className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all flex items-center justify-center gap-2"
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Wand2 className="w-5 h-5" />
                                    Generate Image
                                </>
                            )}
                        </button>
                    </div>

                    {/* Example Prompts */}
                    <div className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 space-y-3">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Example Prompts
                        </h3>

                        {[
                            'A futuristic city with flying cars, neon lights, cyberpunk style',
                            'A cute cat wearing a space helmet, digital art',
                            'Mountain landscape at sunset, photorealistic',
                        ].map((example, index) => (
                            <button
                                key={index}
                                onClick={() => setPrompt(example)}
                                className="w-full text-left p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-sm text-gray-700 dark:text-gray-300"
                            >
                                {example}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Preview Section */}
                <div className="space-y-6">
                    <div className="p-8 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                                Generated Image
                            </h3>

                            {generatedImage && (
                                <button
                                    onClick={handleDownload}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 transition-colors"
                                >
                                    <Download className="w-4 h-4" />
                                    Download
                                </button>
                            )}
                        </div>

                        <div className="aspect-square rounded-xl bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                            {generatedImage ? (
                                <img
                                    src={generatedImage}
                                    alt="Generated"
                                    className="w-full h-full object-contain"
                                    onError={(e) => {
                                        console.error('Image load error');
                                        setError('Failed to load generated image');
                                    }}
                                />
                            ) : isGenerating ? (
                                <div className="text-center space-y-3">
                                    <Loader2 className="w-12 h-12 text-gray-400 animate-spin mx-auto" />
                                    <p className="text-gray-500 dark:text-gray-400">
                                        Creating your image...
                                    </p>
                                </div>
                            ) : (
                                <div className="text-center space-y-2">
                                    <Wand2 className="w-12 h-12 text-gray-400 mx-auto" />
                                    <p className="text-gray-500 dark:text-gray-400">
                                        No image generated yet
                                    </p>
                                    <p className="text-sm text-gray-400 dark:text-gray-500">
                                        Enter a prompt and click Generate
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Image Info */}
                        {generatedImage && task && (
                            <div className="mt-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-700 space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600 dark:text-gray-400">Aspect Ratio:</span>
                                    <span className="text-gray-900 dark:text-white">{aspectRatio}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600 dark:text-gray-400">Steps:</span>
                                    <span className="text-gray-900 dark:text-white">{steps}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600 dark:text-gray-400">Guidance:</span>
                                    <span className="text-gray-900 dark:text-white">{guidance}</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Generation;
