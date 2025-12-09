import axios from 'axios';

// Default to localhost for development, but customizable via environment variable
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add interceptor for token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Add interceptor for response errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Handle token expiration/unauthorized access
        if (error.response && error.response.status === 401) {
            // Optional: clear token and redirect to login if not already there
            // localStorage.removeItem('token');
            // window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const auth = {
    login: (credentials) => api.post('/auth/login/', credentials),
    me: () => api.get('/auth/me/'),
};

export const query = {
    // Generic runner for all query types
    run: (type, params) => api.post(`/query/${type}/`, params),
};

export const monitoring = {
    logs: () => api.get('/logs/history/'),
    budget: () => api.get('/epsilon/status/'),
    resetBudget: () => api.post('/epsilon/reset/', { confirm: true }),
    resetPlatform: () => api.post('/platform/reset/', { confirm: true }),
    stats: () => api.get('/stats/overview/'),
};

export const data = {
    load: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/data/load/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
};

export default api;
