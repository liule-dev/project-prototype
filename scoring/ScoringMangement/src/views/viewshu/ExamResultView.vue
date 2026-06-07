<!-- src/viewshu/TakeExamView.vue -->
<template>
  <div class="take-exam-container">
    <el-tabs v-model="activeTab">
      <!-- 可参加的考试 Tab -->
      <el-tab-pane label="可参加的考试" name="available">
        <el-card>
          <div slot="header" class="clearfix">
            <span>可参加的考试</span>
            <el-button style="float: right;" type="primary" @click="fetchAvailableExams">刷新</el-button>
          </div>

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
                <el-form :model="startForm" ref="startFormRef">
  <!-- 表单内容 -->
                <el-form-item>
                  <el-button
                    size="small"
                    type="primary"
                    @click="startExam(scope.row)"
                    :disabled="isExamStarted(scope.row)"
                  >
                    {{ isExamStarted(scope.row) ? '继续考试' : '开始考试' }}
                  </el-button>
                </el-form-item>
              </el-form>

              </template>
            </el-table-column>
          </el-table>

          <el-empty description="暂无可参加的考试" v-if="availableExams.length === 0 && !loading" />
        </el-card>
      </el-tab-pane>

      <!-- 我的成绩 Tab -->
      <el-tab-pane label="我的成绩" name="myScores">
        <el-card>
          <div slot="header" class="clearfix">
            <span>我的成绩</span>
            <el-button style="float: right;" type="primary" @click="fetchMyScores">刷新</el-button>
          </div>

          <el-table :data="myScores" v-loading="scoreLoading" style="width: 100%">
            <el-table-column prop="exam_name" label="考试名称" />
            <el-table-column prop="subject" label="科目" />
            <el-table-column prop="all_score" label="总分" />
            <el-table-column prop="obtained_score" label="得分" />
            <el-table-column prop="passed" label="是否通过">
              <template #default="scope">
                <el-tag :type="scope.row.passed ? 'success' : 'danger'">
                  {{ scope.row.passed ? '通过' : '未通过' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="考试时间">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button size="small" @click="viewScoreDetail(scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty description="暂无成绩记录" v-if="myScores.length === 0 && !scoreLoading" />
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
          <el-descriptions-item label="是否通过">
            <el-tag :type="selectedScore.passed ? 'success' : 'danger'">
              {{ selectedScore.passed ? '通过' : '未通过' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考试时间">{{ formatDate(selectedScore.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>答题统计</el-divider>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-item">
                <div class="stat-number">{{ selectedScore.statistics?.total_questions || 0 }}</div>
                <div class="stat-label">总题数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card success">
              <div class="stat-item">
                <div class="stat-number">{{ selectedScore.statistics?.correct_answers || 0 }}</div>
                <div class="stat-label">正确题数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card danger">
              <div class="stat-item">
                <div class="stat-number">{{ selectedScore.statistics?.incorrect_answers || 0 }}</div>
                <div class="stat-label">错误题数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card warning">
              <div class="stat-item">
                <div class="stat-number">{{ selectedScore.statistics?.unanswered_questions || 0 }}</div>
                <div class="stat-label">未答题数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="scoreDetailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref,  reactive,onMounted } from 'vue'
import { examAPI } from '@/api1/exam.js'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('available')
const loading = ref(true)
const scoreLoading = ref(true)
const availableExams = ref([])
const myScores = ref([])
const scoreDetailDialogVisible = ref(false)
const selectedScore = ref(null)
const startFormRef = ref(null)
const startForm = reactive({
  exam_paper_id: '',
})
const examStarted = ref(false)
const participationId = ref(null)
const topics = ref([])
const examName = ref('')
const endTime = ref(null)
const timer = ref(null)
// 从localStorage获取用户ID
const userId = parseInt(localStorage.getItem('userId'))
const startTimer = () => {
  // 实现计时器逻辑
  timer.value = setInterval(() => {
    // 计时器逻辑
  }, 1000)
}
// 获取可参加的考试列表
const fetchAvailableExams = async () => {
  loading.value = true
  try {
    const response = await examAPI.getUserAvailableExams(userId)
    availableExams.value = response.data.exams

    for (const exam of availableExams.value) {
      const status = await checkExamStatusForDisplay(exam.id)
      exam.buttonText = status === 'in_progress' ? '继续考试' : '开始考试'
    }

    ElMessage.success(""+response.data.message)
  } catch (error) {
    ElMessage.error('获取考试列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}



// 获取我的成绩（只能获取当前用户的成绩）
const fetchMyScores = async () => {
  scoreLoading.value = true
  try {
    // 修复：使用正确的API方法获取用户成绩
    const response = await examAPI.getUserScores(userId)
    if (response.status === 'success') {
      myScores.value = response.scores
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    ElMessage.error('获取成绩列表失败: ' + error.message)
  } finally {
    scoreLoading.value = false
  }
}

// 开始考试
const startExam = async (exam) => {
    startForm.exam_paper_id = exam.id
  if (!startFormRef.value) return

  await startFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 确保用户ID是数字类型
        const userId = parseInt(startForm.user_id)

        // 先获取考试详情检查考试状态和时间
        const examDetail = await examAPI.getExamDetail(startForm.exam_paper_id)
        if (examDetail.status !== 'success') {
          ElMessage.error('获取考试信息失败: ' + examDetail.message)
          return
        }

        const now = new Date()
        const beginTime = new Date(examDetail.exam.begin_time)
        const endTime = new Date(examDetail.exam.end_time)

        if (now < beginTime) {
          ElMessage.error('考试尚未开始')
          return
        }

        if (now > endTime) {
          ElMessage.error('考试已结束')
          return
        }

        // 检查用户是否已参加过该考试
        const participation = await examAPI.getUserExamParticipation(
          userId,
          startForm.exam_paper_id
        )

        if (participation.status === 'success' &&
           (participation.participation.status === 'submitted' ||
            participation.participation.status === 'in_progress')) {
          ElMessage.error('您已参加过该考试')
          return
        }

        // 开始考试
        const response = await examAPI.startExam({
          exam_paper_id: startForm.exam_paper_id,
          user_id: userId  // 确保传递的是数字类型
        })

        if (response.status === 'success') {
          examStarted.value = true
          participationId.value = response.participation_id
          topics.value = response.topics
          examName.value = `在线考试 - ${examDetail.exam.name || '未知考试'}`

          // 设置结束时间
          endTime.value = new Date(response.end_time)
          startTimer()

          ElMessage.success('考试开始')
             await router.push({
               name: 'ExamPaper',  // 确保路由配置中有这个名称
               params: {
                 examPaperId: startForm.exam_paper_id
               },
               query: {
                 participationId: response.participation_id
               }
             })
        } else {
          ElMessage.error(response.message)
        }
      } catch (error) {
        ElMessage.error('开始考试失败: ' + error.message)
      }
    }
  })
}


// 判断考试是否已开始
const isExamStarted = (exam) => {
  // 这里应该根据用户的考试参与状态来判断
  // 简化处理，实际应调用API获取用户参与状态
  return false
}

// 查看成绩详情
const viewScoreDetail = (score) => {
  selectedScore.value = score
  scoreDetailDialogVisible.value = true
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchAvailableExams()
  fetchMyScores()
})
</script>

<style scoped>
.take-exam-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  text-align: center;
}

.stat-card.success {
  border-color: #67c23a;
  color: #67c23a;
}

.stat-card.danger {
  border-color: #f56c6c;
  color: #f56c6c;
}

.stat-card.warning {
  border-color: #e6a23c;
  color: #e6a23c;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
}
</style>
