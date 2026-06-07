import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api11 = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', // 从环境变量获取API地址
  timeout: 10000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api11.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api11.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 详细错误处理
    console.error('API请求错误:', error)

    // 处理网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    }
    // 处理认证错误
    else if (error.response.status === 401) {
      // 未授权，可能需要重新登录
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    // 处理其他错误
    else {
      const errorMsg = error.response.data?.detail || error.response.data?.message || '请求失败'
      ElMessage.error(`请求错误: ${errorMsg}`)
    }

    return Promise.reject(error)
  }
)

export default api11
