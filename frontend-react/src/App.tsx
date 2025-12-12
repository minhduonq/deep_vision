import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAppStore } from './store/appStore';

// Layout
import Layout from './components/layout/Layout';

// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Home from './pages/Home';
import Enhancement from './pages/Enhancement';
import Generation from './pages/Generation';
import History from './pages/History';
import NotFound from './pages/NotFound';

function App() {
    const { theme, initTheme } = useAppStore();

    useEffect(() => {
        initTheme();
    }, [initTheme]);

    useEffect(() => {
        // Apply theme to document
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

    return (
        <Routes>
            {/* Public routes - no layout */}
            <Route index element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* App routes - with layout */}
            <Route path="/" element={<Layout />}>
                <Route path="/home" element={<Home />} />
                <Route path="enhance" element={<Enhancement />} />
                <Route path="generate" element={<Generation />} />
                <Route path="history" element={<History />} />
                <Route path="404" element={<NotFound />} />
                <Route path="*" element={<Navigate to="/404" replace />} />
            </Route>
        </Routes>
    );
}

export default App;
