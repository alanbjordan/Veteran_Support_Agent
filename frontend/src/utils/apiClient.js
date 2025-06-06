// client/src/utils/apiClient.js

import axios from 'axios';

// API URLs configuration
const BACKUP_API_URL ='http://localhost:5001/api'; // Backup API URL from environment variables or fallback
const DEFAULT_API_URL = process.env.REACT_APP_API_URL || BACKUP_API_URL; // Default API URL from environment variables or fallback
// Check if the environment variable is set
if (!process.env.REACT_APP_API_URL) {
  console.warn('REACT_APP_API_URL is not set. Falling back to localhost.');
}
// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS with credentials
});

// Add a request interceptor to add the auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    // Get the token from localStorage
    const token = localStorage.getItem('auth_token');
    
    // If token exists, add it to the Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add userUUID to headers if available
    const userUUID = localStorage.getItem('userUUID');
    if (userUUID) {
      config.headers.userUUID = userUUID;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors and retry logic
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle 401 Unauthorized errors (token expired or invalid)
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('userUUID');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Check if error is network-related (server unreachable)
    if (
      error.code === 'ECONNABORTED' ||
      error.message === 'Network Error' ||
      (!error.response && error.config)
    ) {
      const originalConfig = error.config;
      // Prevent infinite loops by marking the config that it's been retried
      if (!originalConfig._retry) {
        originalConfig._retry = true;
        // Change the baseURL to the backup URL
        originalConfig.baseURL = BACKUP_API_URL;
        // Reattempt the request with the new configuration
        return apiClient(originalConfig);
      }
    }
    
    return Promise.reject(error);
  }
);


export default apiClient; 