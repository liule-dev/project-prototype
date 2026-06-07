import apiClient from './api11.js'

export default {
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   * @returns {Promise} 登录响应
   */
  login(credentials) {
    return apiClient.post('/api-token-auth/', credentials)
  },

  /**
   * 用户登出
   */
  logout() {
    // 清除本地存储的token
    localStorage.removeItem('token')
  },

  /**
   * 检查用户是否已认证
   * @returns {boolean} 是否已认证
   */
  isAuthenticated() {
    return !!localStorage.getItem('token')
  },

  /**
   * 获取当前用户信息
   * @returns {Promise} 用户信息
   */
  getCurrentUser() {
    return apiClient.get('/users/current/')
  }
}
