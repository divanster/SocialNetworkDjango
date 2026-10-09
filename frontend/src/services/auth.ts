import axios from 'axios';
import { API_URL } from './api';

const extractErrorMessage = (error: unknown, fallback: string): string => {
  if (axios.isAxiosError(error)) {
    const responseData = error.response?.data;
    if (typeof responseData?.detail === 'string') {
      return responseData.detail;
    }
    if (responseData && typeof responseData === 'object') {
      const firstField = Object.values(responseData)[0];
      if (Array.isArray(firstField) && firstField.length > 0) {
        return String(firstField[0]);
      }
      if (typeof firstField === 'string') {
        return firstField;
      }
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
};

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
    throw new Error(`Login failed: ${extractErrorMessage(error, 'An unknown error occurred.')}`);
  }
};

type SignupPayload = {
  email: string;
  username: string;
  password: string;
  password2: string;
  profile?: {
    first_name?: string;
    last_name?: string;
    gender?: string;
    date_of_birth?: string;
    bio?: string;
    phone?: string;
    town?: string;
    country?: string;
    relationship_status?: string;
  };
};

export const signup = async (payload: SignupPayload) => {
  try {
    const response = await axios.post(`${API_URL}/users/signup/`, payload);
    return response.data;
  } catch (error: unknown) {
    throw new Error(`Signup failed: ${extractErrorMessage(error, 'An unknown error occurred.')}`);
  }
};

// Optional: You can re-add the logout function if necessary
// export const logout = () => { /* Handle logout */ };
