import axios from "axios";

const api = axios.create({
    baseURL: 'http://localhost:8000/', //后端接口地址
    timeout: 5000
})

export function apiPost(methodUrl, data) {
    return api.post(methodUrl, data,).then(res => res.data)

}