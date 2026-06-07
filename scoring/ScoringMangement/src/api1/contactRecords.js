import api from './index.js'

export const contactRecordsApi = {
  // 获取用户练习记录
  getByUser(userId) {
    return api.get(`/contact-records/user/${userId}/`)
  },

  // 添加练习记录
  add(data) {
    return api.post('/contact-records/add/', data)
  }
}
