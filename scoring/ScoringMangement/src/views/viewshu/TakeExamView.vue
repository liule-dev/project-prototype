<template>
  <div class="take-exam-container">
    <!-- 引入Element图标组件 -->
    <el-icon :size="18" class="icon-common">
      <Refresh />
    </el-icon>

    <el-tabs v-model="activeTab" class="exam-tabs">


      <!-- 管理员：所有考试 Tab -->
      <el-tab-pane label="所有考试" name="allExams" class="exam-tab-pane" v-if="isAdmin">
        <el-card class="exam-card">
          <div slot="header" class="card-header">
            <span class="card-title">所有考试</span>
            <el-button
              style="float: right;"
              type="primary"
              @click="fetchAllExams"
              class="refresh-btn"
            >
              <el-icon :size="16"><Refresh /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
          </div>

          <el-table
            :data="allExams"
            v-loading="loading"
            style="width: 100%"
            class="exam-table"
          >
            <el-table-column prop="name" label="考试名称" class="table-column" />
            <el-table-column prop="subject" label="科目" class="table-column" />
            <el-table-column prop="all_score" label="总分" class="table-column" />
            <el-table-column prop="begin_time" label="开始时间" class="table-column">
              <template #default="scope">
                {{ formatDate(scope.row.begin_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="end_time" label="结束时间" class="table-column">
              <template #default="scope">
                {{ formatDate(scope.row.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="考试时长(分钟)" class="table-column" />
            <el-table-column prop="created_by" label="创建人" class="table-column" />
            <el-table-column label="操作" width="200" class="table-column operation-column">
              <template #default="scope">
                <el-button
                  size="small"
                  type="primary"
                  @click="viewAllExamDetail(scope.row)"
                  class="operation-btn"
                >
                  查看详情
                </el-button>
                <el-button
                  size="small"
                  type="info"
                  @click="editExam(scope.row)"
                  class="operation-btn"
                >
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            description="暂无考试"
            v-if="allExams.length === 0 && !loading"
            class="empty-state"
          />
        </el-card>
      </el-tab-pane>

      <!-- 学生：可参加的考试 Tab -->
      <el-tab-pane label="可参加的考试" name="available" class="exam-tab-pane" v-if="!isAdmin">
        <el-card class="exam-card">
          <div slot="header" class="card-header">
            <span class="card-title">可参加的考试</span>
            <el-button
              style="margin-left: 858px;"
              type="primary"
              @click="fetchAvailableExams"
              class="refresh-btn"
            >
              <el-icon :size="16"><Refresh /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
            <el-button
        v-if="!isAdmin"
        type="default"
        @click="jupe"
        class="back-home-btn"
        icon="ArrowLeft"
        plain        style="margin-left: 0px; margin-right: 16px;"
      >
        返回主页
      </el-button>
          </div>

          <el-table
            :data="availableExams"
            v-loading="loading"
            style="width: 100%"
            class="exam-table"
          >
            <el-table-column prop="name" label="考试名称" class="table-column" />
            <el-table-column prop="subject" label="科目" class="table-column" />
            <el-table-column prop="all_score" label="总分" class="table-column" />
            <el-table-column prop="begin_time" label="开始时间" class="table-column">
              <template #default="scope">
                {{ formatDate(scope.row.begin_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="end_time" label="结束时间" class="table-column">
              <template #default="scope">
                {{ formatDate(scope.row.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="考试时长(分钟)" class="table-column" />
            <el-table-column label="操作" width="150" class="table-column operation-column">
              <template #default="scope">
                <el-form :model="startForm" ref="startFormRef">
                  <el-form-item>
                    <el-button
                      size="small"
                      type="primary"
                      @click="startOrContinueExam(scope.row)"
                      :loading="isLoadingButton[scope.row.id]"
                      class="operation-btn"
                    >
                      开始考试

                    </el-button>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            description="暂无可参加的考试"
            v-if="availableExams.length === 0 && !loading"
            class="empty-state"
          />
        </el-card>
      </el-tab-pane>

      <!-- 学生：我的成绩 Tab -->
      <el-tab-pane label="参加过的考试" name="myScores" class="exam-tab-pane" v-if="!isAdmin">
        <el-card class="exam-card">
          <div slot="header" class="card-header">
            <span class="card-title">参加过的考试</span>
            <el-button
              style="margin-left: 858px;"
              type="primary"
              @click="fetchMyScores"
              class="refresh-btn"
            >
              <el-icon :size="16"><Refresh /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
            <el-button
        v-if="!isAdmin"
        type="default"
        @click="jupe"
        class="back-home-btn"
        icon="ArrowLeft"
        plain        style="margin-left: 0px; margin-right: 16px;"
      >
        返回主页
      </el-button>
          </div>

          <el-table
            :data="myScores"
            v-loading="scoreLoading"
            style="width: 100%"
            class="exam-table"
          >
            <el-table-column prop="exam_name" label="考试名称" class="table-column" />
            <el-table-column prop="subject" label="科目" class="table-column" />
            <el-table-column prop="all_score" label="总分" class="table-column" />
            <el-table-column prop="created_at" label="考试时间" class="table-column">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" class="table-column status-column">
              <template #default="scope">
                <el-tag
                  :type="getStatusType(scope.row.status)"
                  class="status-tag"
                >
                  {{ formatStatus(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" class="table-column operation-column">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="handleExamAction(scope.row)"
                  :type="scope.row.status === 'in_progress' ? 'warning' : 'primary'"
                  class="operation-btn"
                >
                  {{ scope.row.status === 'in_progress' ? '继续考试' : '查看详情' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            description="暂无参加过的考试记录"
            v-if="myScores.length === 0 && !scoreLoading"
            class="empty-state"
          />
        </el-card>

      </el-tab-pane>

      <!-- 管理员：考试统计 Tab -->
      <el-tab-pane label="考试统计" name="examStats" class="exam-tab-pane" v-if="isAdmin">
        <el-card class="exam-card">
          <div slot="header" class="card-header">
            <span class="card-title">考试统计</span>
            <el-button
              style="float: right;"
              type="primary"
              @click="fetchExamStats"
              class="refresh-btn"
            >
              <el-icon :size="16"><Refresh /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
          </div>

          <el-table
            :data="examStats"
            v-loading="statsLoading"
            style="width: 100%"
            class="exam-table"
          >
            <el-table-column prop="exam_name" label="考试名称" class="table-column" />
            <el-table-column prop="subject" label="科目" class="table-column" />
            <el-table-column prop="total_participants" label="参与人数" class="table-column" />
            <el-table-column prop="avg_score" label="平均分" class="table-column" />
            <el-table-column prop="highest_score" label="最高分" class="table-column" />
            <el-table-column prop="lowest_score" label="最低分" class="table-column" />
            <el-table-column prop="pass_rate" label="通过率" class="table-column">
              <template #default="scope">
                {{ scope.row.pass_rate }}%
              </template>
            </el-table-column>
            <el-table-column label="操作" class="table-column operation-column">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="viewExamParticipants(scope.row)"
                  class="operation-btn"
                >
                  查看参与者
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            description="暂无统计数据"
            v-if="examStats.length === 0 && !statsLoading"
            class="empty-state"
          />
        </el-card>
      </el-tab-pane>

    </el-tabs>

    <!-- 考试详情对话框 -->
    <el-dialog
      title="考试详情"
      v-model="scoreDetailDialogVisible"
      width="80%"
      class="detail-dialog"
    >
      <div v-if="selectedScore" class="detail-content">
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="考试名称" class="desc-item">{{ selectedScore.exam_name || selectedScore.name }}</el-descriptions-item>
          <el-descriptions-item label="科目" class="desc-item">{{ selectedScore.subject }}</el-descriptions-item>
          <el-descriptions-item label="总分" class="desc-item">{{ selectedScore.all_score }}</el-descriptions-item>
          <el-descriptions-item label="考试时间" class="desc-item">{{ formatDate(selectedScore.created_at || selectedScore.begin_time) }}</el-descriptions-item>
          <el-descriptions-item label="状态" class="desc-item" v-if="selectedScore.status">
            <el-tag
              :type="getStatusType(selectedScore.status)"
              class="status-tag"
            >
              {{ formatStatus(selectedScore.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider class="detail-divider">考试题目</el-divider>
        <el-table
          :data="examTopics"
          style="width: 100%"
          max-height="360"
          class="detail-table"
        >
          <el-table-column type="index" label="#" width="50" class="table-column" />
          <el-table-column
            prop="topic_content"
            label="题目内容"
            show-overflow-tooltip
            class="table-column topic-column"
          />
          <el-table-column
            prop="topic_difficulty"
            label="难度"
            width="80"
            class="table-column"
          >
            <template #default="scope">
              <el-tag
                :type="getDifficultyType(scope.row.topic_difficulty)"
                class="difficulty-tag"
              >
                {{ formatDifficulty(scope.row.topic_difficulty) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="考生答案"
            width="100"
            class="table-column answer-column"
          >
            <template #default="scope">
              {{ getUserAnswer(scope.row.topic_number) || '未作答' }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button
            @click="scoreDetailDialogVisible = false"
            class="close-btn"
          >
            关闭
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 参与者详情对话框 -->
    <el-dialog
      title="考试参与者"
      v-model="participantsDialogVisible"
      width="80%"
      class="detail-dialog"
    >
      <div v-if="selectedExamStats" class="detail-content">
        <el-descriptions :column="1" border class="detail-descriptions">
          <el-descriptions-item label="考试名称">{{ selectedExamStats.exam_name }}</el-descriptions-item>
          <el-descriptions-item label="科目">{{ selectedExamStats.subject }}</el-descriptions-item>
          <el-descriptions-item label="参与人数">{{ selectedExamStats.total_participants }}</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ selectedExamStats.avg_score }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>参与者列表</el-divider>
        <el-table
          :data="examParticipants"
          style="width: 100%"
          max-height="400"
          class="detail-table"
        >
          <el-table-column prop="user_name" label="姓名" class="table-column" />
          <el-table-column prop="user_id" label="学号" class="table-column" />
          <el-table-column prop="score" label="得分" class="table-column" />
          <el-table-column prop="submit_time" label="提交时间" class="table-column">
            <template #default="scope">
              {{ formatDate(scope.row.submit_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" class="table-column">
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                class="status-tag"
              >
                {{ formatStatus(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" class="table-column">
            <template #default="scope">
              <el-button
                size="small"
                @click="viewParticipantDetail(scope.row)"
                class="operation-btn"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button
            @click="participantsDialogVisible = false"
            class="close-btn"
          >
            关闭
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
// 导入Element图标
import { Refresh } from '@element-plus/icons-vue'
import { ElIcon } from 'element-plus'
import { ref, reactive, onMounted } from 'vue'
import { examAPI } from '@/api1/exam.js'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
// 检查是否为管理员
const isAdmin = ref(localStorage.getItem('userRole') === 'admin' || localStorage.getItem('userRole') === 'administrator')
const activeTab = ref(isAdmin.value ? 'allExams' : 'available')
const loading = ref(true)
const scoreLoading = ref(true)
const statsLoading = ref(true)

// 学生相关数据
const availableExams = ref([])
const myScores = ref([])

// 管理员相关数据
const allExams = ref([])
const examStats = ref([])

// 通用数据
const scoreDetailDialogVisible = ref(false)
const participantsDialogVisible = ref(false)
const selectedScore = ref(null)
const selectedExamStats = ref(null)
const startFormRef = ref(null)
const startForm = reactive({
  exam_paper_id: '',
  user_id: localStorage.getItem('userId')
})
const examStarted = ref(false)
const participationId = ref(null)
const topics = ref([])
const examName = ref('')
const endTime = ref(null)
const timer = ref(null)
const examTopics = ref([])
const examProgress = ref([])
const examParticipants = ref([])

const userId = localStorage.getItem('userId')
const isLoadingButton = ref({})
const examStatuses = ref({})

const startTimer = () => {
  timer.value = setInterval(() => {}, 1000)
}

// 管理员：获取所有考试
const fetchAllExams = async () => {
  loading.value = true
  try {
    const response = await examAPI.getAllExams()
    allExams.value = response.data.exams
    ElMessage.success(""+response.data.message)
  } catch (error) {
    ElMessage.error('获取考试列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 管理员：获取考试统计
const fetchExamStats = async () => {
  statsLoading.value = true
  try {
    const response = await examAPI.getExamStatistics()
    examStats.value = response.data.statistics
    ElMessage.success(""+response.data.message)
  } catch (error) {
    ElMessage.error('获取考试统计失败: ' + error.message)
  } finally {
    statsLoading.value = false
  }
}

// 学生：获取可参加考试
const fetchAvailableExams = async () => {
  loading.value = true
  try {
    const response = await examAPI.getUserAvailableExams(userId)
    availableExams.value = response.data.exams

    // 初始化可用考试的状态
    for(const exam of availableExams.value) {
      await checkExamStatusForDisplay(exam.id);
    }

    ElMessage.success(""+response.data.message)
  } catch (error) {
    ElMessage.error('获取考试列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 学生：获取我的成绩
// 学生：获取我的成绩
const fetchMyScores = async () => {
  scoreLoading.value = true
  try {
    const response = await examAPI.getClassScores(userId)
    if (response.data.status === 'success') {
      // 过滤掉未开始的考试，只保留已参与的考试
      const allScores = response.data.scores

      // 为每个考试获取参与状态，并过滤掉未开始的考试
      const scoresWithStatus = []
      for(const score of allScores) {
        const status = await checkExamStatus(score.exam_paper_number)
        // 只有当考试状态不是'未开始'时才添加到结果中
        if (status !== 'not_started') {
          score.status = status
          scoresWithStatus.push(score)
        }
      }

      myScores.value = scoresWithStatus
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('获取考试记录失败: ' + error.message)
  } finally {
    scoreLoading.value = false
  }
}

// 获取考试按钮文本
const getExamButtonText = async (exam) => {
  const status = await checkExamStatusForDisplay(exam.id);
  return status === 'in_progress' ? '继续考试' : '开始考试';
}

// 检查考试状态的函数
const checkExamStatus = async (examId) => {
  try {
    const userId = localStorage.getItem('userId');
    const response = await examAPI.getUserExamParticipation(userId, examId);

    if (response.data && response.data.status === 'success') {
      return response.data.participation?.status || 'not_started';
    }
  } catch (error) {
    console.error('获取考试参与状态失败:', error);
  }

  return 'not_started';
}

// 专门用于显示的考试状态检查函数
const checkExamStatusForDisplay = async (examId) => {
  if (examStatuses.value[examId]) {
    return examStatuses.value[examId];
  }

  try {
    const userId = localStorage.getItem('userId');
    const response = await examAPI.getUserExamParticipation(userId, examId);

    if (response.data && response.data.status === 'success') {
      const status = response.data.participation?.status || 'not_started';
      examStatuses.value[examId] = status;
      return status;
    }
  } catch (error) {
    console.error('获取考试参与状态失败:', error);
  }

  return 'not_started';
}

// 修改后的开始或继续考试函数
const startOrContinueExam = async (exam) => {
  // 设置按钮加载状态
  isLoadingButton.value[exam.id] = true;

  try {
    startForm.exam_paper_id = exam.id;
    if (!startFormRef.value) return;

    await startFormRef.value.validate(async (valid) => {
      if (valid) {
        try {
          const userId = parseInt(startForm.user_id)
          const examDetail = await examAPI.getExamDetail(startForm.exam_paper_id)
          if (examDetail.data.status !== 'success') {
            ElMessage.error('获取考试信息失败: ' + examDetail.data.message)
            return
          }

          const now = new Date()
          const beginTime = new Date(examDetail.data.exam.begin_time)
          const endTime = new Date(examDetail.data.exam.end_time)

          if (now < beginTime) {
            ElMessage.error('考试尚未开始')
            return
          }

          if (now > endTime) {
            ElMessage.error('考试已结束')
            return
          }

          // 获取考试参与状态
          let participation = null;
          try {
            const participationResponse = await examAPI.getUserExamParticipation(
              userId,
              startForm.exam_paper_id
            );

            if (participationResponse.data.status === 'success') {
              participation = participationResponse.data.participation;
            }
          } catch (error) {
            console.error('获取考试参与记录失败:', error);
          }

          // 检查是否已经提交
          if (participation && participation.status === 'submitted') {
            ElMessage.error('您已完成该考试，无法再次参加');
            return;
          }

          // 检查是否已经在进行中
          if (participation && participation.status === 'in_progress') {
            // 如果考试已在进行中，直接跳转到考试页面
            ElMessage.success('正在继续考试...')
            await router.push({
              name: 'ExamPaper',
              params: { examPaperId: startForm.exam_paper_id },
              query: { participationId: participation.id }
            })
            return;
          }

          // 如果没有参与记录或状态为 not_started，开始新考试
          const response = await examAPI.startExam({
            exam_paper_id: startForm.exam_paper_id,
            user_id: userId
          })

          if (response.data.status === 'success') {
            examStarted.value = true
            participationId.value = response.data.participation_id
            topics.value = response.data.topics || response.topics
            examName.value = `在线考试 - ${examDetail.data.exam.name || '未知考试'}`
            endTime.value = new Date(response.data.end_time)
            startTimer()
            ElMessage.success('考试开始')
            await router.push({
              name: 'ExamPaper',
              params: { examPaperId: startForm.exam_paper_id },
              query: { participationId: response.data.participation_id }
            })
          } else {
            ElMessage.error(response.data.message)
          }
        } catch (error) {
          ElMessage.error('操作失败: ' + error.message)
        }
      }
    })
  } finally {
    // 移除按钮加载状态
    isLoadingButton.value[exam.id] = false;
  }
}

// 处理考试操作（在"参加过的考试"列表中）
const handleExamAction = async (score) => {
  if (score.status === 'in_progress') {
    // 如果考试正在进行中，跳转到继续考试
    try {
      const userId = localStorage.getItem('userId');
      const participationResponse = await examAPI.getUserExamParticipation(
        userId,
        score.exam_paper_number
      );

      if (participationResponse.data.status === 'success' &&
          participationResponse.data.participation?.status === 'in_progress') {
        ElMessage.success('正在继续考试...');
        await router.push({
          name: 'ExamPaper',
          params: { examPaperId: score.exam_paper_number },
          query: { participationId: participationResponse.data.participation.id }
        });
      } else {
        ElMessage.error('无法找到进行中的考试记录');
      }
    } catch (error) {
      ElMessage.error('继续考试失败: ' + error.message);
    }
  } else {
    // 否则查看考试详情
    await viewExamDetail(score);
  }
}

// 学生：查看考试详情
const viewExamDetail = async (score) => {
  selectedScore.value = score
  examTopics.value = []
  examProgress.value = []

  try {
    const topicsResponse = await examAPI.getExamTopics(score.exam_paper_number)
    if (topicsResponse.data && topicsResponse.data.status === 'success') {
      examTopics.value = topicsResponse.data.topics
    }

    try {
      const answersResponse = await examAPI.getUserExamAnswers(userId, score.exam_paper_number)
      console.log('【调试】answersResponse:', answersResponse)
      console.log('【调试】answersResponse.data:', answersResponse.data)
      
      if (answersResponse.data && answersResponse.data.status === 'success') {
        examProgress.value = answersResponse.data.answers
        console.log('【调试】examProgress:', examProgress.value)
      }
    } catch (answersError) {
      console.log('获取用户答题详情失败:', answersError.message)
    }

  } catch (error) {
    ElMessage.error('获取考试详情失败: ' + error.message)
  }

  scoreDetailDialogVisible.value = true
}

// 管理员：查看考试详情
const viewAllExamDetail = async (exam) => {
  selectedScore.value = exam
  examTopics.value = []
  examProgress.value = []

  try {
    const topicsResponse = await examAPI.getExamTopics(exam.id)
    if (topicsResponse.data && topicsResponse.data.status === 'success') {
      examTopics.value = topicsResponse.data.topics
    }
  } catch (error) {
    ElMessage.error('获取考试详情失败: ' + error.message)
  }

  scoreDetailDialogVisible.value = true
}

// 管理员：编辑考试
const editExam = (exam) => {
  ElMessage.info('进入编辑考试页面');
  // 这里应该跳转到编辑考试页面
  router.push({
    name: 'EditExam',
    params: { examId: exam.id }
  })
}

// 管理员：查看考试参与者
const viewExamParticipants = async (examStats) => {
  selectedExamStats.value = examStats
  try {
    const response = await examAPI.getExamParticipants(examStats.exam_id)
    if (response.data && response.data.status === 'success') {
      examParticipants.value = response.data.participants
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('获取参与者列表失败: ' + error.message)
  }

  participantsDialogVisible.value = true
}

// 管理员：查看参与者详情
const viewParticipantDetail = async (participant) => {
  try {
    const response = await examAPI.getUserExamDetail(participant.user_id, participant.exam_id)
    if (response.data && response.data.status === 'success') {
      selectedScore.value = response.data.exam_detail
      examTopics.value = response.data.topics
      examProgress.value = response.data.answers
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('获取用户考试详情失败: ' + error.message)
  }

  scoreDetailDialogVisible.value = true
}

const getUserAnswer = (topicNumber) => {
  const progress = examProgress.value.find(p => p.topic_number === topicNumber)
  // 修复：直接使用 user_answer 字段，如果没有则显示"未作答"
  return progress && progress.user_answer ? progress.user_answer : '未作答'
}

const isAnswerCorrect = (topicNumber) => {
  // 修复：使用 topic_number 而不是 topic_id
  const progress = examProgress.value.find(p => p.topic_number === topicNumber)
  return progress ? progress.is_correct : false
}

const formatStatus = (status) => {
  const statusMap = {
    'not_started': '未开始',
    'in_progress': '进行中',
    'submitted': '已交卷',
    'graded': '已评分'
  }
  return statusMap[status] || status
}

const getStatusType = (status) => {
  const typeMap = {
    'not_started': 'info',
    'in_progress': 'warning',
    'submitted': 'primary',
    'graded': 'success'
  }
  return typeMap[status] || 'info'
}

const formatDifficulty = (difficulty) => {
  const map = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return map[difficulty] || difficulty
}

const getDifficultyType = (difficulty) => {
  const map = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return map[difficulty] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}


const jupe = async () => {
  await router.push('/main')
}
onMounted(async () => {
  if (isAdmin.value) {
    fetchAllExams()
    fetchExamStats()
  } else {
    await fetchAvailableExams()
    await fetchMyScores()
  }
})
</script>

<style scoped>
/* 全局容器样式 */
.take-exam-container {
  padding: 24px 16px;
  max-width: 1300px;
  margin: 0 auto;
  background-color: #fafbfc;
  min-height: calc(100vh - 64px); /* 适配顶部导航栏高度 */
}

/* 标签页样式 */
.exam-tabs {
  width: 100%;
  margin-bottom: 24px;
}
.exam-tabs .el-tabs__header {
  margin-bottom: 16px;
}
.exam-tabs .el-tabs__item {
  padding: 0 22px;
  font-size: 14px;
  color: #666;
  height: 44px;
  line-height: 44px;
  transition: all 0.3s ease;
}
.exam-tabs .el-tabs__item:hover {
  color: #165dff;
}
.exam-tabs .el-tabs__item.is-active {
  color: #165dff;
  font-weight: 500;
}
.exam-tabs .el-tabs__active-bar {
  height: 2px;
  background-color: #165dff;
  width: 60px !important; /* 适配"可参加的考试"标签宽度 */
  left: 0 !important;
  transition: all 0.3s ease;
}
.exam-tab-pane {
  transition: opacity 0.3s ease;
}

/* 卡片样式 */
.exam-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
  border: none;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
  margin-bottom: 24px;
}
.exam-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
}
.card-header {
  padding: 16px 24px;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
}
.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  line-height: 24px;
}

/* 刷新按钮样式 */
.refresh-btn {
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 13px;
  background-color: #165dff;
  border-color: #165dff;
  transition: all 0.2s ease;
}
.refresh-btn:hover {
  background-color: #0e4bd8;
  border-color: #0e4bd8;
}
.refresh-btn .el-icon {
  margin-right: 4px;
}
.btn-text {
  display: inline-block;
  vertical-align: middle;
}

/* 表格样式 */
.exam-table {
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
}
.exam-table .el-table__header-wrapper {
  background-color: #fafafa;
}
.exam-table .el-table__header-cell {
  font-weight: 500;
  color: #333;
  font-size: 13px;
  border-bottom: 1px solid #eee;
  padding: 12px 0;
}
.exam-table .el-table__row {
  height: 56px;
  transition: background-color 0.2s ease;
}
.exam-table .el-table__row:hover {
  background-color: #f5f7fa;
}
.exam-table .el-table__cell {
  padding: 12px 0;
  color: #666;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}
.table-column {
  text-align: center;
}
.operation-column {
  text-align: center;
}
.status-column {
  text-align: center;
}
.topic-column {
  text-align: left !important;
  padding-left: 16px !important;
}
.answer-column {
  text-align: center;
}

/* 操作按钮样式 */
.operation-btn {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.2s ease;
  margin: 0 2px;
}
.operation-btn.el-button--primary {
  background-color: #165dff;
  border-color: #165dff;
}
.operation-btn.el-button--primary:hover {
  background-color: #0e4bd8;
  border-color: #0e4bd8;
}
.operation-btn.el-button--warning {
  background-color: #e6a23c;
  border-color: #e6a23c;
}
.operation-btn.el-button--warning:hover {
  background-color: #cf9236;
  border-color: #cf9236;
}
.operation-btn:not(.el-button--primary):not(.el-button--warning) {
  color: #666;
  border-color: #dcdfe6;
}
.operation-btn:not(.el-button--primary):not(.el-button--warning):hover {
  color: #165dff;
  border-color: #c6d2fe;
  background-color: #f5f7fa;
}

/* 状态标签样式 */
.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 400;
}
/* 难度标签样式 */
.difficulty-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* 空状态样式 */
.empty-state {
  margin-top: 60px;
  margin-bottom: 60px;
}
.empty-state .el-empty__image {
  width: 160px;
  height: auto;
  margin-bottom: 16px;
}
.empty-state .el-empty__description {
  color: #999;
  font-size: 14px;
}

/* 详情弹窗样式 */
.detail-dialog {
  border-radius: 8px;
  overflow: hidden;
}
.detail-dialog .el-dialog__header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fff;
}
.detail-dialog .el-dialog__title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
.detail-dialog .el-dialog__body {
  padding: 24px;
  background-color: #fff;
  line-height: 1.6;
}
.detail-content {
  width: 100%;
}

/* 描述列表样式 */
.detail-descriptions {
  margin-bottom: 24px;
  border-color: #f0f0f0;
}
.detail-descriptions .el-descriptions__label {
  font-weight: 500;
  color: #666;
  font-size: 13px;
  width: 120px;
  text-align: right;
  padding: 12px 16px;
  background-color: #fafafa;
}
.detail-descriptions .el-descriptions__content {
  color: #333;
  font-size: 13px;
  padding: 12px 16px;
}
.desc-item {
  border-right: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

/* 分割线样式 */
.detail-divider {
  margin: 16px 0;
  background-color: #eee;
  height: 1px;
}

/* 详情表格样式 */
.detail-table {
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}
.detail-table .el-table__body-wrapper {
  overflow-y: auto;
}
/* 自定义滚动条 */
.detail-table .el-table__body-wrapper::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.detail-table .el-table__body-wrapper::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}
.detail-table .el-table__body-wrapper::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}
.detail-table .el-table__body-wrapper::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

/* 关闭按钮样式 */
.close-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  transition: all 0.2s ease;
}
.close-btn:hover {
  color: #165dff;
  border-color: #c6d2fe;
  background-color: #f5f7fa;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .take-exam-container {
    max-width: 100%;
    padding: 16px 8px;
  }
  .detail-dialog {
    width: 90%;
  }
}
@media (max-width: 768px) {
  .card-header {
    padding: 12px 16px;
  }
  .card-title {
    font-size: 14px;
  }
  .refresh-btn {
    padding: 4px 10px;
    font-size: 12px;
  }
  .exam-table .el-table__header-cell {
    font-size: 12px;
    padding: 10px 0;
  }
  .exam-table .el-table__cell {
    font-size: 12px;
    padding: 10px 0;
  }
  .operation-btn {
    padding: 3px 8px;
    font-size: 11px;
  }
  .detail-descriptions {
    column: 1;
  }
  .detail-descriptions .el-descriptions__label {
    width: 100px;
    text-align: left;
  }
}
</style>
