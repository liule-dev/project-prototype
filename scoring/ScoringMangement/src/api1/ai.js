import api from './index.js'

export const aiApi = {
  // 生成学习计划
  generateStudyPlan(data) {
    return api.post('/ai/study-plan/', data, {
      timeout: 120000 // 设置超时时间为2分钟（120000毫秒）
    })
  },

  // 分析错题本
  analyzeWrongTopics(userId) {
    return api.get(`/ai/analyze-wrong-topics/${userId}/`, {
      timeout: 120000 // 设置超时时间为2分钟（120000毫秒）
    })
  },
   // AI聊天功能
  chatWithAI(data) {
    return api.post('/ai/chat/', data, {
      timeout: 120000 // 设置超时时间为2分钟
    })
  },
}
