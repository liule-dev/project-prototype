import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000/',
    timeout: 5000,
});


api.interceptors.request.use(config => {
    // 只有在不是注册、发送验证码和重置密码的请求中才添加认证头
    const isPublicRoute = config.url.includes('/send_code/') || 
                          config.url.includes('/login/register1/') || 
                          config.url.includes('/login/reset_password/');
    
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

export function LoginAPI(motendurl,data){
    return api.post(motendurl,{username:data.username,password:data.password}).then(res => res.data);
}

export function ResetPasswordAPI(motendurl,data){
    return api.post(motendurl, {
        username: data.username,
        email: data.email,
        verifyCode: data.verifyCode,
        newPassword: data.newPassword
    }).then(res => res.data);
}

export function RegisterAPI(motendurl,data){
    return api.post(motendurl, {username:data.username,password:data.password,email:data.email,code:data.verifyCode}).then(res => res.data);
}

export function Query1API(motendurl,username){
    return api.post(motendurl, {username:username}).then(res => res.data);
}

export function Query2API(motendurl){
    return api.get(motendurl).then(res => res.data);
}

export function SendCodeAPI(motendurl,data){
    return api.post(motendurl, {
        username: data.username || '',
        email: data.email || ''
    }).then(res => res.data);
}

export function QueryUserAPI(motendurl){
    return api.get(motendurl).then(res => res.data);
}



export function manageUpdateAPI(motendurl,data){
    return api.post(motendurl, {id:data.id,username:data.username,email:data.email,password:data.password,role:data.role,grade:data.grade1_name,class:data.class1_name,specialty:data.specialty1_name,phone:data.phone,}).then(res => res.data);
}


export function userUpdateAPI(motendurl,data){

    return api.post(motendurl, {username:data.username,email:data.email,grade:data.grade1_name,class:data.class1_name,specialty:data.specialty1_name,phone:data.phone,}).then(res => res.data);
}
export function manageDeleteAPI(motendurl,id){
    return api.post(motendurl, {id:id}).then(res => res.data);
}

export function logoutAPI(motendurl){
    return api.post(motendurl).then(res => res.data);
}


export default api;