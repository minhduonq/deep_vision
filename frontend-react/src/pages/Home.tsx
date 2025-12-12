import { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Loader2, Bot, User, Upload, X } from 'lucide-react';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiClient } from '@/api/client';

interface Message {
    id: number;
    role: 'user' | 'assistant';
    message: string;
    timestamp: string;
    extra_data?: {
        task_id?: string;
        task_type?: string;
        result_url?: string;
        has_image?: boolean;
    };
}

interface ChatResponse {
    message: string;
    session_id: string;
    task_id?: string;
    task_type?: string;
    requires_image?: boolean;
    status: string;
    result_url?: string;
    timestamp: string;
}

const Home = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 0,
            role: 'assistant',
            message: `👋 Xin chào! Tôi là trợ lý AI của Deep Vision. Tôi có thể giúp bạn:

• 🎨 **Tạo hình ảnh** từ mô tả văn bản (không cần ảnh gốc)
• ✨ **Cải thiện chất lượng** hình ảnh (tải ảnh + mô tả)
• 🔍 **Làm nét** hình ảnh bị mờ (tải ảnh lên)
• 🧹 **Xóa đối tượng** không mong muốn (tải ảnh + mô tả)
• 🎨 **Chỉnh sửa** hình ảnh theo prompt (tải ảnh + mô tả thay đổi)

Hãy cho tôi biết bạn muốn làm gì! Đừng quên tải ảnh lên bằng nút 📎 nếu cần.`,
            timestamp: new Date().toISOString(),
        },
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string>('');
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Auto scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Poll task status for async operations
    const pollTaskStatus = (taskId: string) => {
        const pollInterval = setInterval(async () => {
            try {
                const statusData = await apiClient.get<any>(`/api/v1/chat-agent/status/${taskId}`);

                if (statusData.status === 'completed' && statusData.result_url) {
                    clearInterval(pollInterval);

                    // Add completion message with image
                    const completionMessage: Message = {
                        id: Date.now(),
                        role: 'assistant',
                        message: '✅ Đã hoàn thành! Đây là kết quả:',
                        timestamp: new Date().toISOString(),
                        extra_data: {
                            task_id: taskId,
                            result_url: statusData.result_url,
                        },
                    };
                    setMessages((prev) => [...prev, completionMessage]);
                    toast.success('Task completed!');
                } else if (statusData.status === 'failed') {
                    clearInterval(pollInterval);
                    toast.error(statusData.error || 'Task failed');
                }
            } catch (error) {
                console.error('Error polling task status:', error);
            }
        }, 2000);

        // Timeout after 5 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
        }, 300000);
    };

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!inputMessage.trim() && !selectedImage) {
            toast.error('Please enter a message or select an image');
            return;
        }

        setIsLoading(true);

        try {
            const userMessage: Message = {
                id: Date.now(),
                role: 'user',
                message: inputMessage,
                timestamp: new Date().toISOString(),
                extra_data: {
                    has_image: !!selectedImage,
                },
            };
            setMessages((prev) => [...prev, userMessage]);

            const formData = new FormData();
            formData.append('message', inputMessage);
            if (sessionId) {
                formData.append('session_id', sessionId);
            }
            if (selectedImage) {
                formData.append('image', selectedImage);
            }

            const data = await apiClient.post<ChatResponse>(
                '/api/v1/chat-agent/message',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }
            );

            if (data.session_id && !sessionId) {
                setSessionId(data.session_id);
            }

            const assistantMessage: Message = {
                id: Date.now() + 1,
                role: 'assistant',
                message: data.message,
                timestamp: data.timestamp,
                extra_data: {
                    task_id: data.task_id,
                    task_type: data.task_type,
                    result_url: data.result_url,
                },
            };
            setMessages((prev) => [...prev, assistantMessage]);

            // If there's a task that needs processing, poll for completion
            if (data.task_id && data.status === 'processing') {
                pollTaskStatus(data.task_id);
            }

            setInputMessage('');
            removeImage();
        } catch (error: any) {
            console.error('Error sending message:', error);
            toast.error(error.response?.data?.detail || 'Failed to send message');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                        <Bot className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                            AI Assistant
                        </h1>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Powered by Deep Vision
                        </p>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'
                            }`}
                    >
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0">
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                        )}

                        <div
                            className={`max-w-2xl rounded-2xl px-4 py-3 ${msg.role === 'user'
                                ? 'bg-primary-500 text-white'
                                : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                                }`}
                        >
                            <div className={`prose ${msg.role === 'user' ? 'prose-invert' : 'dark:prose-invert'} max-w-none`}>
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    components={{
                                        // Customize heading styles
                                        h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-2" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-xl font-bold mb-2" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="text-lg font-bold mb-1" {...props} />,
                                        // Customize list styles
                                        ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1" {...props} />,
                                        ol: ({ node, ...props }) => <ol className="list-decimal pl-5 space-y-1" {...props} />,
                                        // Customize code blocks
                                        code: ({ node, inline, ...props }: any) =>
                                            inline ? (
                                                <code className="px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-sm font-mono" {...props} />
                                            ) : (
                                                <code className="block p-3 rounded-lg bg-gray-100 dark:bg-gray-900 text-sm font-mono overflow-x-auto" {...props} />
                                            ),
                                        // Customize links
                                        a: ({ node, ...props }) => (
                                            <a className="text-primary-600 dark:text-primary-400 underline hover:text-primary-700" target="_blank" rel="noopener noreferrer" {...props} />
                                        ),
                                        // Customize blockquotes
                                        blockquote: ({ node, ...props }) => (
                                            <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic" {...props} />
                                        ),
                                        // Customize paragraphs
                                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                    }}
                                >
                                    {msg.message}
                                </ReactMarkdown>
                            </div>

                            {msg.extra_data?.has_image && (
                                <div className="mt-2 flex items-center gap-2 text-sm opacity-75">
                                    <ImageIcon className="w-4 h-4" />
                                    <span>Image attached</span>
                                </div>
                            )}

                            {msg.extra_data?.task_id && !msg.extra_data?.result_url && (
                                <div className="mt-2 flex items-center gap-2 text-sm">
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    <span>Processing...</span>
                                </div>
                            )}

                            {msg.extra_data?.result_url && (
                                <div className="mt-3">
                                    <img
                                        src={`http://localhost:8000${msg.extra_data.result_url}`}
                                        alt="Result"
                                        className="rounded-lg max-w-full h-auto border border-gray-200 dark:border-gray-700"
                                    />
                                </div>
                            )}

                            <div
                                className={`text-xs mt-2 ${msg.role === 'user'
                                    ? 'text-primary-100'
                                    : 'text-gray-500 dark:text-gray-400'
                                    }`}
                            >
                                {new Date(msg.timestamp).toLocaleTimeString()}
                            </div>
                        </div>

                        {msg.role === 'user' && (
                            <div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center flex-shrink-0">
                                <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                            </div>
                        )}
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
                {imagePreview && (
                    <div className="mb-3 relative inline-block">
                        <img
                            src={imagePreview}
                            alt="Preview"
                            className="h-20 w-20 object-cover rounded-lg border-2 border-primary-500"
                        />
                        <button
                            onClick={removeImage}
                            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-white hover:bg-red-600"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex gap-3">
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageSelect}
                        className="hidden"
                    />

                    <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="flex-shrink-0 w-12 h-12 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 flex items-center justify-center transition-colors"
                        disabled={isLoading}
                    >
                        <Upload className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                    </button>

                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Ask me anything... (e.g., 'Generate a sunset image' or 'Enhance this photo')"
                        className="flex-1 px-4 py-3 rounded-xl bg-gray-100 dark:bg-gray-700 border-0 focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                        disabled={isLoading}
                    />

                    <button
                        type="submit"
                        disabled={isLoading || (!inputMessage.trim() && !selectedImage)}
                        className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 hover:shadow-lg hover:shadow-primary-500/50 flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 text-white animate-spin" />
                        ) : (
                            <Send className="w-5 h-5 text-white" />
                        )}
                    </button>
                </form>

                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                    AI can make mistakes. Check important info.
                </p>
            </div>
        </div>
    );
};

export default Home;
