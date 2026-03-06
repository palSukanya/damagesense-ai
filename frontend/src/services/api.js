import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const damageAPI = {
  healthCheck: () => api.get('/health'),

  analyzeDamage: async (imageFile, vehicleId, inspectionType = 'general', checkHistory = true) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('vehicle_id', vehicleId);
    formData.append('inspection_type', inspectionType);
    formData.append('check_history', checkHistory);

    return api.post('/api/v1/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  checkImageQuality: async (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);

    return api.post('/api/v1/quality-check', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export default api;