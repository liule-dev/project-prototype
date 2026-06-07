<template>
  <div class="auto-grade-container">
    <!-- 页面标题 -->


    <el-card class="filter-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-search"></i>
            <span>筛选条件</span>
          </div>
        </div>
      </template>
      <el-form :inline="true" :model="filterForm" class="filter-form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="10">
            <el-form-item label="考试名称">
              <el-select
                v-model="filterForm.examId"
                placeholder="请选择考试"
                @change="onExamChange"
                clearable
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="exam in exams"
                  :key="exam.id"
                  :label="exam.name"
                  :value="exam.id.toString()">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item>
              <el-button type="primary" @click="loadExamPapers" class="gradient-button">查询</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="papers-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-document"></i>
            <span>待批改试卷</span>
          </div>
          <el-button style="float: right; padding: 8px 16px" type="success" @click="startAutoGrading" :disabled="selectedPapers.length === 0" class="gradient-button">开始自动批改</el-button>
        </div>
      </template>

      <el-table
        :data="examPapers"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        class="modern-table"
        stripe>
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="studentName" label="学生姓名" min-width="120">
          <template #default="scope">
            <div class="student-info">
              <i class="el-icon-user"></i>
              <span>{{ scope.row.studentName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="studentId" label="学号" min-width="120"></el-table-column>
        <el-table-column prop="className" label="班级" min-width="150"></el-table-column>
        <el-table-column prop="submitTime" label="提交时间" min-width="200"></el-table-column>
        <el-table-column label="客观题数量" min-width="120">
          <template #default="scope">
            <span v-if="scope.row.status === 'graded'">{{ scope.row.objectiveCount }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'graded' ? 'success' : 'warning'" class="status-tag">
              {{ scope.row.status === 'graded' ? '已批改' : '未批改' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="客观题得分" min-width="120">
          <template #default="scope">
            <span v-if="scope.row.status === 'graded'" class="score-text">
              {{ scope.row.objectiveScore }} / {{ scope.row.totalObjectiveScore }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          background>
        </el-pagination>
      </div>
    </el-card>

    <el-dialog v-model="gradingDialogVisible" title="自动批改进度" width="50%" class="modern-dialog">
      <div class="dialog-content">
        <el-progress :percentage="gradingProgress" :stroke-width="12" class="progress-bar"></el-progress>
        <p class="progress-status">{{ gradingStatus }}</p>

        <!-- 批改详情展示 -->
        <div v-if="currentGradingDetails.length > 0" style="margin-top: 20px;">
          <el-checkbox v-model="showGradingDetails" @change="handleShowDetailsChange" class="detail-checkbox">
            显示批改详情
          </el-checkbox>

          <div v-show="showGradingDetails" style="margin-top: 15px;">
            <el-table :data="currentGradingDetails" style="width: 100%" max-height="300" class="detail-table">
              <el-table-column prop="questionNumber" label="题号" width="80"></el-table-column>
              <el-table-column prop="studentAnswer" label="学生答案" width="120"></el-table-column>
              <el-table-column prop="correctAnswer" label="正确答案" width="120"></el-table-column>
              <el-table-column prop="isCorrect" label="是否正确">
                <template #default="scope">
                  <el-tag :type="scope.row.isCorrect ? 'success' : 'danger'" class="result-tag">
                    {{ scope.row.isCorrect ? '正确' : '错误' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="得分" width="80"></el-table-column>
              <el-table-column prop="maxScore" label="满分" width="80"></el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="gradingDialogVisible = false" :disabled="!gradingFinished" class="footer-button">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import examService from '@/services/examService'
import paperService from '@/services/paperService'

const filterForm = reactive({
  examId: ''
})

const exams = ref([])
const examPapers = ref([])
const selectedPapers = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const gradingDialogVisible = ref(false)
const gradingProgress = ref(0)
const gradingStatus = ref('准备开始批改')
const gradingFinished = ref(false)
const showGradingDetails = ref(false) // 控制是否显示批改详情
const currentGradingDetails = ref([]) // 当前批改详情

// 获取考试列表
const loadExams = async () => {
  try {
    const response = await examService.getExams()
    exams.value = response.data.map(exam => {
      // 修复字符编码问题
      let name = exam.name;
      try {
        // 尝试修复可能的编码问题
        name = decodeURIComponent(escape(name));
      } catch (e) {
        // 检查是否是编码问题导致的异常
        if (e instanceof URIError) {
          // URIError表示编码不正确，使用原始名称
          console.warn('字符编码修复失败，使用原始名称:', name);
        } else {
          // 其他错误重新抛出
          throw e;
        }
      }

      return {
        id: exam.number || exam.id,
        name: name || '未知考试'
      }
    })

    // 如果只有一门考试，自动选择它
    if (exams.value.length === 1) {
      filterForm.examId = exams.value[0].id.toString()
      loadExamPapers()
    }
  } catch (error) {
    console.error('获取考试列表失败:', error)
    ElMessage.error('获取考试列表失败: ' + (error.response?.data?.message || error.message))
    exams.value = []
  }
}

// 考试选择变化时的处理函数
const onExamChange = (examId) => {
  filterForm.examId = examId
  if (examId) {
    loadExamPapers()
  } else {
    // 如果没有选择考试，清空试卷列表
    examPapers.value = []
    total.value = 0
  }
}

// 格式化时间显示
const formatSubmitTime = (timeValue) => {
  if (!timeValue) return '';

  try {
    // 如果是对象，尝试获取其字符串表示
    let timeString = typeof timeValue === 'object' ? JSON.stringify(timeValue) : timeValue;

    // 尝试修复编码问题
    const decodedTime = decodeURIComponent(escape(timeString));

    // 尝试解析为日期对象
    const date = new Date(decodedTime);
    if (!isNaN(date.getTime())) {
      // 成功解析为日期，格式化为本地时间字符串
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }

    // 不是日期格式，但编码修复成功，返回修复后的字符串
    return decodedTime;
  } catch (e) {
    console.warn('时间格式化失败:', e);
    // 编码修复失败，尝试直接使用原始值
    try {
      return typeof timeValue === 'object' ? JSON.stringify(timeValue) : timeValue;
    } catch (e2) {
      console.warn('时间值序列化失败:', e2);
      return '';
    }
  }
}

// 获取试卷列表
const loadExamPapers = async () => {
  try {
    if (!filterForm.examId) {
      examPapers.value = []
      total.value = 0
      return
    }

    const response = await paperService.getPapersByExamId(filterForm.examId)
    // 转换数据格式以适配前端显示
    examPapers.value = response.data.map(paper => {
      // 修复字符编码问题
      const cleanName = (str) => {
        if (!str) return '';
        // 尝试修复可能的编码问题
        try {
          return decodeURIComponent(escape(str));
        } catch (e) {
          return str;
        }
      };

      // 获取客观题数量
      let objectiveCount = 0;
      if (paper.objective_count !== undefined) {
        // 优先使用后端直接提供的客观题数量
        objectiveCount = paper.objective_count;
      } else if (paper.objective_details && Array.isArray(paper.objective_details)) {
        // 如果有objective_details数组，通过数组长度计算
        objectiveCount = paper.objective_details.length;
      } else if (paper.objective_details) {
        // 如果是对象而不是数组
        objectiveCount = Object.keys(paper.objective_details).length;
      }

      return {
        id: paper.id || paper.number,
        studentName: cleanName((paper.user?.first_name || '') + (paper.user?.last_name || '')) || '未知学生',
        studentId: paper.user?.id || '',
        className: cleanName(paper.user?.class1?.name || '未知班级'),
        submitTime: formatSubmitTime(paper.end_time),
        objectiveCount: objectiveCount, // 正确计算客观题数量
        status: paper.status ? 'graded' : 'pending',
        objectiveScore: paper.objective_score !== undefined ? paper.objective_score : 0, // 正确处理客观题得分
        totalObjectiveScore: paper.total_objective_score !== undefined ? paper.total_objective_score : 0 // 正确处理客观题总分
      }
    });
    total.value = response.data.length
  } catch (error) {
    console.error('获取试卷列表失败:', error)
    ElMessage.error('获取试卷列表失败: ' + (error.response?.data?.message || error.message))
    examPapers.value = []
    total.value = 0
  }
}

const handleSelectionChange = (val) => {
  selectedPapers.value = val
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadExamPapers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadExamPapers()
}

// 处理显示详情的变更
const handleShowDetailsChange = (val) => {
  showGradingDetails.value = val
}

// 开始自动批改
const startAutoGrading = async () => {
  if (selectedPapers.value.length === 0) {
    ElMessage.warning('请先选择需要批改的试卷')
    return
  }

  gradingDialogVisible.value = true
  gradingProgress.value = 0
  gradingStatus.value = '正在批改...'
  gradingFinished.value = false
  showGradingDetails.value = false
  currentGradingDetails.value = []

  try {
    // 对每份试卷进行自动批改
    for (let i = 0; i < selectedPapers.value.length; i++) {
      const paper = selectedPapers.value[i]
      const response = await paperService.autoGradeObjective(paper.id)

      // 更新进度
      gradingProgress.value = Math.round(((i + 1) / selectedPapers.value.length) * 100)
      console.log(response)
      // 处理批改详情
      if (response.data.grading_details) {
        currentGradingDetails.value = response.data.grading_details.map(detail => ({
          questionNumber: detail.question_number,
          studentAnswer: detail.student_answer || '',
          correctAnswer: detail.correct_answer || '',
          isCorrect: detail.is_correct || false,
          score: detail.score || 0,
          maxScore: detail.max_score || 0
        }))
      }

      // 显示批改结果
      ElMessage.success(`试卷 ${response.data.paper_id} 批改完成，客观题得分: ${response.data.objective_score}/${response.data.total_objective_score}`)

      // 更新试卷列表中的分数和数量
      const index = examPapers.value.findIndex(p => p.id === paper.id)
      if (index !== -1) {
        examPapers.value[index].objectiveScore = response.data.objective_score
        examPapers.value[index].totalObjectiveScore = response.data.total_objective_score
        // 如果返回了客观题数量，则更新
        if (response.data.objective_count !== undefined) {
          examPapers.value[index].objectiveCount = response.data.objective_count
        }
        examPapers.value[index].status = 'graded'
      }
    }

    gradingStatus.value = '批改完成'
    gradingFinished.value = true

    ElMessage.success('自动批改完成')
  } catch (error) {
    console.error('自动批改失败:', error)
    const errorMessage = error.response?.data?.error || error.message || '未知错误'
    ElMessage.error('自动批改失败: ' + errorMessage)
    gradingStatus.value = '批改失败'
    gradingFinished.value = true
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.auto-grade-container {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 32px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
  animation: fadeInDown 0.8s ease;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 12px 0;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
  margin: 0;
}

.filter-card, .papers-card {
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease;
}

.filter-card:hover, .papers-card:hover {
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
  color: #1f2937;
  font-size: 18px;
}

.header-content i {
  font-size: 22px;
  color: #667eea;
}

.filter-form {
  width: 100%;
  padding: 24px;
}

.filter-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #4b5563;
  font-size: 14px;
}

.filter-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e5e7eb inset;
  transition: all 0.3s ease;
}

.filter-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #a3bffa inset;
}

.filter-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2), 0 0 0 1px #667eea inset;
}

.gradient-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  padding: 12px 24px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.gradient-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.gradient-button:disabled {
  background: linear-gradient(135deg, #d1d5db, #9ca3af);
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

.modern-table :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.modern-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.modern-table :deep(.el-table__body tr) {
  transition: all 0.2s ease;
}

.modern-table :deep(.el-table__body tr:hover) {
  background: rgba(102, 126, 234, 0.05);
}

.student-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.student-info i {
  color: #667eea;
  font-size: 16px;
}

.status-tag {
  border-radius: 20px;
  padding: 6px 14px;
  font-weight: 600;
  font-size: 12px;
}

.score-text {
  font-weight: 700;
  color: #667eea;
  font-size: 15px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.modern-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modern-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  border-bottom: none;
}

.modern-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 700;
  font-size: 18px;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.progress-bar {
  margin: 24px 0;
}

.progress-bar :deep(.el-progress__text) {
  font-weight: 700;
  color: #667eea;
}

.progress-status {
  text-align: center;
  font-weight: 600;
  color: #4b5563;
  font-size: 16px;
  margin: 16px 0;
}

.detail-checkbox {
  font-weight: 600;
  color: #667eea;
}

.detail-table {
  border-radius: 12px;
  overflow: hidden;
  margin-top: 16px;
}

.detail-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  color: #4b5563;
  font-weight: 600;
}

.result-tag {
  border-radius: 15px;
  padding: 4px 12px;
  font-weight: 600;
  font-size: 12px;
}

.dialog-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  text-align: right;
}

.footer-button {
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.footer-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .auto-grade-container {
    padding: 16px;
  }

  .page-header {
    padding: 24px 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .filter-card, .papers-card {
    border-radius: 12px;
  }

  .card-header {
    padding: 16px;
  }

  .filter-form {
    padding: 16px;
  }

  .gradient-button {
    padding: 10px 16px;
  }
}
</style>
