import { useState, useEffect } from 'react';
import { History as HistoryIcon, MessageSquare, Image as ImageIcon, Clock, CheckCircle, XCircle, Loader2, Calendar, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { apiClient } from '@/api/client';

interface TaskHistoryItem {
    id: number;
    task_id: string;
    task_type: string;
    prompt: string | null;
    status: string;
    result_url: string | null;
    error_message: string | null;
    created_at: string;
    completed_at: string | null;
}

interface ChatSessionItem {
    session_id: string;
    title: string;
    task_type: string;
    message_count: number;
    last_message: string;
    last_timestamp: string;
    created_at: string;
}

interface HistoryData {
    tasks: TaskHistoryItem[];
    sessions: ChatSessionItem[];
    total_tasks: number;
    total_sessions: number;
}

const History = () => {
    const [historyData, setHistoryData] = useState<HistoryData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'tasks' | 'chats'>('tasks');
    const [filterStatus, setFilterStatus] = useState<string>('all');
    const [filterType, setFilterType] = useState<string>('all');

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            setIsLoading(true);
            const data = await apiClient.get<HistoryData>('/api/v1/history/');
            setHistoryData(data ?? null);
        } catch (error: any) {
            console.error('Error fetching history:', error);
            toast.error(error.response?.data?.detail || 'Failed to load history');
        } finally {
            setIsLoading(false);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'failed':
                return <XCircle className="w-5 h-5 text-red-500" />;
            case 'processing':
                return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
            default:
                return <Clock className="w-5 h-5 text-gray-500" />;
        }
    };

    const getTaskTypeLabel = (type: string) => {
        const labels: Record<string, string> = {
            generate: '🎨 Generation',
            enhance: '✨ Enhancement',
            edit: '🖌️ Edit',
            deblur: '🔍 Deblur',
            inpaint: '🧹 Inpaint',
        };
        return labels[type] || type;
    };

    const filteredTasks = historyData?.tasks.filter(task => {
        if (filterStatus !== 'all' && task.status !== filterStatus) return false;
        if (filterType !== 'all' && task.task_type !== filterType) return false;
        return true;
    }) || [];

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-lg">
                        <HistoryIcon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            History
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400">
                            {historyData ? `${historyData.total_tasks} tasks, ${historyData.total_sessions} chat sessions` : 'Loading...'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-4 border-b border-gray-200 dark:border-gray-700">
                <button
                    onClick={() => setActiveTab('tasks')}
                    className={`px-6 py-3 font-semibold transition-all ${activeTab === 'tasks'
                        ? 'border-b-2 border-primary-500 text-primary-600 dark:text-primary-400'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                        }`}
                >
                    <div className="flex items-center gap-2">
                        <ImageIcon className="w-5 h-5" />
                        <span>Tasks ({historyData?.total_tasks || 0})</span>
                    </div>
                </button>
                <button
                    onClick={() => setActiveTab('chats')}
                    className={`px-6 py-3 font-semibold transition-all ${activeTab === 'chats'
                        ? 'border-b-2 border-primary-500 text-primary-600 dark:text-primary-400'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                        }`}
                >
                    <div className="flex items-center gap-2">
                        <MessageSquare className="w-5 h-5" />
                        <span>Chat Sessions ({historyData?.total_sessions || 0})</span>
                    </div>
                </button>
            </div>

            {/* Loading State */}
            {isLoading && (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
                </div>
            )}

            {/* Tasks Tab */}
            {!isLoading && activeTab === 'tasks' && (
                <div className="space-y-4">
                    {/* Filters */}
                    <div className="flex gap-4 p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-2">
                            <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters:</span>
                        </div>
                        <select
                            value={filterStatus}
                            onChange={(e) => setFilterStatus(e.target.value)}
                            className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 border-0 text-sm"
                        >
                            <option value="all">All Status</option>
                            <option value="completed">Completed</option>
                            <option value="processing">Processing</option>
                            <option value="failed">Failed</option>
                        </select>
                        <select
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                            className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 border-0 text-sm"
                        >
                            <option value="all">All Types</option>
                            <option value="generate">Generation</option>
                            <option value="enhance">Enhancement</option>
                            <option value="edit">Edit</option>
                            <option value="deblur">Deblur</option>
                        </select>
                    </div>

                    {/* Tasks List */}
                    {filteredTasks.length === 0 ? (
                        <div className="p-12 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-center">
                            <ImageIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                No Tasks Yet
                            </h3>
                            <p className="text-gray-600 dark:text-gray-400">
                                Your processed images will appear here
                            </p>
                        </div>
                    ) : (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredTasks.map((task) => (
                                <div
                                    key={task.id}
                                    className="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all"
                                >
                                    {/* Task Image */}
                                    {task.result_url ? (
                                        <div className="aspect-video rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 mb-3">
                                            <img
                                                src={`http://localhost:8000${task.result_url}`}
                                                alt={task.task_type}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                    ) : (
                                        <div className="aspect-video rounded-lg bg-gray-100 dark:bg-gray-700 mb-3 flex items-center justify-center">
                                            <ImageIcon className="w-12 h-12 text-gray-400" />
                                        </div>
                                    )}

                                    {/* Task Info */}
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                                                {getTaskTypeLabel(task.task_type)}
                                            </span>
                                            {getStatusIcon(task.status)}
                                        </div>

                                        {task.prompt && (
                                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                                                {task.prompt}
                                            </p>
                                        )}

                                        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500">
                                            <Calendar className="w-4 h-4" />
                                            <span>{formatDate(task.created_at)}</span>
                                        </div>

                                        {task.error_message && (
                                            <p className="text-xs text-red-500 mt-2">{task.error_message}</p>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Chat Sessions Tab */}
            {!isLoading && activeTab === 'chats' && (
                <div className="space-y-4">
                    {historyData?.sessions.length === 0 ? (
                        <div className="p-12 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-center">
                            <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                                No Chat History Yet
                            </h3>
                            <p className="text-gray-600 dark:text-gray-400">
                                Your conversations will appear here
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {historyData?.sessions.map((session) => (
                                <div
                                    key={session.session_id}
                                    className="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-all cursor-pointer"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0">
                                            <MessageSquare className="w-5 h-5 text-white" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between mb-2">
                                                <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                                                    {session.title}
                                                </h3>
                                                <span className="text-xs text-gray-500 dark:text-gray-500">
                                                    {formatDate(session.last_timestamp)}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                                                {session.last_message}
                                            </p>
                                            <div className="flex items-center gap-2 mt-2">
                                                <span className="text-xs px-2 py-1 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
                                                    {getTaskTypeLabel(session.task_type)}
                                                </span>
                                                <span className="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                                                    {session.message_count} messages
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default History;
