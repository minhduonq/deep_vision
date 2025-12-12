import { useState } from 'react';
import { useAuth as useAuthContext } from '@/contexts/AuthContext';

// Re-export useAuth from AuthContext for direct usage
export { useAuth } from '@/contexts/AuthContext';

interface LoginCredentials {
    username: string;
    password: string;
}

interface RegisterData {
    username: string;
    email: string;
    password: string;
    fullName?: string;
}

export const useLogin = () => {
    const { login } = useAuthContext();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (credentials: LoginCredentials) => {
        setIsLoading(true);
        setError(null);

        try {
            await login(credentials.username, credentials.password);
            return true;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Login failed');
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    return {
        login: handleLogin,
        isLoading,
        error,
    };
};

export const useRegister = () => {
    const { register } = useAuthContext();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRegister = async (data: RegisterData) => {
        setIsLoading(true);
        setError(null);

        try {
            await register(data);
            return true;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Registration failed');
            return false;
        } finally {
            setIsLoading(false);
        }
    };

    return {
        register: handleRegister,
        isLoading,
        error,
    };
};

export const useLogout = () => {
    const { logout } = useAuthContext();

    return {
        logout,
    };
};
