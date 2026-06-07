import apiClient from './api11.js'

export default {
  // 获取所有题目
  getTopics() {
    return apiClient.get('/topics/')
  },

  // 根据ID获取题目
  getTopicById(id) {
    return apiClient.get(`/topics/${id}/`)
  },

  // 创建题目
  createTopic(topicData) {
    return apiClient.post('/topics/', topicData)
  },

  // 更新题目
  updateTopic(id, topicData) {
    return apiClient.put(`/topics/${id}/`, topicData)
  },

  // 删除题目
  deleteTopic(id) {
    return apiClient.delete(`/topics/${id}/`)
  }
}
