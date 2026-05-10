import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  res => res.data,
  err => Promise.reject(err.response?.data?.error ?? err.message ?? 'Bir hata oluştu')
);

export const dashboardApi = {
  get: () => api.get('/dashboard'),
};

export const productsApi = {
  getAll:  (params) => api.get('/products', { params }),
  getById: (id)     => api.get(`/products/${id}`),
  create:  (data)   => api.post('/products', data),
  update:  (id, d)  => api.put(`/products/${id}`, d),
  remove:  (id)     => api.delete(`/products/${id}`),
};

export const categoriesApi = {
  getAll:  ()        => api.get('/categories'),
  create:  (data)    => api.post('/categories', data),
  update:  (id, d)   => api.put(`/categories/${id}`, d),
  remove:  (id)      => api.delete(`/categories/${id}`),
};

export const movementsApi = {
  getAll:  (params)  => api.get('/movements', { params }),
  create:  (data)    => api.post('/movements', data),
};

export default api;
