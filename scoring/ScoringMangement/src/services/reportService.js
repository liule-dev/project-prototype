import apiClient from './api11.js'

export default {
  // 获取成绩报告
  getGradeReport(params) {
    return apiClient.get('/reports/grade/', { params })
  },

  // 获取班级报告
  getClassReport(params) {
    return apiClient.get('/reports/class_report/', { params })
  },

  // 获取个人报告
  getPersonalReport(params) {
    return apiClient.get('/reports/personal/', { params })
  },

  // 预览报告
  previewReport(params) {
    // 为预览创建一个新的API端点，返回JSON格式数据
    return apiClient.get('/export-report/', {
      params: params,
      responseType: 'json'
    })
  },

  // 导出报告
  exportReport(params) {
    // 确保使用正确的基础URL和路径
    return apiClient.get('/export-report/', {
      params: params,
      responseType: 'blob' // 用于处理文件下载
    })
  },

  // 根据考试ID获取班级列表
  getClassesByExam(examId) {
    return apiClient.get('/reports/get_classes_by_exam/', {
      params: { exam_id: examId }
    })
  }
}
