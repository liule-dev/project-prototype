<!-- src/viewshu/HomeView.vue -->
<template>
  <div class="home">
    <!-- 管理员：显示功能卡片 -->
    <div v-if="userRole === 'admin'" class="admin-home">
      <el-container>
        <el-header>
          <h1>在线考试系统</h1>
          <div v-if="userInfo" class="user-info">
            <el-tag>欢迎，{{ userInfo.username }}</el-tag>
            <el-tag type="info">{{ userInfo.role === 'student' ? '学生' : '教师' }}</el-tag>
            <el-tag v-if="userInfo.classInfo" type="success">
              {{ userInfo.classInfo.grade }} {{ userInfo.classInfo.specialty }} {{ userInfo.classInfo.className }}
            </el-tag>
          </div>
        </el-header>
        <el-main>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card class="function-card" @click="goToExamManagement">
                <div class="card-content">
                  <el-icon size="40"><Upload /></el-icon>
                  <h3>考试管理</h3>
                  <p>创建、编辑、发布考试</p>
                </div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="function-card" @click="goToTakeExam">
                <div class="card-content">
                  <el-icon size="40"><Edit /></el-icon>
                  <h3>查看考试</h3>
                  <p>查看已发布的考试</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-main>
      </el-container>
    </div>

    <!-- 学生：直接显示考试列表 -->
    <div v-else class="student-home">
      <el-tabs v-model="activeTab" class="exam-tabs">
        <!-- 可参加的考试 -->
        <el-tab-pane label="可参加的考试" name="available">
          <el-card class="exam-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">可参加的考试</span>
                <el-button type="primary" @click="fetchAvailableExams" :loading="loading">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>

            <el-table :data="availableExams" v-loading="loading" style="width: 100%">
              <el-table-column prop="name" label="考试名称" />
              <el-table-column prop="subject" label="科目" />
              <el-table-column prop="all_score" label="总分" />
              <el-table-column prop="begin_time" label="开始时间">
                <template #default="scope">
                  {{ formatDate(scope.row.begin_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="end_time" label="结束时间">
                <template #default="scope">
                  {{ formatDate(scope.row.end_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="duration" label="考试时长(分钟)" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button
                    size="small"
                    type="primary"
                    @click="startOrContinueExam(scope.row)"
                    :loading="isLoadingButton[scope.row.id]"
                  >
                    开始考试
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty
              description="暂无可参加的考试"
              v-if="availableExams.length === 0 && !loading"
            />
          </el-card>
        </el-tab-pane>

        <!-- 参加过的考试 -->
        <el-tab-pane label="已参加的考试" name="myScores">
          <el-card class="exam-card">
            <template #header>
              <div class="card-header">
                <span class="card-title">已参加的考试</span>
                <el-button type="primary" @click="fetchMyScores" :loading="scoreLoading">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>

            <el-table :data="myScores" v-loading="scoreLoading" style="width: 100%">
              <el-table-column prop="exam_name" label="考试名称" />
              <el-table-column prop="subject" label="科目" />
              <el-table-column prop="all_score" label="总分" />
              <el-table-column prop="obtained_score" label="得分" />
              <el-table-column prop="created_at" label="考试时间">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)">
                    {{ formatStatus(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button
                    size="small"
                    @click="viewScoreDetail(scope.row)"
                    :type="scope.row.status === 'in_progress' ? 'warning' : 'primary'"
                  >
                    {{ scope.row.status === 'in_progress' ? '继续考试' : '查看详情' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty
              description="暂无已参加的考试记录"
              v-if="myScores.length === 0 && !scoreLoading"
            />
          </el-card>
        </el-tab-pane>
      </el-tabs>

      <!-- 成绩详情对话框 -->
      <el-dialog title="成绩详情" v-model="scoreDetailDialogVisible" width="60%">
        <div v-if="selectedScore">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="考试名称">{{ selectedScore.exam_name }}</el-descriptions-item>
            <el-descriptions-item label="科目">{{ selectedScore.subject }}</el-descriptions-item>
            <el-descriptions-item label="总分">{{ selectedScore.all_score }}</el-descriptions-item>
            <el-descriptions-item label="得分">{{ selectedScore.obtained_score }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(selectedScore.status)">
                {{ formatStatus(selectedScore.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="考试时间">{{ formatDate(selectedScore.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <template #footer>
          <span class="dialog-footer">
            <el-button @click="scoreDetailDialogVisible = false">关闭</el-button>
            <el-button 
              v-if="selectedScore && selectedScore.status === 'in_progress'" 
              type="primary" 
              @click="continueExam"
            >
              继续考试
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {Edit, Upload, Refresh} from '@element-plus/icons-vue'
import {ElMessage} from 'element-plus'
import { examAPI } from '@/api1/exam.js'

const router = useRouter()
const userRole = ref('admin') // 默认为教师
const userInfo = ref(null)
const userId = ref(null)

// 学生相关数据
const activeTab = ref('available')
const availableExams = ref([])
const myScores = ref([])
const loading = ref(false)
const scoreLoading = ref(false)
const isLoadingButton = ref({})
const scoreDetailDialogVisible = ref(false)
const selectedScore = ref(null)

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    // 从localStorage获取用户ID
    userId.value = localStorage.getItem('userId')

    // 获取用户角色
    const role = localStorage.getItem('role')
    userRole.value = role

    // 获取用户名
    const username = localStorage.getItem('username1')
    userInfo.value = {
      username: username,
      role: role
    }

    console.log('用户信息:', userInfo.value)
    
    // 如果是学生，加载考试数据
    if (role === 'student') {
      fetchAvailableExams()
      fetchMyScores()
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 获取可参加的考试
const fetchAvailableExams = async () => {
  loading.value = true
  try {
    const response = await examAPI.getUserAvailableExams(userId.value)
    if (response.data && response.data.exams) {
      availableExams.value = response.data.exams
      ElMessage.success(response.data.message || '获取考试列表成功')
    } else {
      availableExams.value = []
    }
  } catch (error) {
    ElMessage.error('获取考试列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 获取我的成绩
const fetchMyScores = async () => {
  scoreLoading.value = true
  try {
    const response = await examAPI.getMyScores(userId.value)
    if (response.data.status === 'success') {
      myScores.value = response.data.scores
      ElMessage.success('获取成绩成功')
    } else {
      ElMessage.error(response.data.message || '获取成绩失败')
    }
  } catch (error) {
    ElMessage.error('获取成绩列表失败: ' + (error.response?.data?.message || error.message))
  } finally {
    scoreLoading.value = false
  }
}

// 开始或继续考试
const startOrContinueExam = async (exam) => {
  isLoadingButton.value[exam.id] = true
  try {
    const response = await examAPI.startExam({
      exam_paper_id: exam.id,
      user_id: userId.value
    })
    ElMessage.success('开始考试成功')
    // 跳转到考试页面
    router.push({
      name: 'ExamPaper',
      params: {
        examPaperId: exam.id
      },
      query: {
        participationId: response.data.participation_id
      }
    })
  } catch (error) {
    ElMessage.error('开始考试失败: ' + error.message)
  } finally {
    isLoadingButton.value[exam.id] = false
  }
}

// 查看成绩详情
const viewScoreDetail = (score) => {
  if (score.status === 'in_progress') {
    // 如果是进行中的考试，直接跳转到考试页面
    router.push({
      name: 'ExamPaper',
      params: {
        examPaperId: score.exam_paper_number
      },
      query: {
        participationId: score.id
      }
    })
  } else {
    // 其他状态显示详情对话框
    selectedScore.value = score
    scoreDetailDialogVisible.value = true
  }
}

// 继续考试
const continueExam = () => {
  if (selectedScore.value) {
    router.push({
      name: 'ExamPaper',
      params: {
        examPaperId: selectedScore.value.exam_paper_number
      },
      query: {
        participationId: selectedScore.value.id
      }
    })
    scoreDetailDialogVisible.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    'in_progress': 'warning',
    'submitted': 'success',
    'graded': 'success',
    'completed': 'success'
  }
  return map[status] || 'info'
}

// 格式化状态
const formatStatus = (status) => {
  const map = {
    'in_progress': '考试中',
    'submitted': '已提交',
    'graded': '已评分',
    'completed': '已完成'
  }
  return map[status] || status
}

// 获取用户角色
onMounted(() => {
  fetchUserInfo()
})

const goToExamManagement = () => {
  router.push('/exam-management')
}

const goToTakeExam = () => {
  router.push('/take-exam')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #f5f7fa;
}

.admin-home {
  padding: 20px;
}

.student-home {
  padding: 20px;
}

.exam-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.exam-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.function-card {
  cursor: pointer;
  text-align: center;
  height: 200px;
}

.function-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.card-content i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #409EFF;
}

.card-content h3 {
  margin-bottom: 8px;
}

.user-info {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
</style>
