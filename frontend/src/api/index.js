import axios from 'axios'
import { ElMessage } from 'element-plus'

// 支持环境变量配置 API 地址
// 优先级：环境变量 > 硬编码生产 URL > 相对路径（开发环境）
function getBaseUrl() {
  // 1. 尝试读取环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // 2. 生产环境硬编码回退值
  if (import.meta.env.PROD) {
    return 'https://ai-trade-platform-api.onrender.com'
  }
  
  // 3. 开发环境使用相对路径（通过 Vite proxy 转发）
  return '/api'
}

const BASE_URL = getBaseUrl()

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.detail || error.message || 'Request failed'
    ElMessage.error(msg)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ─── Auth ───
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

// ─── Generic CRUD ───
export function createAPI(prefix) {
  return {
    list: (params) => api.get(`/${prefix}`, { params }),
    get: (id) => api.get(`/${prefix}/${id}`),
    create: (data) => api.post(`/${prefix}`, data),
    update: (id, data) => api.put(`/${prefix}/${id}`, data),
    delete: (id, permanent = false) => api.delete(`/${prefix}/${id}`, { params: { permanent } }),
    restore: (id) => api.post(`/${prefix}/${id}/restore`),
    batchDelete: (ids) => api.post(`/${prefix}/batch-delete`, ids),
  }
}

// ─── AI APIs ───
export const aiAPI = {
  ocrExtract: (formData) => api.post('/ai/ocr/extract', formData),
  ocrExtractFields: (formData) => api.post('/ai/ocr/extract-fields', formData),
  translate: (data) => api.post('/ai/translate', data),
  hsRecommend: (data) => api.post('/ai/hs-recommend', data),
  contractParse: (text) => api.post('/ai/contract/parse', { contract_text: text }),
  contractParseFile: (formData) => api.post('/ai/contract/parse-file', formData),
  compareQuotes: (data) => api.post('/ai/compare-quotes', data),
  orderRisk: (data) => api.post('/ai/order/risk', data),
  creditAssess: (data) => api.post('/ai/credit/assess', data),
  naturalSearch: (data) => api.post('/ai/search', data),
  generateReport: (data) => api.post('/ai/report', data),
  documentClassify: (formData) => api.post('/ai/document/classify', formData),
  documentVerify: (formData) => api.post('/ai/document/verify', formData),
  embed: (data) => api.post('/ai/embed', data),
  imageGenerate: (formData) => api.post('/ai/image/generate', formData),
}

export default api
