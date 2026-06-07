// 配置 API 服务
import axios from 'axios'

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
    timeout: 5000,
});


api.interceptors.request.use(config => {
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

api.interceptors.response.use(config => {
    return config;
},async error => {

    if (error.response && error.response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        try {
            const response = await api.post('/api1/token/refresh/', {refresh: refreshToken})
            localStorage.setItem('access_token', response.data.access)
            if (response.data.refresh) {
                localStorage.setItem('refresh_token', response.data.refresh)
            }
            error.config.headers.Authorization = `Bearer ${response.data.access}`

            return api(error.config)
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});

export default api

