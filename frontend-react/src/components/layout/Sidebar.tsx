import { NavLink } from 'react-router-dom';
import { useAppStore } from '@/store/appStore';
import { Home, Sparkles, Wand2, History, X } from 'lucide-react';

const Sidebar = () => {
    const { sidebarOpen, toggleSidebar } = useAppStore();

    const navItems = [
        { to: '/home', icon: Home, label: 'Home', end: true },
        { to: '/enhance', icon: Sparkles, label: 'Enhancement' },
        { to: '/generate', icon: Wand2, label: 'Generation' },
        { to: '/history', icon: History, label: 'History' },
    ];

    return (
        <>
            {/* Overlay for mobile */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={toggleSidebar}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`fixed left-0 top-16 bottom-0 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 z-40 transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                <nav className="flex flex-col h-full p-4">
                    <div className="flex items-center justify-between mb-6 lg:hidden">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Navigation
                        </h2>
                        <button
                            onClick={toggleSidebar}
                            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            return (
                                <NavLink
                                    key={item.to}
                                    to={item.to}
                                    end={item.end}
                                    onClick={() => {
                                        // Close sidebar on mobile after navigation
                                        if (window.innerWidth < 1024) {
                                            toggleSidebar();
                                        }
                                    }}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${isActive
                                            ? 'bg-gradient-to-r from-primary-500 to-accent-500 text-white shadow-lg shadow-primary-500/50'
                                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                                        }`
                                    }
                                >
                                    {({ isActive }) => (
                                        <>
                                            <Icon
                                                className={`w-5 h-5 ${isActive ? 'text-white' : ''
                                                    }`}
                                            />
                                            <span className="font-medium">{item.label}</span>
                                        </>
                                    )}
                                </NavLink>
                            );
                        })}
                    </div>

                    {/* Footer info */}
                    <div className="mt-auto pt-6 border-t border-gray-200 dark:border-gray-700">
                        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                            <p className="font-medium">Deep Vision v1.0</p>
                            <p>AI-powered image processing</p>
                        </div>
                    </div>
                </nav>
            </aside>
        </>
    );
};

export default Sidebar;
