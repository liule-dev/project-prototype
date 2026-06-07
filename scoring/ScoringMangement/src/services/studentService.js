import apiClient from './api11.js'

export default {
  // 获取所有学生
  getStudents() {
    return apiClient.get('/students/')
  },

  // 根据ID获取学生
  getStudentById(id) {
    return apiClient.get(`/students/${id}/`)
  },

  // 根据班级ID获取学生
  getStudentsByClassId(classId) {
    return apiClient.get(`/students/?class_id=${classId}`)
  },

  // 创建学生
  createStudent(studentData) {
    return apiClient.post('/students/', studentData)
  },

  // 更新学生
  updateStudent(id, studentData) {
    return apiClient.put(`/students/${id}/`, studentData)
  },

  // 删除学生
  deleteStudent(id) {
    return apiClient.delete(`/students/${id}/`)
  }
}
