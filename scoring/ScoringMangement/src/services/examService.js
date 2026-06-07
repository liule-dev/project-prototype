import apiClient from './api11.js'

export default {
  // 获取所有考试
  getExams() {
    return apiClient.get('/exams/')
      .then(response => {
        // 确保返回的数据格式正确
        if (response.data && Array.isArray(response.data)) {
          return response;
        } else {
          // 如果响应不是数组，将其包装在数组中
          return {
            ...response,
            data: response.data ? [response.data] : []
          };
        }
      })
      .catch(error => {
        console.error('获取考试列表失败:', error);
        throw error;
      });
  },

  // 根据ID获取考试
  getExamById(id) {
    return apiClient.get(`/exams/${id}/`)
  },

  // 创建考试
  createExam(examData) {
    return apiClient.post('/exams/', examData)
  },

  // 更新考试
  updateExam(id, examData) {
    return apiClient.put(`/exams/${id}/`, examData)
  },

  // 删除考试
  deleteExam(id) {
    return apiClient.delete(`/exams/${id}/`)
  }
}
