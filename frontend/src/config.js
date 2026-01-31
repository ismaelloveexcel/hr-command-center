/**
 * Frontend configuration
 * 
 * Loads environment variables with fallback defaults for development.
 */

// API Base URL - loaded from environment variable or defaults to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const config = {
  apiUrl: API_URL,
};

export default config;
