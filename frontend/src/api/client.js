/**
 * SAHAYAK AI - API Client
 * 
 * Handles all HTTP requests to the FastAPI backend.
 * Includes JWT token management and error handling.
 */

import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - adds auth token to every request
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handles errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid - clear and redirect
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ============================================
// Authentication API
// ============================================

export const authAPI = {
    register: async (data) => {
        const response = await api.post('/auth/register', data);
        return response.data;
    },

    login: async (email, password) => {
        const response = await api.post('/auth/login', { email, password });
        return response.data;
    },

    getMe: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    updateMe: async (data) => {
        const response = await api.put('/auth/me', data);
        return response.data;
    },
};

// ============================================
// SOS API
// ============================================

export const sosAPI = {
    // Submit SOS request and get playbook
    create: async (data) => {
        const response = await api.post('/sos/', data);
        return response.data;
    },

    // Quick SOS (no auth required for demo)
    quick: async (rawInput, subject = null, grade = null) => {
        const params = new URLSearchParams({ raw_input: rawInput });
        if (subject) params.append('subject', subject);
        if (grade) params.append('grade', grade);
        const response = await api.post(`/sos/quick?${params.toString()}`);
        return response.data;
    },

    // Get SOS history
    getHistory: async (skip = 0, limit = 10) => {
        const response = await api.get('/sos/', { params: { skip, limit } });
        return response.data;
    },

    // Get specific SOS with playbook
    getById: async (id) => {
        const response = await api.get(`/sos/${id}`);
        return response.data;
    },

    // Submit feedback
    submitFeedback: async (id, feedback) => {
        const response = await api.post(`/sos/${id}/feedback`, feedback);
        return response.data;
    },
};

// ============================================
// Dashboard API
// ============================================

export const dashboardAPI = {
    // Get teacher dashboard
    getTeacher: async () => {
        const response = await api.get('/dashboard/teacher');
        return response.data;
    },

    // Get CRP dashboard
    getCRP: async (days = 7) => {
        const response = await api.get('/dashboard/crp', { params: { days } });
        return response.data;
    },

    // Get DIET dashboard  
    getDIET: async (days = 7) => {
        const response = await api.get('/dashboard/diet', { params: { days } });
        return response.data;
    },

    // Get public overview (no auth needed)
    getOverview: async () => {
        const response = await api.get('/dashboard/overview');
        return response.data;
    },
};

export default api;
