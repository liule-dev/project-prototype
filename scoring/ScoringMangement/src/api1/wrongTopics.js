import api from './index.js'

export const wrongTopicsApi = {
  // 获取用户错题列表
  getByUser(userId) {
    return api.get(`/wrong-topics/user/${userId}/`)
  },

  // 添加错题
  add(data) {
    return api.post('/wrong-topics/add/', data)
  },

  // 更新错题状态
  updateStatus(wrongTopicId) {
    return api.post(`/wrong-topics/update/${wrongTopicId}/`)
  }
}
