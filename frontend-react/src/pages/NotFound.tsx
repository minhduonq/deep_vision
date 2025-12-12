import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const NotFound = () => {
    return (
        <div className="min-h-[60vh] flex items-center justify-center">
            <div className="text-center space-y-6 animate-fade-in">
                <div className="text-9xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                    404
                </div>

                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Page Not Found
                </h1>

                <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                    The page you're looking for doesn't exist or has been moved.
                </p>

                <div className="flex gap-4 justify-center pt-4">
                    <Link
                        to="/"
                        className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-105"
                    >
                        <Home className="w-5 h-5" />
                        <span>Go Home</span>
                    </Link>

                    <button
                        onClick={() => window.history.back()}
                        className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span>Go Back</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NotFound;
