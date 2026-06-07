import axios from 'axios'

const apiClient = axios.create({
     baseURL: 'http://127.0.0.1:8000/',
    timeout: 5000,
});


apiClient.interceptors.request.use(config => {
    // 只有在不是注册和发送验证码的请求中才添加认证头
    const isPublicRoute = config.url.includes('/send_code/') || config.url.includes('/login/register1/');

    if (!isPublicRoute) {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
},error => {
    return Promise.reject(error);
});

apiClient.interceptors.response.use(config => {
    return config;
},async error => {

    if (error.response && error.response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        try {
            const response = await apiClient.post('/api1/token/refresh/', {refresh: refreshToken})
            localStorage.setItem('access_token', response.data.access)
            if (response.data.refresh) {
                localStorage.setItem('refresh_token', response.data.refresh)
            }
            error.config.headers.Authorization = `Bearer ${response.data.access}`

            return apiClient(error.config)
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});

// 登录请求接口类型定义
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应接口类型定义
export interface LoginResponse {
  refresh: string
  access: string
  user: {
    id: number
    username: string
    role: string
  }
}

// 通知接口类型定义
export interface Notification {
  id: number
  title: string
  content: string
  type: string
  is_read: boolean
  created_at: string
  sender: number | null
  receiver: number
}

// 创建通知请求类型
export interface CreateNotificationRequest {
  title: string
  content: string
  type: string
}

// 批量标记已读请求类型
export interface BatchMarkAsReadRequest {
  notification_ids?: number[]
}

// 未读通知计数响应类型
export interface UnreadCountResponse {
  unread_count: number
}



// 获取通知列表
export const getNotifications = () => {
  return apiClient.get<Notification[]>('/notifications/')
}

// 标记通知为已读
export const markAsRead = (notificationId: number) => {
  return apiClient.patch<Notification>(`/notifications/${notificationId}/`, { is_read: true })
}

// 删除通知
export const deleteNotification = (notificationId: number) => {
  return apiClient.delete(`/notifications/${notificationId}/`)
}

// 批量标记为已读
export const markAllAsRead = () => {
  return apiClient.post('/notifications/mark_as_read/')
}

// 批量标记通知为已读
export const batchMarkAsRead = (data: BatchMarkAsReadRequest) => {
  return apiClient.post('/batch-mark-as-read/', data)
}

// 创建通知
export const createNotification = (data: CreateNotificationRequest) => {
  return apiClient.post('/notifications/send-to-user/', data)
}

// 删除已读通知
export const deleteReadNotifications = () => {
  return apiClient.delete('/notifications/delete-read/')
}

// 获取未读通知数量
export const getUnreadCount = () => {
  return apiClient.get<UnreadCountResponse>('/notifications/unread-count/')
}
