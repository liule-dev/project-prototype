import apiClient from './api11.js'

export default {
  // 获取所有试卷
  getPapers() {
    return apiClient.get('/papers/')
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
        console.error('获取试卷列表失败:', error);
        throw error;
      });
  },

  // 根据ID获取试卷
  getPaperById(id) {
    return apiClient.get(`/papers/${id}/`)
  },

  // 根据考试ID获取试卷
  getPapersByExamId(examId, classId = null) {
    let url = `/papers/?exam_id=${examId}`;
    if (classId) {
      url += `&class_id=${classId}`;
    }
    return apiClient.get(url)
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
        console.error('根据考试ID获取试卷列表失败:', error);
        throw error;
      });
  },

  // 根据学生ID获取试卷
  getPapersByStudentId(studentId) {
    return apiClient.get(`/papers/?student_id=${studentId}`)
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
        console.error('根据学生ID获取试卷列表失败:', error);
        throw error;
      });
  },

  // 创建试卷
  createPaper(paperData) {
    return apiClient.post('/papers/', paperData)
  },

  // 更新试卷
  updatePaper(id, paperData) {
    return apiClient.put(`/papers/${id}/`, paperData)
  },

  // 删除试卷
  deletePaper(id) {
    return apiClient.delete(`/papers/${id}/`)
  },

  // 自动批改客观题
  autoGradeObjective(id) {
    return apiClient.post(`/papers/${id}/auto_grade_objective/`)
  },

  // 手动批改主观题
  manualGradeSubjective(id, gradeData) {
    return apiClient.post(`/papers/${id}/manual_grade_subjective/`, gradeData)
  },

  // 获取主观题题目
  getSubjectiveQuestions(id) {
    return apiClient.get(`/papers/${id}/get_subjective_questions/`)
  },

  // AI批改主观题
  aiGradeSubjective(id) {
    return apiClient.post(`/papers/${id}/ai_grade_subjective/`)
  },

  // 成绩整合
  integrateGrades(data) {
    return apiClient.post(`/papers/integrate_grades/`, data)
  }
}
