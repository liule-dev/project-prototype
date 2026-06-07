import api from './index.js'

export const reviewRecordsApi = {
  // 获取用户复习记录
  getByUser(userId) {
    return api.get(`/review-records/user/${userId}/`)
  },

  // 添加复习记录
  add(data) {
    return api.post('/review-records/add/', data)
  }
}
