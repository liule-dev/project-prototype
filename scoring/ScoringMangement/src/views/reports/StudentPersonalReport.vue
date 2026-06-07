<template>
  <div class="student-report-container">
    <!-- 页面标题和返回按钮 -->
    <div class="header-container">
      <h2 class="page-title">学生个人报告</h2>
      <el-button 
        type="primary" 
        :icon="House" 
        @click="goHome"
        class="home-button gradient-button"
      >
        返回主页
      </el-button>
    </div>
    
    <!-- 筛选条件卡片 -->
    <el-card class="filter-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-search"></i>
            <span>筛选条件</span>
          </div>
        </div>
      </template>
      <!-- 筛选表单 -->
      <el-form :model="filterForm" class="filter-form" label-width="80px">
        <el-row :gutter="20" class="filter-row">
          <!-- 考试名称选择器 -->
          <el-col :xs="24" :sm="24" :md="18" :lg="20" class="filter-col">
            <el-form-item label="考试名称" class="exam-form-item">
              <el-select 
                v-model="filterForm.examId" 
                @change="loadReport" 
                clearable
                class="exam-select"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="exam in exams"
                  :key="exam.id"
                  :label="exam.name"
                  :value="exam.id">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <!-- 查询按钮列 -->
          <el-col :xs="24" :sm="24" :md="6" :lg="4" class="button-col">
            <el-form-item class="button-form-item">
              <el-button 
                type="primary" 
                @click="loadReport" 
                :disabled="!filterForm.examId"
                class="query-button gradient-button"
                style="width: 100%">
                查询
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 报告内容卡片 -->
    <el-card class="report-card glass-card" v-if="reportData">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-data-analysis"></i>
            <span>{{ reportData.exam_name }} 个人成绩报告</span>
          </div>
        </div>
      </template>
      
      <el-row :gutter="20">
        <!-- 左侧内容区域 -->
        <el-col :xs="24" :lg="16">
          <!-- 成绩概览卡片 -->
          <el-card class="overview-card glass-card">
            <template #header>
              <div class="card-header">
                <div class="header-content">
                  <i class="el-icon-view"></i>
                  <span>成绩概览</span>
                </div>
              </div>
            </template>
            <!-- 成绩分数展示 -->
            <el-row :gutter="20">
              <!-- 客观题得分 -->
              <el-col :xs="24" :sm="8">
                <div class="score-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(64, 158, 255, 0.2); color: #409eff;">
                    <i class="el-icon-edit"></i>
                  </div>
                  <div class="stat-info">
                    <div class="score-label">客观题得分</div>
                    <div class="score-value">{{ formatScore(reportData.objective_score) }}<span class="score-total">/{{ formatScore(reportData.objective_total) }}</span></div>
                  </div>
                </div>
              </el-col>
              <!-- 主观题得分 -->
              <el-col :xs="24" :sm="8">
                <div class="score-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(103, 194, 58, 0.2); color: #67c23a;">
                    <i class="el-icon-edit-outline"></i>
                  </div>
                  <div class="stat-info">
                    <div class="score-label">主观题得分</div>
                    <div class="score-value">{{ formatScore(reportData.subjective_score) }}<span class="score-total">/{{ formatScore(reportData.subjective_total) }}</span></div>
                  </div>
                </div>
              </el-col>
              <!-- 总分 -->
              <el-col :xs="24" :sm="8">
                <div class="score-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(245, 108, 108, 0.2); color: #f56c6c;">
                    <i class="el-icon-star-on"></i>
                  </div>
                  <div class="stat-info">
                    <div class="score-label">总分</div>
                    <div class="score-value">{{ formatScore(reportData.total_score) }}<span class="score-total">/{{ formatScore(reportData.total_total) }}</span></div>
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <!-- 排名信息 -->
            <el-row :gutter="20" style="margin-top: 20px;">
              <!-- 班级排名 -->
              <el-col :xs="24" :sm="8">
                <div class="rank-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(144, 147, 153, 0.2); color: #909399;">
                    <i class="el-icon-medal"></i>
                  </div>
                  <div class="stat-info">
                    <div class="rank-label">班级排名</div>
                    <div class="rank-value">{{ reportData.class_rank }}<span class="rank-change" :class="reportData.class_rank_change >= 0 ? 'up' : 'down'">{{ reportData.class_rank_change >= 0 ? '↑' : '↓' }}{{ Math.abs(reportData.class_rank_change) }}</span></div>
                  </div>
                </div>
              </el-col>
              <!-- 年级排名 -->
              <el-col :xs="24" :sm="8">
                <div class="rank-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(230, 162, 60, 0.2); color: #e6a23c;">
                    <i class="el-icon-trophy"></i>
                  </div>
                  <div class="stat-info">
                    <div class="rank-label">年级排名</div>
                    <div class="rank-value">{{ reportData.school_rank }}<span class="rank-change" :class="reportData.school_rank_change >= 0 ? 'up' : 'down'">{{ reportData.school_rank_change >= 0 ? '↑' : '↓' }}{{ Math.abs(reportData.school_rank_change) }}</span></div>
                  </div>
                </div>
              </el-col>
              <!-- 超越比例 -->
              <el-col :xs="24" :sm="8">
                <div class="rank-item stat-card">
                  <div class="stat-icon" style="background-color: rgba(157, 83, 217, 0.2); color: #9d53d9;">
                    <i class="el-icon-data-line"></i>
                  </div>
                  <div class="stat-info">
                    <div class="rank-label">超越比例</div>
                    <div class="rank-value">{{ reportData.exceed_percentage }}%</div>
                  </div>
                </div>
              </el-col>
            </el-row>
            
            <!-- 进度条和成绩等级 -->
            <div style="margin-top: 20px;">
              <!-- 成绩进度条 -->
              <el-progress :percentage="Math.round((reportData.total_score / reportData.total_total) * 100)" :status="getProgressStatus(reportData.total_score, reportData.total_total)" class="score-progress"></el-progress>
              <!-- 成绩等级标签 -->
              <div style="text-align: center; margin-top: 15px;">
                <el-tag :type="getScoreLevelType(reportData.score_level)" class="score-level-tag">{{ reportData.score_level }}</el-tag>
              </div>
            </div>
          </el-card>
          
          <!-- 能力分析图表卡片 -->
          <el-card class="chart-card glass-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <div class="header-content">
                  <i class="el-icon-pie-chart"></i>
                  <span>能力分析</span>
                </div>
              </div>
            </template>
            <!-- 图表容器 -->
            <div ref="chartContainer" class="chart-container"></div>
          </el-card>
        </el-col>
        
        <!-- 右侧内容区域 -->
        <el-col :xs="24" :lg="8">
          <!-- 主观题详情卡片 -->
          <el-card class="subjective-card glass-card">
            <template #header>
              <div class="card-header">
                <div class="header-content">
                  <i class="el-icon-document"></i>
                  <span>主观题详情</span>
                </div>
              </div>
            </template>
            <!-- 主观题详情表格 -->
            <el-table :data="reportData.subjective_details" style="width: 100%" max-height="300" class="subjective-table">
              <el-table-column prop="questionNumber" label="题号" :width="isMobile ? 50 : 60" align="center"></el-table-column>
              <el-table-column prop="givenScore" label="得分" :width="isMobile ? 50 : 60" align="center">
                <template #default="scope">
                  <span class="score-text">{{ scope.row.givenScore }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="score" label="满分" :width="isMobile ? 50 : 60" align="center"></el-table-column>
              <el-table-column prop="comment" label="评语"></el-table-column>
            </el-table>
          </el-card>
          
          <!-- 学习建议卡片 -->
          <el-card class="suggestion-card glass-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <div class="header-content">
                  <i class="el-icon-lightning"></i>
                  <span>学习建议</span>
                </div>
              </div>
            </template>
            <!-- 学习建议内容 -->
            <div class="suggestion-content">
              <p class="suggestion-title">根据您的答题情况，建议您：</p>
              <ul class="suggestion-list">
                <li v-for="(suggestion, index) in reportData.learning_suggestions" :key="index" class="suggestion-item">
                  <i class="el-icon-check"></i>
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 提示信息弹窗：未选择考试时显示 -->
    <el-dialog v-model="infoDialogVisible" title="提示" width="30%" center class="modern-dialog">
      <div class="dialog-content">
        <i class="el-icon-warning-outline" style="font-size: 48px; color: #e6a23c; display: block; text-align: center; margin-bottom: 15px;"></i>
        <span style="display: block; text-align: center; font-size: 16px;">请选择考试进行查询</span>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="infoDialogVisible = false" class="footer-button">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 无数据提示弹窗 -->
    <el-dialog v-model="emptyDialogVisible" title="提示" width="30%" center class="modern-dialog">
      <div class="dialog-content">
        <i class="el-icon-info" style="font-size: 48px; color: #409eff; display: block; text-align: center; margin-bottom: 15px;"></i>
        <span style="display: block; text-align: center; font-size: 16px;">暂无数据，请选择其他考试</span>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="emptyDialogVisible = false" class="footer-button">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import examService from '@/services/examService'
import reportService from '@/services/reportService'
import { House } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 筛选表单数据
const filterForm = reactive({
  examId: ''  // 选中的考试ID
})

// 考试列表数据
const exams = ref([])
// 报告数据
const reportData = ref(null)
// 图表容器引用
const chartContainer = ref(null)
// 图表实例
let chartInstance = null
// 提示信息弹窗显示状态
const infoDialogVisible = ref(false)
// 无数据提示弹窗显示状态
const emptyDialogVisible = ref(false)

// 返回主页功能
const goHome = () => {
  router.push('/main');
};

// 检测是否为移动设备
const isMobile = computed(() => {
  return window.innerWidth < 768
})

// 格式化分数显示，保留一位小数
const formatScore = (score) => {
  return typeof score === 'number' ? score.toFixed(1) : score
}

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
    // 根据规范，取消弹窗提示，仅在控制台输出错误日志
    exams.value = []
  }
}

// 获取报表数据
const loadReport = async () => {
  // 检查是否已选择考试
  if (!filterForm.examId) {
    // 显示提示弹窗
    infoDialogVisible.value = true
    return
  }

  try {
    // 构造请求参数
    const params = {
      exam_id: filterForm.examId
    }
    
    // 调用服务获取个人报告数据
    const response = await reportService.getPersonalReport(params)
    // 检查响应数据是否包含错误信息
    if (response.data.message) {
      emptyDialogVisible.value = true
      reportData.value = null
      return
    }
    
    reportData.value = response.data
    
    // 等待DOM更新后绘制图表
    await nextTick()
    drawChart()
  } catch (error) {
    console.error('获取报表数据失败:', error)
    // 根据规范，取消弹窗提示，仅在控制台输出错误日志
    reportData.value = null
  }
}

// 绘制能力分析图表
const drawChart = () => {
  // 检查图表容器和报告数据是否存在
  if (!chartContainer.value || !reportData.value) return
  
  // 如果已有图表实例，先销毁
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  // 初始化图表
  chartInstance = echarts.init(chartContainer.value)
  
  // 图表配置选项
  const option = {
    radar: {
      // 雷达图指示器
      indicator: reportData.value.abilities.map(item => ({
        name: item.name,
        max: 100
      })),
      shape: 'polygon',         // 雷达图形状
      splitNumber: 5,           // 分隔区域数量
      axisName: {
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      splitArea: {
        show: false
      },
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      }
    },
    series: [{
      type: 'radar',            // 图表类型为雷达图
      data: [{
        value: reportData.value.abilities.map(item => item.score),
        name: '能力分析',
        lineStyle: {
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: '#409EFF',
          opacity: 0.3
        }
      }]
    }]
  }
  
  // 设置图表选项
  chartInstance.setOption(option)
}

// 获取进度条状态
const getProgressStatus = (score, total) => {
  const percentage = (score / total) * 100
  if (percentage >= 80) return 'success'   // 优秀（80分以上）
  if (percentage >= 60) return 'warning'   // 良好（60分以上）
  return 'exception'                       // 不及格（60分以下）
}

// 获取成绩等级标签类型
const getScoreLevelType = (level) => {
  switch (level) {
    case '优秀': return 'success'
    case '良好': return 'primary'
    case '中等': return 'warning'
    case '及格': return 'info'
    case '不及格': return 'danger'
    default: return 'info'
  }
}

// 窗口大小改变时重绘图表
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadExams()
  window.addEventListener('resize', handleResize)
})

// 组件卸载前清理
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* 学生报告容器样式 */
.student-report-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e4f3ff 0%, #f0f9ff 100%);
  min-height: 100vh;
}

/* 页面标题和返回按钮容器 */
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
  animation: fadeInDown 0.8s ease;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a73e8;
  text-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
}

/* 筛选卡片和报告卡片样式 */
.filter-card, .report-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease;
}

.filter-card:hover, .report-card:hover {
  box-shadow: 0 15px 40px rgba(26, 115, 232, 0.25);
  transform: translateY(-5px);
}

.glass-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
  flex-wrap: wrap;
  gap: 10px;
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

/* 分数项样式 */
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

/* 分数标签样式 */
.score-label, .rank-label {
  font-size: 14px;
  color: #5f6368;
  margin-bottom: 5px;
}

/* 分数值样式 */
.score-value, .rank-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a73e8;
}

/* 分数总分样式 */
.score-total {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

/* 排名变化样式 */
.rank-change {
  font-size: 12px;
  margin-left: 5px;
}

.rank-change.up {
  color: #67c23a;
}

.rank-change.down {
  color: #f56c6c;
}

/* 学习建议内容样式 */
.suggestion-content {
  padding: 15px;
}

.suggestion-title {
  font-weight: 600;
  color: #1a73e8;
  margin-bottom: 15px;
  font-size: 16px;
}

.suggestion-list {
  padding-left: 20px;
}

.suggestion-item {
  margin-bottom: 10px;
  color: #5f6368;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.suggestion-item i {
  color: #1a73e8;
  margin-top: 3px;
}

/* 筛选表单样式 */
.filter-form {
  width: 100%;
  padding: 20px;
}

/* 筛选行样式 */
.filter-row {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end; /* 确保子元素底部对齐 */
  gap: 20px; /* 添加间距 */
}

/* 筛选列样式 */
.filter-col {
  display: flex;
  flex-direction: column;
}

/* 表单元素样式 */
.exam-form-item {
  flex: 1;
  margin-bottom: 0;
}

.button-form-item {
  display: flex;
  align-items: flex-end;
  height: 100%;
  margin-bottom: 0;
  justify-content: flex-start;
}

.query-button {
  width: 100%;
  min-width: 80px;
  height: 40px; /* 确保按钮高度 */
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

/* 图表容器样式 */
.chart-container {
  width: 100%;
  height: 300px;
}

.score-progress {
  border-radius: 10px;
  overflow: hidden;
}

.score-level-tag {
  border-radius: 20px;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 600;
}

.subjective-table :deep(.el-table__row:hover) {
  background-color: #f0f9ff;
}

.score-text {
  font-weight: 700;
  color: #1a73e8;
}

.dialog-content {
  padding: 20px 0;
}

.footer-button {
  padding: 10px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.footer-button:hover {
  background: #e4e7ed;
}

.modern-dialog :deep(.el-dialog__header) {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  color: white;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.modern-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 500;
}

/* 筛选器响应式调整 */
@media (max-width: 1200px) {
  .filter-col:first-child {
    margin-bottom: 10px;
  }
  
  .button-form-item {
    justify-content: flex-start;
  }
  
  .query-button {
    height: auto;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-report-container {
    padding: 15px;
  }
  
  .header-container {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 20px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .home-button {
    align-self: flex-end;
  }
  
  .filter-card, .report-card {
    border-radius: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
  }
  
  .filter-form {
    padding: 15px;
  }
  
  .stat-card {
    padding: 15px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .score-value, .rank-value {
    font-size: 20px;
  }
  
  .chart-container {
    height: 250px;
  }
  
  /* 在小屏幕上调整筛选器布局 */
  .filter-row {
    flex-direction: column; /* 在中等屏幕上保持横向布局 */
    gap: 10px;
  }
  
  .button-form-item {
    justify-content: flex-start;
  }
  
  .query-button {
    width: 100%;
    min-width: 80px;
    height: 40px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
}

@media (max-width: 576px) {
  /* 在小屏幕上改为纵向布局 */
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .query-button {
    width: 100%;
    min-width: auto;
  }
  
  .score-value, .rank-value {
    font-size: 18px;
  }
  
  .chart-container {
    height: 200px;
  }
  
  .el-col {
    margin-bottom: 10px;
  }
  
  .suggestion-content {
    padding: 10px;
  }
  
  .suggestion-title {
    font-size: 14px;
  }
  
  .suggestion-item {
    font-size: 14px;
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