const apiHost = typeof window !== 'undefined' 
  ? (window.location.hostname === 'localhost' ? '127.0.0.1' : window.location.hostname) 
  : '127.0.0.1';

export const API_BASE_URL = `http://${apiHost}:8001/api`;
