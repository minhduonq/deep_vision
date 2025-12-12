import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { HistoryItem, TaskType } from '@/types';

interface AppState {
    // Theme
    theme: 'light' | 'dark';
    toggleTheme: () => void;
    setTheme: (theme: 'light' | 'dark') => void;
    initTheme: () => void;

    // History
    history: HistoryItem[];
    addToHistory: (item: HistoryItem) => void;
    removeFromHistory: (id: string) => void;
    clearHistory: () => void;

    // Current Task
    currentTaskId: string | null;
    setCurrentTaskId: (id: string | null) => void;

    // UI State
    sidebarOpen: boolean;
    toggleSidebar: () => void;
    setSidebarOpen: (open: boolean) => void;

    // Settings
    settings: {
        autoSaveHistory: boolean;
        showMetadata: boolean;
        enableComparison: boolean;
        maxHistoryItems: number;
    };
    updateSettings: (settings: Partial<AppState['settings']>) => void;
}

export const useAppStore = create<AppState>()(
    persist(
        (set, get) => ({
            // Theme
            theme: 'light',
            toggleTheme: () => {
                const newTheme = get().theme === 'light' ? 'dark' : 'light';
                set({ theme: newTheme });

                // Update document class
                if (newTheme === 'dark') {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
            },
            setTheme: theme => {
                set({ theme });
                if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
            },
            initTheme: () => {
                const theme = get().theme;
                if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
            },

            // History
            history: [],
            addToHistory: item => {
                const { history, settings } = get();
                const newHistory = [item, ...history].slice(0, settings.maxHistoryItems);
                set({ history: newHistory });
            },
            removeFromHistory: id => {
                set(state => ({
                    history: state.history.filter(item => item.id !== id),
                }));
            },
            clearHistory: () => set({ history: [] }),

            // Current Task
            currentTaskId: null,
            setCurrentTaskId: id => set({ currentTaskId: id }),

            // UI State
            sidebarOpen: true,
            toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
            setSidebarOpen: open => set({ sidebarOpen: open }),

            // Settings
            settings: {
                autoSaveHistory: true,
                showMetadata: true,
                enableComparison: true,
                maxHistoryItems: 20,
            },
            updateSettings: newSettings =>
                set(state => ({
                    settings: { ...state.settings, ...newSettings },
                })),
        }),
        {
            name: 'deep-vision-storage',
            partialize: state => ({
                theme: state.theme,
                history: state.history,
                settings: state.settings,
            }),
        }
    )
);

// Initialize theme on load
if (typeof window !== 'undefined') {
    const storedTheme = useAppStore.getState().theme;
    if (storedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }
}
