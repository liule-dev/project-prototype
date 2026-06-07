<template>
  <div class="exam-management-container">
    <!-- 页面标题 -->
    <!-- 页面标题 -->
<div class="page-header">
  <!-- 标题组：用 flex 包裹并自动外边距拉到左侧，再通过 margin-left: auto 让其视觉居中 -->
  <div class="title-wrapper">
    <h1 class="page-title">考试管理系统</h1>
    <p class="page-subtitle">创建、管理和监控考试活动</p>
  </div>
  <el-button
    type="default"
    @click="jupe"
    class="back-home-btn"
    icon="ArrowLeft"
    plain
  >
    返回主页
  </el-button>
</div>



    <!-- 标签页区域 -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- 考试创建/编辑 Tab -->
      <el-tab-pane label="创建/编辑考试" name="create">
        <div class="tab-content">
          <div class="form-card">
            <div class="form-header">
              <h2 class="form-title">{{ examForm.id ? '编辑考试' : '创建考试' }}</h2>
              <div class="form-actions">
                <el-button type="primary" @click="submitForm" class="submit-btn">
                  <el-icon><Check /></el-icon>
                  <span>提交</span>
                </el-button>
                <el-button @click="resetForm" class="reset-btn">
                  <el-icon><Refresh /></el-icon>
                  <span>重置</span>
                </el-button>
              </div>
            </div>

            <el-form
              :model="examForm"
              :rules="examRules"
              ref="examFormRef"
              label-width="120px"
              class="exam-form"
            >
              <!-- 基础信息部分 -->
              <div class="form-section">
                <h3 class="section-title">基础信息</h3>
                <div class="form-grid">
                  <el-form-item label="考试名称" prop="exam_name" class="form-item">
                    <el-input
                      v-model="examForm.exam_name"
                      placeholder="请输入考试名称"
                      class="form-input"
                    />
                  </el-form-item>

                  <el-form-item label="科目" prop="subject_id" class="form-item">
                    <el-select
                      v-model="examForm.subject_id"
                      placeholder="请选择科目"
                      class="form-select"
                      @change="handleSubjectChange"
                    >
                      <el-option
                        v-for="subject in subjects"
                        :key="subject.id"
                        :label="subject.subject_name"
                        :value="subject.id"
                      />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="总分" prop="all_score" class="form-item">
                    <el-input
                      v-model.number="examForm.all_score"
                      type="number"
                      placeholder="请输入总分"
                      class="form-input"
                    />
                  </el-form-item>

                  <el-form-item label="及格线" prop="passing_score" class="form-item">
                    <el-input
                      v-model.number="examForm.passing_score"
                      type="number"
                      placeholder="请输入及格线"
                      class="form-input"
                    />
                  </el-form-item>

                  <el-form-item label="考试时长" prop="duration" class="form-item">
                    <el-input
                      v-model.number="examForm.duration"
                      type="number"
                      placeholder="分钟"
                      class="form-input"
                    >
                      <template #append>分钟</template>
                    </el-input>
                  </el-form-item>

                  <el-form-item label="难度" prop="difficulty" class="form-item">
                    <el-select
                      v-model="examForm.difficulty"
                      placeholder="请选择难度"
                      class="form-select"
                    >
                      <el-option label="简单" value="简单" />
                      <el-option label="中等" value="中等" />
                      <el-option label="困难" value="困难" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="开始时间" prop="begin_time" class="form-item">
                    <el-date-picker
                      v-model="examForm.begin_time"
                      type="datetime"
                      placeholder="请选择开始时间"
                      class="form-date-picker"
                    />
                  </el-form-item>

                  <el-form-item label="结束时间" prop="end_time" class="form-item">
                    <el-date-picker
                      v-model="examForm.end_time"
                      type="datetime"
                      placeholder="请选择结束时间"
                      class="form-date-picker"
                    />
                  </el-form-item>

                  <el-form-item label="抽题规则" prop="draw_rule" class="form-item">
                    <el-select
                      v-model="examForm.draw_rule"
                      placeholder="请选择抽题规则"
                      class="form-select"
                    >
                      <el-option label="随机抽题" value="random" />
                      <el-option label="手动选题" value="manual" />
                    </el-select>
                  </el-form-item>
                </div>
              </div>

              <!-- 手动选题区域 -->
              <div v-if="examForm.draw_rule === 'manual' && hasManualTopics" class="manual-topics-container">
                <div class="form-section">
                  <h3 class="section-title">手动选题</h3>
                  
                  <!-- 单项选择题 -->
                  <div v-if="subjectConfig.choice_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      单项选择题 ({{ subjectConfig.choice_count }}题，每题{{ subjectConfig.choice_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.choice" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="3" placeholder="请输入题干" />
                      </el-form-item>
                      <el-row :gutter="10">
                        <el-col :span="6">
                          <el-form-item label="A" class="topic-item">
                            <el-input v-model="topic.A" placeholder="选项A" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="B" class="topic-item">
                            <el-input v-model="topic.B" placeholder="选项B" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="C" class="topic-item">
                            <el-input v-model="topic.C" placeholder="选项C" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="D" class="topic-item">
                            <el-input v-model="topic.D" placeholder="选项D" />
                          </el-form-item>
                        </el-col>
                      </el-row>
                      <el-form-item label="正确答案" class="topic-item">
                        <el-select v-model="topic.topic_answer" placeholder="请选择正确答案">
                          <el-option label="A" value="A" />
                          <el-option label="B" value="B" />
                          <el-option label="C" value="C" />
                          <el-option label="D" value="D" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </div>

                  <!-- 多项选择题 -->
                  <div v-if="subjectConfig.multiple_choice_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      多项选择题 ({{ subjectConfig.multiple_choice_count }}题，每题{{ subjectConfig.multiple_choice_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.multiple_choice" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="3" placeholder="请输入题干" />
                      </el-form-item>
                      <el-row :gutter="10">
                        <el-col :span="6">
                          <el-form-item label="A" class="topic-item">
                            <el-input v-model="topic.A" placeholder="选项A" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="B" class="topic-item">
                            <el-input v-model="topic.B" placeholder="选项B" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="C" class="topic-item">
                            <el-input v-model="topic.C" placeholder="选项C" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="6">
                          <el-form-item label="D" class="topic-item">
                            <el-input v-model="topic.D" placeholder="选项D" />
                          </el-form-item>
                        </el-col>
                      </el-row>
                      <el-form-item label="正确答案" class="topic-item">
                        <el-select v-model="topic.topic_answer" multiple placeholder="请选择正确答案">
                          <el-option label="A" value="A" />
                          <el-option label="B" value="B" />
                          <el-option label="C" value="C" />
                          <el-option label="D" value="D" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </div>

                  <!-- 判断题 -->
                  <div v-if="subjectConfig.judgment_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      判断题 ({{ subjectConfig.judgment_count }}题，每题{{ subjectConfig.judgment_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.judgment" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="3" placeholder="请输入题干" />
                      </el-form-item>
                      <el-form-item label="正确答案" class="topic-item">
                        <el-radio-group v-model="topic.topic_answer">
                          <el-radio label="对">对</el-radio>
                          <el-radio label="错">错</el-radio>
                        </el-radio-group>
                      </el-form-item>
                    </div>
                  </div>

                  <!-- 案例分析题 -->
                  <div v-if="subjectConfig.case_analysis_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      案例分析题 ({{ subjectConfig.case_analysis_count }}题，每题{{ subjectConfig.case_analysis_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.case_analysis" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="5" placeholder="请输入题干" />
                      </el-form-item>
                      <el-form-item label="参考答案" class="topic-item">
                        <el-input v-model="topic.topic_answer" type="textarea" :rows="5" placeholder="请输入参考答案" />
                      </el-form-item>
                    </div>
                  </div>

                  <!-- 计算分析题 -->
                  <div v-if="subjectConfig.calculation_analysis_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      计算分析题 ({{ subjectConfig.calculation_analysis_count }}题，每题{{ subjectConfig.calculation_analysis_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.calculation_analysis" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="5" placeholder="请输入题干" />
                      </el-form-item>
                      <el-form-item label="参考答案" class="topic-item">
                        <el-input v-model="topic.topic_answer" type="textarea" :rows="5" placeholder="请输入参考答案" />
                      </el-form-item>
                    </div>
                  </div>

                  <!-- 综合题 -->
                  <div v-if="subjectConfig.comprehensive_count > 0" class="topic-type-section">
                    <h4 class="topic-type-title">
                      综合题 ({{ subjectConfig.comprehensive_count }}题，每题{{ subjectConfig.comprehensive_score }}分)
                    </h4>
                    <div v-for="(topic, index) in manualTopics.comprehensive" :key="index" class="topic-card">
                      <el-form-item :label="`第${index + 1}题题干`" class="topic-item">
                        <el-input v-model="topic.topic_content" type="textarea" :rows="5" placeholder="请输入题干" />
                      </el-form-item>
                      <el-form-item label="参考答案" class="topic-item">
                        <el-input v-model="topic.topic_answer" type="textarea" :rows="5" placeholder="请输入参考答案" />
                      </el-form-item>
                    </div>
                  </div>
                </div>
              </div>

            </el-form>
          </div>
        </div>
      </el-tab-pane>

      <!-- 考试列表 Tab -->
      <el-tab-pane label="考试列表" name="list">
        <div class="tab-content">
          <div class="list-header">
            <h2 class="list-title">考试列表</h2>
            <div class="list-actions">
              <el-button type="primary" @click="fetchExams" class="refresh-btn">
                <el-icon><Refresh /></el-icon>
                <span>刷新</span>
              </el-button>
            </div>
          </div>

          <div class="list-card">
            <el-table
              :data="exams"
              v-loading="loading"
              style="width: 100%"
              class="exam-table"
              :empty-text="'暂无考试数据'"
            >
              <el-table-column prop="name" label="考试名称" min-width="180" />
              <el-table-column prop="subject" label="科目" width="120" />
              <el-table-column prop="all_score" label="总分" width="90" align="center">
                <template #default="scope">
                  <span class="score-value">{{ scope.row.all_score }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="begin_time" label="开始时间" width="180">
                <template #default="scope">
                  <div class="time-cell">
                    <el-icon class="time-icon"><Clock /></el-icon>
                    <span>{{ formatDate(scope.row.begin_time) }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="end_time" label="结束时间" width="180">
                <template #default="scope">
                  <div class="time-cell">
                    <el-icon class="time-icon"><Clock /></el-icon>
                    <span>{{ formatDate(scope.row.end_time) }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100" align="center">
                <template #default="scope">
                  <el-tag
                    :type="scope.row.status ? 'success' : 'warning'"
                    class="status-tag"
                    :class="scope.row.status ? 'status-published' : 'status-draft'"
                  >
                    {{ scope.row.status ? '已发布' : '未发布' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="320" align="center" fixed="right">
                <template #default="scope">
                  <div class="action-buttons">
                    <el-button
                      size="small"
                      @click="editExam(scope.row)"
                      class="edit-btn"
                      :icon="Edit"
                    >
                      编辑
                    </el-button>
                    <el-button
                      size="small"
                      type="primary"
                      @click="publishExam(scope.row)"
                      :disabled="scope.row.status || !canManageExam(scope.row)"
                      class="publish-btn"
                      :icon="Promotion"
                    >
                      {{ scope.row.status ? '已发布' : '发布' }}
                    </el-button>
                    <el-button
                      size="small"
                      type="danger"
                      @click="deleteExam(scope.row)"
                      :disabled="!canManageExam(scope.row)"
                      class="delete-btn"
                      :icon="Delete"
                    >
                      删除
                    </el-button>
                    <el-button
                      size="small"
                      @click="showDetail(scope.row)"
                      class="detail-btn"
                      :icon="View"
                    >
                      详情
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 详情对话框 -->
    <el-dialog
      title="考试详情"
      v-model="detailDialogVisible"
      width="80%"
      class="detail-dialog"
      :close-on-click-modal="false"
    >
      <div v-if="selectedExam" class="detail-content">
        <div class="exam-info-card">
          <div class="info-header">
            <h3>{{ selectedExam.name }}</h3>
            <el-tag
              :type="selectedExam.status ? 'success' : 'warning'"
              class="status-tag"
              :class="selectedExam.status ? 'status-published' : 'status-draft'"
            >
              {{ selectedExam.status ? '已发布' : '未发布' }}
            </el-tag>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">科目</span>
              <span class="info-value">{{ selectedExam.subject }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">总分</span>
              <span class="info-value score-highlight">{{ selectedExam.all_score }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">及格线</span>
              <span class="info-value">{{ selectedExam.settings?.passing_score || '未设置' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">考试时长</span>
              <span class="info-value">{{ selectedExam.settings?.duration || '未设置' }}分钟</span>
            </div>
            <div class="info-item">
              <span class="info-label">开始时间</span>
              <span class="info-value">{{ formatDate(selectedExam.begin_time) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">结束时间</span>
              <span class="info-value">{{ formatDate(selectedExam.end_time) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">抽题规则</span>
              <span class="info-value">{{ selectedExam.settings?.draw_rule || '未设置' }}</span>
            </div>
          </div>
        </div>

        <div class="topics-section">
          <h4 class="section-title">试卷题目</h4>
          <div v-if="examTopics && examTopics.length > 0" class="topics-container">
            <el-card
              v-for="(topic, index) in examTopics"
              :key="topic.topic_number"
              class="topic-card"
            >
              <div class="topic-header">
                <span class="topic-number">第{{ index + 1 }}题</span>
                <el-tag
                  :type="getDifficultyType(topic.topic_difficulty)"
                  class="difficulty-tag"
                  :class="`difficulty-${topic.topic_difficulty}`"
                >
                  {{ formatDifficulty(topic.topic_difficulty) }}
                </el-tag>
              </div>
              <div class="topic-content">
                <p class="topic-question">{{ topic.topic_content }}</p>
                <div class="options">
                  <p v-if="topic.A" class="option"><span class="option-label">A.</span> {{ topic.A }}</p>
                  <p v-if="topic.B" class="option"><span class="option-label">B.</span> {{ topic.B }}</p>
                  <p v-if="topic.C" class="option"><span class="option-label">C.</span> {{ topic.C }}</p>
                  <p v-if="topic.D" class="option"><span class="option-label">D.</span> {{ topic.D }}</p>
                  <p v-if="topic.E" class="option"><span class="option-label">E.</span> {{ topic.E }}</p>
                </div>
              </div>
            </el-card>
          </div>
          <div v-else class="empty-topics">
            <el-empty description="暂无题目" />
            <p v-if="loadingTopics" class="loading-text">正在加载题目...</p>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false" class="close-btn">
            关闭
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { examAPI } from '@/api1/exam.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check, Refresh, Clock, Promotion, Delete, View, Edit,
  Star, Collection
} from '@element-plus/icons-vue'

// 数据状态
const loading = ref(true)
const exams = ref([])
const subjects = ref([])
const activeTab = ref('create')
const detailDialogVisible = ref(false)
const selectedExam = ref(null)
const examTopics = ref([])
const loadingTopics = ref(false)
const subjectConfig = ref(null)
const manualTopics = reactive({
  choice: [],
  multiple_choice: [],
  case_analysis: [],
  calculation_analysis: [],
  comprehensive: []
})

// 获取当前用户ID和角色（从localStorage或其他状态管理中获取）
const currentUserId = localStorage.getItem('userId') || 1
const currentUserRole = 'admin'

// 计算属性：判断是否有手动选题表单需要显示
const hasManualTopics = computed(() => {
  if (!subjectConfig.value) return false
  return (
    (subjectConfig.value.choice_count || 0) > 0 ||
    (subjectConfig.value.multiple_choice_count || 0) > 0 ||
    (subjectConfig.value.case_analysis_count || 0) > 0 ||
    (subjectConfig.value.calculation_analysis_count || 0) > 0 ||
    (subjectConfig.value.comprehensive_count || 0) > 0
  )
})

// 表单数据
const examForm = reactive({
  id: null,
  exam_name: '',
  subject_id: '',
  created_person_id: currentUserId, // 使用当前用户ID
  passing_score: 60,
  duration: 120,
  begin_time: '',
  end_time: '',
  draw_rule: 'random',
  all_score: 100,
  status: false,
  difficulty: '中等',
  difficulty_distribution: {
    easy: 5,
    medium: 10,
    hard: 5
  },
  knowledge_points: ''
})

// 表单验证规则
const examRules = {
  exam_name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  subject_id: [{ required: true, message: '请选择科目', trigger: 'change' }],
  passing_score: [{ required: true, message: '请输入及格线', trigger: 'blur' }],
  duration: [{ required: true, message: '请输入考试时长', trigger: 'blur' }],
  begin_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

// 表单引用
const examFormRef = ref(null)

// 检查是否有权限管理考试
const canManageExam = (exam) => {
  if (currentUserRole === 'admin') return true
  // 教师只能管理自己创建的考试
  if (currentUserRole === 'teacher') {
    return exam.created_person_id === parseInt(currentUserId)
  }
  return false
}

// 获取考试列表（教师只能看到自己创建的考试）
const fetchExams = async () => {
  loading.value = true
  try {
    const response = await examAPI.getPublishedExams()
    if (response.status === 'success') {
      // 根据用户角色过滤考试列表
      if (currentUserRole === 'teacher') {
        // 教师只显示自己创建的考试
        exams.value = response.exams
      } else if (currentUserRole === 'admin') {
        // 管理员显示所有考试
        exams.value = response.exams
      } else {
        // 学生显示所有已发布的考试
        exams.value = response.exams.filter(exam => exam.status === true)
      }
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    ElMessage.error('获取考试列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取科目列表
const fetchSubjects = async () => {
  try {
    const response = await examAPI.getSubjects()
    subjects.value = response.data.subjects
  } catch (error) {
    ElMessage.error('获取科目列表失败: ' + error.message)
  }
}

// 监听科目选择变化，加载科目配置
const handleSubjectChange = async (subjectId) => {
  if (!subjectId || examForm.draw_rule !== 'manual') return
  
  try {
    const response = await examAPI.getSubjectDetail(subjectId)
    if (response.data && response.data.status === 'success') {
      subjectConfig.value = response.data.data
      // 初始化手动选题表单
      initManualTopics()
      console.log('科目配置加载成功:', subjectConfig.value)
    } else {
      ElMessage.error('获取科目配置失败: ' + (response.data?.message || '未知错误'))
    }
  } catch (error) {
    console.error('获取科目配置错误:', error)
    ElMessage.error('获取科目配置失败: ' + error.message)
  }
}

// 初始化手动选题表单
const initManualTopics = () => {
  if (!subjectConfig.value) return
  
  const config = subjectConfig.value
  
  // 初始化选择题
  manualTopics.choice = Array(config.choice_count || 0).fill(null).map(() => ({
    topic_content: '',
    A: '',
    B: '',
    C: '',
    D: '',
    topic_answer: '',
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.choice_score || 0,
    topic_type: '单项选择题'
  }))
  
  // 初始化多选题
  manualTopics.multiple_choice = Array(config.multiple_choice_count || 0).fill(null).map(() => ({
    topic_content: '',
    A: '',
    B: '',
    C: '',
    D: '',
    topic_answer: [],
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.multiple_choice_score || 0,
    topic_type: '多项选择题'
  }))
  
  // 初始化判断题
  manualTopics.judgment = Array(config.judgment_count || 0).fill(null).map(() => ({
    topic_content: '',
    topic_answer: '',
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.judgment_score || 0,
    topic_type: '判断题'
  }))
  
  // 初始化案例分析题
  manualTopics.case_analysis = Array(config.case_analysis_count || 0).fill(null).map(() => ({
    topic_content: '',
    topic_answer: '',
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.case_analysis_score || 0,
    topic_type: '案例分析题'
  }))
  
  // 初始化计算分析题
  manualTopics.calculation_analysis = Array(config.calculation_analysis_count || 0).fill(null).map(() => ({
    topic_content: '',
    topic_answer: '',
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.calculation_analysis_score || 0,
    topic_type: '计算分析题'
  }))
  
  // 初始化综合题
  manualTopics.comprehensive = Array(config.comprehensive_count || 0).fill(null).map(() => ({
    topic_content: '',
    topic_answer: '',
    topic_difficulty: 'medium',
    topic_knowledge: '',
    topic_analysis: '',
    score: config.comprehensive_score || 0,
    topic_type: '综合题'
  }))
}

// 提交表单
const submitForm = () => {
  examFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        let response
        // 设置创建人ID为当前用户
        examForm.created_person_id = localStorage.getItem('userId')

        const formData = {
          ...examForm,
          begin_time: examForm.begin_time instanceof Date ? examForm.begin_time.toISOString() : examForm.begin_time,
          end_time: examForm.end_time instanceof Date ? examForm.end_time.toISOString() : examForm.end_time,
          difficulty_distribution: examForm.draw_rule === 'random'
            ? examForm.difficulty_distribution
            : undefined,
          // 手动选题时，传递题目数据
          manual_topics: examForm.draw_rule === 'manual' ? prepareManualTopics() : undefined
        }

        if (examForm.id) {
          // 更新考试（检查权限）
          if (!canManageExam({ created_person_id: examForm.created_person_id })) {
            ElMessage.error('无权限编辑该考试')
            return
          }
          response = await examAPI.updateExam(examForm.id, formData)
        } else {
          // 创建考试
          response = await examAPI.createExam(formData)
        }
        console.log(response)
        if (response.data .status === 'success') {
          ElMessage.success(examForm.id ? '考试更新成功' : '考试创建成功')
          resetForm()
          await fetchExams() // 刷新列表
          activeTab.value = 'list' // 切换到考试列表Tab
        } else {
        ElMessage.error(response.data.message)
        }
      } catch (error) {
        ElMessage.error((examForm.id ? '更新' : '创建') + '考试失败: ' + error.message)
      }
    }
  })
}

// 准备手动选题数据
const prepareManualTopics = () => {
  const allTopics = [
    ...manualTopics.choice,
    ...manualTopics.multiple_choice,
    ...manualTopics.judgment,
    ...manualTopics.case_analysis,
    ...manualTopics.calculation_analysis,
    ...manualTopics.comprehensive
  ]
  
  // 过滤掉空题目（题干为空的）
  const validTopics = allTopics.filter(topic => topic.topic_content && topic.topic_content.trim())
  
  // 处理多选题答案（数组转字符串）
  return validTopics.map(topic => ({
    ...topic,
    topic_answer: Array.isArray(topic.topic_answer) ? topic.topic_answer.join(',') : topic.topic_answer
  }))
}

// 重置表单
const resetForm = () => {
  examFormRef.value?.resetFields()
  examForm.id = null
  examForm.exam_name = ''
  examForm.subject_id = ''
  examForm.created_person_id = currentUserId
  examForm.passing_score = 60
  examForm.duration = 120
  examForm.begin_time = ''
  examForm.end_time = ''
  examForm.draw_rule = 'random'
  examForm.all_score = 100
  examForm.status = false
  examForm.difficulty = '中等'
  examForm.difficulty_distribution = {
    easy: 5,
    medium: 10,
    hard: 5
  }
  examForm.knowledge_points = ''
  // 重置手动选题相关数据
  subjectConfig.value = null
  manualTopics.choice = []
  manualTopics.multiple_choice = []
  manualTopics.judgment = []
  manualTopics.case_analysis = []
  manualTopics.calculation_analysis = []
  manualTopics.comprehensive = []
}

// 编辑考试
const editExam = (exam) => {
  // 检查是否有权限编辑该考试
  if (!canManageExam(exam)) {
    ElMessage.error('无权限编辑该考试')
    return
  }

  activeTab.value = 'create'
  examForm.id = exam.id
  examForm.exam_name = exam.name
  examForm.subject_id = exam.subject_id || ''
  examForm.created_person_id = exam.created_person_id
  examForm.passing_score = exam.settings?.passing_score || 60
  examForm.duration = exam.settings?.duration || 120
  examForm.begin_time = new Date(exam.begin_time)
  examForm.end_time = new Date(exam.end_time)
  examForm.draw_rule = exam.settings?.draw_rule || 'random'
  examForm.all_score = exam.all_score
  examForm.status = exam.status
  examForm.difficulty = exam.difficulty || '中等'

  // 处理难度分布
  if (exam.settings?.difficulty_distribution) {
    examForm.difficulty_distribution = { ...exam.settings.difficulty_distribution }
  } else {
    examForm.difficulty_distribution = {
      easy: 5,
      medium: 10,
      hard: 5
    }
  }
}

// 删除考试
const deleteExam = (exam) => {
  // 检查是否有权限删除该考试
  if (!canManageExam(exam)) {
    ElMessage.error('无权限删除该考试')
    return
  }

  ElMessageBox.confirm('确定要删除该考试吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    center: true,
    lockScroll: true,
    draggable: true,
    closeOnClickModal: false,
    customClass: 'beautiful-confirm-dialog',
    iconClass: 'el-icon-warning'
  }).then(async () => {
    try {
      const response = await examAPI.deleteExam(exam.id)
      if (response.data.status === 'success') {
        ElMessage.success('删除成功')
        // 添加延迟确保删除成功后再刷新
        setTimeout(async () => {
          await fetchExams()
        }, 1000)
      } else {
        ElMessage.error(response.data.message)
        // 即使删除失败也尝试刷新列表
        await fetchExams()
      }
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
      // 异常情况下也尝试刷新列表
      await fetchExams()
    }
  })
}
import { useRouter } from 'vue-router';
const router1 = useRouter();
const jupe = async () => {
  await router1.push('/main')
}
// 发布考试
const publishExam = async (exam) => {
  // 检查是否有权限发布该考试
  if (!canManageExam(exam)) {
    ElMessage.error('无权限发布该考试')
    return
  }

  try {
    const response = await examAPI.publishExam({ exam_paper_id: exam.id })
    if (response.data.status === 'success') {
      ElMessage.success('发布成功')
      await fetchExams()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('发布失败: ' + error.message)
  }
}

// 显示详情
const showDetail = async (exam) => {
  // 检查是否有权限查看该考试详情
  if (currentUserRole !== 'student' && !canManageExam(exam)) {
    ElMessage.error('无权限查看该考试详情')
    return
  }

  // 添加检查确保exam.id存在
  if (!exam || !exam.id) {
    ElMessage.error('考试信息不完整')
    return
  }

  selectedExam.value = exam
  detailDialogVisible.value = true
  examTopics.value = []
  loadingTopics.value = true

  try {
    const response = await examAPI.getExamTopics(exam.id)
    if (response.data.status === 'success') {
      examTopics.value = response.data.topics
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('获取题目失败: ' + error.message)
  } finally {
    loadingTopics.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 格式化难度
const formatDifficulty = (difficulty) => {
  const map = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return map[difficulty] || difficulty
}

// 获取难度类型
const getDifficultyType = (difficulty) => {
  const map = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return map[difficulty] || 'info'
}

// 组件挂载时获取数据
onMounted(() => {

  fetchExams()
  fetchSubjects()
})
</script>

<style scoped>
/* 全局容器样式 */
.exam-management-container {
  padding: 20px;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
  box-sizing: border-box;
}

/* 页面标题区域 */
.page-header {
  margin-bottom: 24px;
  text-align: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 标签页样式 */
.management-tabs {
  width: 100%;
  margin-bottom: 20px;
}

.management-tabs :deep(.el-tabs__header) {
  background: white;
  border-radius: 8px;
  padding: 0 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.management-tabs :deep(.el-tabs__item) {
  padding: 0 20px;
  font-size: 14px;
  color: #6b7280;
  height: 48px;
  line-height: 48px;
  font-weight: 500;
}

.management-tabs :deep(.el-tabs__item.is-active) {
  color: #3b82f6;
  font-weight: 600;
}

.management-tabs :deep(.el-tabs__active-bar) {
  height: 2px;
  background: #3b82f6;
}

/* 标签内容区域 */
.tab-content {
  background: transparent;
  width: 100%;
}

/* 表单卡片样式 */
.form-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.form-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.form-actions {
  display: flex;
  gap: 12px;
}

/* 表单样式 */
.exam-form {
  padding: 24px;
  width: 100%;
  box-sizing: border-box;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f3f4f6;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #3b82f6;
}

.subsection-title {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 16px;
}

/* 表单网格布局 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  width: 100%;
}

.distribution-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  width: 100%;
}

/* 表单项目样式 */
.form-item {
  margin-bottom: 0;
  width: 100%;
}

.form-item :deep(.el-form-item__label) {
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
}

.full-width {
  grid-column: 1 / -1;
}

/* 表单元素样式 */
.form-input {
  width: 100%;
}

.form-input :deep(.el-input__inner) {
  border-radius: 6px;
  border: 1px solid #d1d5db;
  transition: all 0.2s ease;
  height: 36px;
  line-height: 36px;
}

.form-input :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-select {
  width: 100%;
}

.form-select :deep(.el-select .el-input__inner) {
  border-radius: 6px;
  border: 1px solid #d1d5db;
  transition: all 0.2s ease;
  height: 36px;
  line-height: 36px;
}

.form-select :deep(.el-select .el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.form-date-picker {
  width: 100%;
}

.form-date-picker :deep(.el-input__inner) {
  border-radius: 6px;
  border: 1px solid #d1d5db;
  transition: all 0.2s ease;
  height: 36px;
  line-height: 36px;
}

.form-date-picker :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 分布配置区域 */
.distribution-section {
  background: #f8fafc;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  margin-top: 12px;
}

/* 按钮样式 */
.submit-btn {
  background: #10b981;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.submit-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.reset-btn {
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.reset-btn:hover {
  background-color: #3b82f6;
  color: white;
  transform: translateY(-1px);
}

/* 列表样式 */
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.list-actions {
  display: flex;
  gap: 12px;
}

.refresh-btn {
  background: #3b82f6;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.list-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 表格样式 */
.exam-table {
  border-radius: 8px;
  overflow: hidden;
}

.exam-table :deep(.el-table__header-wrapper) {
  background: #f8fafc;
}

.exam-table :deep(.el-table__header th) {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
  padding: 12px 8px;
}

.exam-table :deep(.el-table__row) {
  height: 52px;
}

.exam-table :deep(.el-table__row:hover) {
  background-color: #f3f4f6;
}

.exam-table :deep(.el-table__cell) {
  padding: 12px 8px;
  color: #4b5563;
  font-size: 14px;
  border-bottom: 1px solid #f3f4f6;
}

/* 特殊单元格样式 */
.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-icon {
  color: #6b7280;
  font-size: 14px;
}

.score-value {
  font-weight: 600;
  color: #3b82f6;
  font-size: 14px;
}

/* 状态标签样式 */
.status-tag {
  border: none;
  border-radius: 12px;
  padding: 4px 8px;
  font-weight: 500;
  font-size: 12px;
}

.status-published {
  background: #d1fae5;
  color: #065f46;
}

.status-draft {
  background: #fef3c7;
  color: #92400e;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

.edit-btn {
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background-color: #3b82f6;
  color: white;
}

.publish-btn {
  background: #10b981;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.publish-btn:hover:not(:disabled) {
  background: #059669;
}

.publish-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.delete-btn {
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.delete-btn:hover:not(:disabled) {
  background-color: #ef4444;
  color: white;
}

.delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.detail-btn {
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  transition: all 0.2s ease;
}

.detail-btn:hover {
  background-color: #8b5cf6;
  color: white;
}

/* 详情弹窗样式 */
.detail-dialog :deep(.el-dialog) {
  border-radius: 8px;
  overflow: hidden;
  max-width: 90%;
}

.detail-dialog :deep(.el-dialog__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #f8fafc;
}

.detail-dialog :deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.detail-dialog :deep(.el-dialog__body) {
  padding: 0;
  max-height: 70vh;
  overflow-y: auto;
}

.detail-content {
  padding: 0;
}

/* 考试信息卡片 */
.exam-info-card {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #f3f4f6;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.info-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.score-highlight {
  color: #3b82f6;
  font-weight: 600;
}

/* 题目区域 */
.topics-section {
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f3f4f6;
}

.topics-container {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.topics-container::-webkit-scrollbar {
  width: 4px;
}

.topics-container::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.topics-container::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.topics-container::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.topic-card {
  margin-bottom: 12px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.topic-number {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.difficulty-tag {
  border: none;
  border-radius: 10px;
  padding: 2px 6px;
  font-weight: 500;
  font-size: 10px;
}

.difficulty-easy {
  background: #d1fae5;
  color: #065f46;
}

.difficulty-medium {
  background: #fef3c7;
  color: #92400e;
}

.difficulty-hard {
  background: #fee2e2;
  color: #991b1b;
}

.topic-content {
  padding: 12px;
}

.topic-question {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.5;
  margin-bottom: 8px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option {
  margin: 0;
  padding: 6px 8px;
  background: #f8fafc;
  border-radius: 4px;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.4;
}

.option-label {
  font-weight: 600;
  color: #3b82f6;
  margin-right: 6px;
}

.empty-topics {
  padding: 30px 0;
  text-align: center;
}

.loading-text {
  color: #6b7280;
  margin-top: 12px;
  font-size: 14px;
}

/* 手动选题样式 */
.manual-topics-container {
  margin-top: 20px;
}

.topic-type-section {
  margin-bottom: 30px;
}

.topic-type-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #3b82f6;
}

.topic-form-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.topic-form-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.topic-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f3f4f6;
}

.topic-index {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.topic-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.topic-form :deep(.el-textarea__inner) {
  resize: vertical;
}

.empty-tip {
  padding: 40px 0;
  text-align: center;
}

/* 关闭按钮 */
.close-btn {
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #3b82f6;
  color: white;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .exam-management-container {
    padding: 16px 12px;
  }

  .page-title {
    font-size: 24px;
  }

  .form-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .management-tabs :deep(.el-tabs__item) {
    padding: 0 12px;
    font-size: 13px;
  }

  .exam-form {
    padding: 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .distribution-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }

  .action-buttons .el-button {
    width: 100%;
    justify-content: center;
  }

  .detail-dialog {
    width: 95% !important;
  }
}

@media (max-width: 480px) {
  .exam-management-container {
    padding: 12px 8px;
  }

  .page-title {
    font-size: 20px;
  }

  .management-tabs :deep(.el-tabs__item) {
    padding: 0 8px;
    font-size: 12px;
  }

  .form-header {
    padding: 16px;
  }

  .exam-form {
    padding: 12px;
  }

  .submit-btn, .reset-btn, .refresh-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 左右分布 */
  margin-bottom: 24px;
}

/* 让标题组在视觉上“居中” —— 实际是靠左，但通过 margin-left: auto 实现居中效果 */
.title-wrapper {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  flex: 0 0 auto; /* 不伸缩，宽度由内容决定 */
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 4px 0 0;
}

.back-home-btn {
  flex: 0 0 auto;
}


</style>
