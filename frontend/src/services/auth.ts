import axios from 'axios';
import { API_URL } from './api';

export const login = async (email: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}/token/`, {
      email,
      password,
    });

    if (response.data.access && response.data.refresh) {
      return {
        access: response.data.access,
        refresh: response.data.refresh,
      };
    } else {
      throw new Error('Login failed: Access or refresh token not received.');
    }
  } catch (error: unknown) {
    // Type guard to check if the error is an instance of Error
    if (error instanceof Error) {
      throw new Error(`Login failed: ${error.message}`);
    } else {
      throw new Error('Login failed: An unknown error occurred.');
    }
  }
};

export const signup = async (formData: FormData) => {
  try {
    const response = await axios.post(`${API_URL}/auth/signup/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: unknown) {
    // Type guard to check if the error is an instance of Error
    if (error instanceof Error) {
      throw new Error(`Signup failed: ${error.message}`);
    } else {
      throw new Error('Signup failed: An unknown error occurred.');
    }
  }
};

// Optional: You can re-add the logout function if necessary
// export const logout = () => { /* Handle logout */ };
