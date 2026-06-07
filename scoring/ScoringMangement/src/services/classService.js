import apiClient from './api11.js'

export default {
  // 获取所有班级
  getClasses() {
    return apiClient.get('/classes/')
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
        console.error('获取班级列表失败:', error);
        throw error;
      });
  },

  // 根据ID获取班级
  getClassById(id) {
    return apiClient.get(`/classes/${id}/`)
  },

  // 创建班级
  createClass(classData) {
    return apiClient.post('/classes/', classData)
  },

  // 更新班级
  updateClass(id, classData) {
    return apiClient.put(`/classes/${id}/`, classData)
  },

  // 删除班级
  deleteClass(id) {
    return apiClient.delete(`/classes/${id}/`)
  }
}
