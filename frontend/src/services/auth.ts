// frontend/src/services/auth.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const login = async (email: string, password: string) => {
    const response = await axios.post(`${API_URL}/token/`, {
        email,
        password,
    });
    if (response.data.access) {
        localStorage.setItem('token', response.data.access);
    }
    return response.data;
};

export const signup = async (email: string, username: string, password: string) => {
    const response = await axios.post(`${API_URL}/users/`, {
        email,
        username,
        password,
    });
    return response.data;
};

export const logout = () => {
    localStorage.removeItem('token');
};

export const getCurrentUser = () => {
    return localStorage.getItem('token');
};
