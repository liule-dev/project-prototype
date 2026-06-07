import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
    timeout: 10000,
});

// 上传医疗文档
export function upload_medical(url, data) {
    return api.post(url, data).then(res => res.data)
}

// 用户登录
export function login(username, password) {
    return api.post('/auth/login', {
        username,
        password
    }).then(res => res.data)
}

// 用户注册
export function register(username, password, email = null) {
    return api.post('/auth/register', {
        username,
        password,
        email
    }).then(res => res.data)
}

// 检查用户是否已登录
export function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true'
}

// 获取当前用户信息
export function getCurrentUser() {
    return {
        user_id: localStorage.getItem('user_id'),
        username: localStorage.getItem('username')
    }
}

// 登出
export function logout() {
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('isLoggedIn')
}
