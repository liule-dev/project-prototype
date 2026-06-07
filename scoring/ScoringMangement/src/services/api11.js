import axios from 'axios'

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api1', // Django 后端地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证 token
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
apiClient.interceptors.response.use(
  (response) => {
    // 处理响应数据的字符编码问题
    if (response.data && typeof response.data === 'string') {
      try {
        // 尝试修复可能的编码问题
        response.data = decodeURIComponent(escape(response.data));
      } catch (e) {
        console.warn('字符编码修复失败:', e);
      }
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // 处理未授权错误
      // 例如：重定向到登录页
      console.error('用户未授权访问该资源')
    }
    return Promise.reject(error)
  }
)

export default apiClient