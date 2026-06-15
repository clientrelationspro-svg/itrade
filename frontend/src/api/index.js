import axios from 'axios'
import { ElMessage } from 'element-plus'

// 开发环境使用本地代理，生产环境使用部署地址
const BASE_URL = import.meta.env.DEV ? '/api' : 'https://ai-trade-platform-api.onrender.com/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // 清理请求体：空字符串 → null（避免 Decimal 等类型验证报错）
  if (config.data && typeof config.data === 'object' && !(config.data instanceof FormData)) {
    config.data = JSON.parse(JSON.stringify(config.data, (key, value) => value === '' ? null : value))
  }
  return config
})

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
  websiteAnalyze: (data) => api.post('/ai/website/analyze', data),
  webSearch: (data) => api.post('/ai/web-search', data),
  smartFill: (data) => api.post('/ai/smart-fill', data),
  configStatus: () => api.get('/ai/config/status'),
}

export default api
