// src/api/exam.js
import axios from 'axios'

// 创建axios实例，增加超时时间
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000, // 增加到30秒
})

api.interceptors.request.use(config => {
    // 只有在不是注册和发送验证码的请求中才添加认证头
    const isPublicRoute = config.url.includes('/send_code/') || config.url.includes('/login/register1/');

    if (!isPublicRoute) {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
},error => {
    return Promise.reject(error);
});

api.interceptors.response.use(config => {
    return config;
},async error => {

    if (error.response && error.response.status === 401) {
        const refreshToken = localStorage.getItem('refresh_token');
        try {
            const response = await api.post('/api1/token/refresh/', {refresh: refreshToken})
            localStorage.setItem('access_token', response.data.access)
            if (response.data.refresh) {
                localStorage.setItem('refresh_token', response.data.refresh)
            }
            error.config.headers.Authorization = `Bearer ${response.data.access}`

            return api(error.config)
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});
// 考试相关API
export const examAPI = {
  // 创建考试
  createExam(data) {
    return api.post('/create_exam/', data)
  },

  // AI智能组卷
  aiGenerateExam(data) {
    return api.post('/ai_generate_exam/', data)
  },

  // 发布考试
  publishExam(data) {
    return api.post('/publish_exam/', data)
  },

  // 更新考试
  updateExam(examId, data) {
    return api.put(`/exam/${examId}/`, data)
  },

  // 删除考试
  deleteExam(examId) {
    return api.delete(`/exam/${examId}/`)
  },

  // 开始答题
  startExam(data) {
    return api.post('/start_exam/', data)
  },

  // 保存答题进度
  saveProgress(data) {
    return api.post('/save_progress/', data)
  },

  // 交卷
  submitExam(data) {
    return api.post('/submit_exam/', data)
  },

  // 生成成绩报告
  generateScoreReport(data) {
    return api.post('/generate_score_report/', data)
  },

  // 获取考试详情
  getExamDetail(examPaperId) {
    return api.get(`/exam/${examPaperId}/`)
  },

  // 获取试卷题目
  getExamTopics(examPaperId) {
    return api.get(`/exam/${examPaperId}/topics/`)
  },
   getUserExamAnswers(userId, examPaperId) {
    return api.get(`/user/${userId}/exam/${examPaperId}/answers/`)
  },
  // 获取用户考试参与情况
  getUserExamParticipation(userId, examPaperId) {
    return api.get(`/exam_participation/${userId}/${examPaperId}/`)
  },

  // 获取所有考试列表
  getPublishedExams() {
    return api.get('/published_exams/').then(res => res.data);
  },

  // 获取科目列表
  getSubjects() {
    return api.get('/subjects/')
  },

  // 获取科目详情（包含题型配置）
  getSubjectDetail(subjectId) {
    return api.get(`/subject/${subjectId}/detail/`)
  },

  // 获取用户可参加的考试列表
  getUserAvailableExams(userId) {
    return api.get(`/user_exams/${userId}/`)
  },

  // 获取用户信息
  getUserInfo(userId) {
    return api.get(`/user/${userId}/`)
  },

  // 获取班级成绩
  getClassScores(userId) {
    return api.get(`/user/${userId}/scores/`)
  },

  // 获取用户成绩列表
  getMyScores(userId) {
    return api.get(`/user/${userId}/scores/`)
  }
}

export default api
