<template>
  <div class="grade-summary-container">
    <!-- 页面标题 -->


    <el-card class="filter-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-search"></i>
            <span>选择考试</span>
          </div>
        </div>
      </template>
      <el-form :model="filterForm" label-width="80px" class="filter-form">
        <el-form-item label="考试名称">
          <el-select
            v-model="filterForm.examId"
            placeholder="请选择考试"
            clearable
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="exam.name"
              :value="exam.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="integrateGrades" :disabled="!filterForm.examId" :loading="loading" class="gradient-button">开始成绩整合</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="summaryData" class="result-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-data-analysis"></i>
            <span>{{ summaryData.exam_name }} - 成绩整合结果</span>
          </div>
        </div>
      </template>

      <!-- 统计概览 -->
      <div class="stats-grid">
        <div class="stat-item" v-for="(stat, index) in mainStats" :key="index">
          <div class="stat-card">
            <div class="stat-icon" :style="{ backgroundColor: stat.color + '20', color: stat.color }">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分项得分统计 -->
      <div class="section-title">
        <i class="el-icon-tickets"></i>
        <span>分项得分统计</span>
      </div>
      <div class="stats-grid">
        <div class="stat-item" v-for="(stat, index) in scoreStats" :key="index">
          <div class="stat-card">
            <div class="stat-icon" :style="{ backgroundColor: stat.color + '20', color: stat.color }">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最高分统计 -->
      <div class="section-title">
        <i class="el-icon-medal"></i>
        <span>最高分统计</span>
      </div>
      <div class="stats-grid">
        <div class="stat-item" v-for="(stat, index) in highestStats" :key="index">
          <div class="stat-card">
            <div class="stat-icon" :style="{ backgroundColor: stat.color + '20', color: stat.color }">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 试卷详细信息 -->
    <el-card v-if="summaryData && summaryData.paper_details && summaryData.paper_details.length > 0" class="details-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-document"></i>
            <span>试卷详细信息</span>
          </div>
        </div>
      </template>

      <el-table :data="summaryData.paper_details" style="width: 100%" max-height="400" class="modern-table" stripe>
        <el-table-column prop="paper_id" label="试卷ID" width="80"></el-table-column>
        <el-table-column prop="student_name" label="学生姓名" width="120">
          <template #default="scope">
            <div class="student-info">
              <i class="el-icon-user"></i>
              <span>{{ scope.row.student_name || '未知学生' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已批改' ? 'success' : 'warning'" class="status-tag">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="objective_score" label="客观题得分" width="120">
          <template #default="scope">
            <span class="score-text">{{ scope.row.objective_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="subjective_score" label="主观题得分" width="120">
          <template #default="scope">
            <span class="score-text">{{ scope.row.subjective_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="100">
          <template #default="scope">
            <span class="total-score">{{ scope.row.total_score }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import examService from '@/services/examService'
import paperService from '@/services/paperService'

const filterForm = reactive({
  examId: ''
})

const exams = ref([])
const summaryData = ref(null)
const loading = ref(false)

// 主要统计数据
const mainStats = computed(() => {
  if (!summaryData.value) return []

  return [
    {
      label: '总试卷数',
      value: summaryData.value.stats.total_papers,
      icon: 'el-icon-document',
      color: '#409eff'
    },
    {
      label: '已批改试卷',
      value: summaryData.value.stats.graded_papers,
      icon: 'el-icon-finished',
      color: '#67c23a'
    },
    {
      label: '未批改试卷',
      value: summaryData.value.stats.ungraded_papers,
      icon: 'el-icon-warning-outline',
      color: '#e6a23c'
    },
    {
      label: '平均总分',
      value: summaryData.value.stats.average_total_score,
      icon: 'el-icon-data-analysis',
      color: '#909399'
    }
  ]
})

// 分数统计数据
const scoreStats = computed(() => {
  if (!summaryData.value) return []

  return [
    {
      label: '客观题平均分',
      value: summaryData.value.stats.average_objective_score,
      icon: 'el-icon-edit',
      color: '#409eff'
    },
    {
      label: '主观题平均分',
      value: summaryData.value.stats.average_subjective_score,
      icon: 'el-icon-edit-outline',
      color: '#67c23a'
    },
    {
      label: '及格率',
      value: summaryData.value.stats.pass_rate + '%',
      icon: 'el-icon-check',
      color: '#67c23a'
    },
    {
      label: '优秀率',
      value: summaryData.value.stats.excellent_rate + '%',
      icon: 'el-icon-star-on',
      color: '#e6a23c'
    }
  ]
})

// 最高分统计数据
const highestStats = computed(() => {
  if (!summaryData.value) return []

  return [
    {
      label: '最高总分',
      value: summaryData.value.stats.highest_total_score,
      icon: 'el-icon-medal-1',
      color: '#ea8282'
    },
    {
      label: '客观题最高分',
      value: summaryData.value.stats.highest_objective_score,
      icon: 'el-icon-medal',
      color: '#409eff'
    },
    {
      label: '主观题最高分',
      value: summaryData.value.stats.highest_subjective_score,
      icon: 'el-icon-medal',
      color: '#67c23a'
    }
  ]
})

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
  } catch (error) {
    console.error('获取考试列表失败:', error)
    ElMessage.error('获取考试列表失败: ' + (error.response?.data?.message || error.message))
    exams.value = []
  }
}

// 成绩整合
const integrateGrades = async () => {
  if (!filterForm.examId) {
    ElMessage.warning('请选择考试')
    return
  }

  loading.value = true
  try {
    const response = await paperService.integrateGrades({
      exam_id: filterForm.examId
    })

    summaryData.value = response.data
    ElMessage.success(response.data.message || '成绩整合完成')
  } catch (error) {
    console.error('成绩整合失败:', error)
    ElMessage.error('成绩整合失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadExams()
})
</script>

<style scoped>
.grade-summary-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e4f3ff 0%, #f0f9ff 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  animation: fadeInDown 0.8s ease;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1a73e8;
  text-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
}

.page-subtitle {
  font-size: 16px;
  color: #5f6368;
  font-weight: 400;
}

.filter-card, .result-card, .details-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease;
}

.filter-card:hover, .result-card:hover, .details-card:hover {
  box-shadow: 0 15px 40px rgba(26, 115, 232, 0.25);
  transform: translateY(-5px);
}

.glass-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1a73e8;
  font-size: 18px;
}

.header-content i {
  font-size: 20px;
  color: #1a73e8;
}

.filter-form {
  width: 100%;
  padding: 20px;
}

.gradient-button {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  border: none;
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
}

.gradient-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(26, 115, 232, 0.4);
}

.gradient-button:disabled {
  background: #c0c4cc;
  transform: none;
  box-shadow: none;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  margin: 25px 0 15px;
  color: #1a73e8;
}

.section-title i {
  color: #1a73e8;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 10px;
}

.stat-item {
  margin-bottom: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.05);
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(26, 115, 232, 0.15);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 5px;
  color: #1a73e8;
}

.stat-label {
  font-size: 14px;
  color: #5f6368;
}

.modern-table :deep(.el-table__row:hover) {
  background-color: #f0f9ff;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  border-radius: 20px;
  padding: 5px 12px;
}

.score-text {
  font-weight: 600;
  color: #1a73e8;
}

.total-score {
  font-weight: 700;
  color: #1a73e8;
}

@media (max-width: 768px) {
  .grade-summary-container {
    padding: 15px;
  }

  .page-title {
    font-size: 24px;
  }

  .filter-card, .result-card, .details-card {
    border-radius: 10px;
  }

  .card-header {
    padding: 15px;
  }

  .filter-form {
    padding: 15px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 15px;
  }

  .stat-value {
    font-size: 20px;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
