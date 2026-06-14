import axios from 'axios'
import { ElMessage } from 'element-plus'

// 直接硬编码后端地址，不做任何判断
const BASE_URL = 'https://ai-trade-platform-api.onrender.com/api'
console.log('[API v3] 硬编码 BASE_URL:', BASE_URL)

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

// Request interceptor - 记录每次请求的完整 URL
api.interceptors.request.use((config) => {
  const fullUrl = (config.baseURL || '') + (config.url || '')
  console.log('[API] 📤', config.method?.toUpperCase(), fullUrl)
  
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - 详细的错误日志
api.interceptors.response.use(
  (response) => {
    console.log('[API] ✅', response.config.method?.toUpperCase(), response.config.url, response.status)
    return response.data
  },
  (error) => {
    const fullUrl = (error.config?.baseURL || '') + (error.config?.url || '')
    const status = error.response?.status || 'NETWORK_ERROR'
    console.error('[API] ❌', status, fullUrl, error.response?.data || error.message)
    
    const msg = `${status}: ${error.response?.data?.detail || error.message}`
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
