<template>
  <div class="exam-paper-container" v-if="examStarted">
    <!-- 考试头部信息 -->
    <el-card class="exam-header-card" shadow="hover">
      <div class="exam-header">
        <h2 class="exam-title">{{ examName }}</h2>
        <div class="exam-info-items">
          <el-tag type="danger" class="timer-tag">
            <el-icon class="timer-icon"><Clock /></el-icon>
            {{ remainingTime }}
          </el-tag>
          <el-tag type="info">
            题目: {{ currentQuestion + 1 }}/{{ topics.length }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <div class="main-content">
      <!-- 题目列表区域 -->
      <div class="question-list-container">
        <div class="section-header">
          <h3>题目列表</h3>
        </div>
        <el-scrollbar class="question-list-scroll">
          <!-- 按题型分组显示题目 -->
          <div
            v-for="group in availableQuestionTypes"
            :key="group.type"
            class="question-type-group"
          >
            <h4 class="question-type-title">
              <el-tag
                :type="getQuestionTypeTagType(group.type)"
                size="small"
              >
                {{ group.type }}
              </el-tag>
              <span class="question-count">({{ group.items.length }}题)</span>
            </h4>
            <div class="question-grid">
              <div
                v-for="(topic, idx) in group.items"
                :key="topic.topic_number"
                class="question-grid-item"
                :class="{
                  'active': currentQuestion === topic.originalIndex,
                  'answered': answers[topic.topic_number],
                  'marked': isMarked(topic.topic_number),
                  'choice-question': isChoiceQuestion(topic),
                  'subjective-question': isSubjectiveQuestion(topic),
                  'disabled': examSubmitted
                }"
                @click="!examSubmitted ? setCurrentQuestion(topic.originalIndex) : null"
              >
                <span class="question-index">{{ topic.originalIndex + 1 }}</span>
                <el-icon v-if="isMarked(topic.topic_number)" class="mark-icon"><Star /></el-icon>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>

      <!-- 题目内容区域 -->
      <div class="question-content-container">
        <div class="section-header">
          <h3>题目详情</h3>
          <el-tag
            v-if="currentTopic"
            :type="getDifficultyType(currentTopic.topic_difficulty)"
            class="difficulty-tag"
          >
            {{ formatDifficulty(currentTopic.topic_difficulty) }}
          </el-tag>
        </div>

        <el-card class="question-card" shadow="hover">
          <div class="question-detail" v-if="currentTopic">
            <div class="question-main">
              <h4 class="question-title">
                第 {{ currentQuestion + 1 }} 题
                <el-tag
                  v-if="currentTopic.topic_type"
                  :type="getQuestionTypeTagType(currentTopic.topic_type)"
                  size="small"
                  class="question-type-tag-in-content"
                >
                  {{ currentTopic.topic_type }}
                </el-tag>
              </h4>
              <p class="question-text">{{ currentTopic.topic_content }}</p>

              <!-- 题目附件（如果有） -->
              <div v-if="currentTopic.attachment_url" class="attachment-section">
                <el-link :href="currentTopic.attachment_url" target="_blank" type="primary">
                  <el-icon><Paperclip /></el-icon>
                  下载附件
                </el-link>
              </div>
            </div>

            <!-- 选择题选项区域 -->
            <div class="options-section" v-if="isChoiceQuestion(currentTopic)">
              <div class="section-title">选项</div>
              
              <!-- 判断题 -->
              <div v-if="isJudgmentQuestion(currentTopic)" class="judgment-section">
                <el-radio-group
                  v-model="answers[currentTopic.topic_number]"
                  @change="!examSubmitted ? saveAnswer() : null"
                  class="options-group judgment-group"
                  :disabled="examSubmitted"
                >
                  <el-radio
                    label="对"
                    class="option-item-radio judgment-option"
                    :class="{'selected': answers[currentTopic.topic_number] === '对'}"
                    :disabled="examSubmitted"
                  >
                    <span class="option-key">✓</span>
                    <span class="option-content">对</span>
                  </el-radio>
                  <el-radio
                    label="错"
                    class="option-item-radio judgment-option"
                    :class="{'selected': answers[currentTopic.topic_number] === '错'}"
                    :disabled="examSubmitted"
                  >
                    <span class="option-key">✗</span>
                    <span class="option-content">错</span>
                  </el-radio>
                </el-radio-group>
              </div>
              
              <!-- 多项选择题 -->
              <div v-else-if="isMultipleChoice(currentTopic)" class="multiple-choice-section">
                <!-- 多项选择题 -->
                <el-checkbox-group
                  v-model="answers[currentTopic.topic_number]"
                  @change="!examSubmitted ? saveAnswer() : null"
                  class="options-group"
                  :disabled="examSubmitted"
                >
                  <el-checkbox
                    v-for="(option, key) in getOptions(currentTopic)"
                    :key="key"
                    :label="key"
                    class="option-item-checkbox"
                    :class="{'selected': isSelected(currentTopic.topic_number, key)}"
                    :disabled="examSubmitted"
                  >
                    <span class="option-key">{{ key }}.</span>
                    <span class="option-content">{{ option }}</span>
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              <div v-else class="single-choice-section">
                <!-- 单项选择题 -->
                <el-radio-group
                  v-model="answers[currentTopic.topic_number]"
                  @change="!examSubmitted ? saveAnswer() : null"
                  class="options-group"
                  :disabled="examSubmitted"
                >
                  <el-radio
                    v-for="(option, key) in getOptions(currentTopic)"
                    :key="key"
                    :label="key"
                    class="option-item-radio"
                    :class="{'selected': isSelected(currentTopic.topic_number, key)}"
                    :disabled="examSubmitted"
                  >
                    <span class="option-key">{{ key }}.</span>
                    <span class="option-content">{{ option }}</span>
                  </el-radio>
                </el-radio-group>
              </div>
            </div>

            <!-- 主观题输入区域 -->
            <div class="subjective-section" v-else-if="isSubjectiveQuestion(currentTopic)">
              <div class="section-title">答题区域</div>
              <div class="subjective-answer-area">
                <!-- 案例分析题 -->
                <div v-if="currentTopic.topic_type === '案例分析题'" class="case-analysis-format">
                  <div class="textarea-container">
                    <el-input
                      v-model="answers[currentTopic.topic_number]"
                      type="textarea"
                      :rows="8"
                      :autosize="{ minRows: 6, maxRows: 15 }"
                      placeholder="请在此输入案例分析的答案..."
                      @input="!examSubmitted ? debounceSaveAnswer() : null"
                      class="answer-textarea"
                      :disabled="examSubmitted"
                    />
                  </div>
                  <div class="analysis-tips">
                    <p><strong>答题提示：</strong></p>
                    <ul>
                      <li>请根据案例材料进行分析</li>
                      <li>分点论述，条理清晰</li>
                      <li>结合理论知识进行阐述</li>
                    </ul>
                  </div>
                </div>

                <!-- 计算分析题 -->
                <div v-else-if="currentTopic.topic_type === '计算分析题'" class="calculation-format">
                  <div class="textarea-container">
                    <el-input
                      v-model="answers[currentTopic.topic_number]"
                      type="textarea"
                      :rows="6"
                      :autosize="{ minRows: 5, maxRows: 12 }"
                      placeholder="请在此输入计算过程和答案..."
                      @input="!examSubmitted ? debounceSaveAnswer() : null"
                      class="answer-textarea"
                      :disabled="examSubmitted"
                    />
                  </div>
                  <div class="calculation-tips">
                    <p><strong>答题提示：</strong></p>
                    <ul>
                      <li>请写出详细的计算步骤</li>
                      <li>保留必要的计算公式</li>
                      <li>标注计算单位</li>
                    </ul>
                  </div>
                </div>

                <!-- 综合题 -->
                <div v-else-if="currentTopic.topic_type === '综合题'" class="comprehensive-format">
                  <div class="textarea-container">
                    <el-input
                      v-model="answers[currentTopic.topic_number]"
                      type="textarea"
                      :rows="10"
                      :autosize="{ minRows: 8, maxRows: 20 }"
                      placeholder="请在此输入综合性问题的答案..."
                      @input="!examSubmitted ? debounceSaveAnswer() : null"
                      class="answer-textarea"
                      :disabled="examSubmitted"
                    />
                  </div>
                  <div class="comprehensive-tips">
                    <p><strong>答题提示：</strong></p>
                    <ul>
                      <li>全面考虑问题各个层面</li>
                      <li>理论联系实际</li>
                      <li>逻辑清晰，论证充分</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="no-question" v-else>
            <el-icon class="empty-icon"><Document /></el-icon>
            <p>请选择题目</p>
          </div>
        </el-card>

        <!-- 操作按钮区域 -->
        <div class="question-actions">
          <el-button
            @click="!examSubmitted ? markQuestion() : null"
            :type="isMarked(currentTopic?.topic_number) ? 'warning' : 'default'"
            class="action-btn mark-btn"
            :disabled="examSubmitted"
          >
            <el-icon><Star /></el-icon>
            {{ isMarked(currentTopic?.topic_number) ? '取消标记' : '标记题目' }}
          </el-button>
        </div>
      </div>

      <!-- 答题状态区域 -->
      <div class="status-container">
        <div class="section-header">
          <h3>答题状态</h3>
        </div>
        <el-card class="status-card" shadow="hover">
          <div class="status-stats">
            <div class="stat-item">
              <div class="stat-value">{{ topics.length }}</div>
              <div class="stat-label">总题数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value answered">{{ answeredCount }}</div>
              <div class="stat-label">已答</div>
            </div>
            <div class="stat-item">
              <div class="stat-value marked">{{ markedQuestions.size }}</div>
              <div class="stat-label">标记</div>
            </div>
            <div class="stat-item">
              <div class="stat-value unanswered">{{ unansweredCount }}</div>
              <div class="stat-label">未答</div>
            </div>
          </div>

          <!-- 按题型统计 -->
          <div class="type-stats">
            <div class="stat-item" v-for="(count, type) in questionTypeCounts" :key="type">
              <div class="stat-value" :class="type.replace(' ', '-').replace('_', '-')">{{ count }}</div>
              <div class="stat-label">{{ type }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 导航和交卷区域 -->
    <el-card class="exam-footer-card" shadow="hover">
      <div class="navigation">
        <el-button
          @click="prevQuestion"
          :disabled="currentQuestion <= 0 || examSubmitted"
          class="nav-btn"
        >
          <el-icon><ArrowLeft /></el-icon>
          上一题
        </el-button>

        <!-- 显示当前题目页码信息 -->
        <div class="question-page-info">
          <span class="page-text">第 {{ currentQuestion + 1 }} / {{ topics.length }} 题</span>
        </div>

        <el-button
          @click="nextQuestion"
          :disabled="currentQuestion >= topics.length - 1 || examSubmitted"
          class="nav-btn"
        >
          下一题
          <el-icon><ArrowRight /></el-icon>
        </el-button>

        <el-button
          type="danger"
          @click="submitExam"
          class="submit-btn"
          :disabled="examSubmitted"
        >
          <el-icon><Upload /></el-icon>
          交卷
        </el-button>
      </div>
    </el-card>
  </div>

  <!-- 考试开始界面 -->
  <div class="exam-start-container" v-else>
    <el-card class="start-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><EditPen /></el-icon>
          <span>开始考试</span>
        </div>
      </template>

      <el-form
        :model="startForm"
        :rules="startRules"
        ref="startFormRef"
        label-width="100px"
        class="start-form"
      >
        <el-form-item label="考试ID" prop="exam_paper_id">
          <el-input
            v-model.number="startForm.exam_paper_id"
            type="number"
            placeholder="请输入考试ID"
            clearable
            :disabled="examStarted"
          >
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="用户ID" prop="user_id">
          <el-input
            v-model.number="startForm.user_id"
            type="number"
            placeholder="请输入用户ID"
            disabled
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="startExam"
            class="start-btn"
            size="large"
            :disabled="examStarted"
          >
            <el-icon><VideoPlay /></el-icon>
            开始考试
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { examAPI } from '@/api1/exam.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock, Star, Document, ArrowLeft, ArrowRight,
  Upload, EditPen, User, VideoPlay, Paperclip
} from '@element-plus/icons-vue'

// 路由
const route = useRoute()
const router = useRouter()

// 表单引用
const startFormRef = ref(null)

// 考试状态
const examStarted = ref(false)
const examName = ref('')
const type1 = ref('')
const participationId = ref(null)
const examSubmitted = ref(false) // 新增：考试是否已提交
const examStartTime = ref(null) // 新增：考试开始时间

// 考试数据
const topics = ref([])
const answers = reactive({})
const markedQuestions = reactive(new Set())
const currentQuestion = ref(0)

// 定时器
const timer = ref(null)
const endTime = ref(null)
const timeLeft = ref('00:00')

// 倒计时显示
const remainingTime = computed(() => timeLeft.value)

// 开始表单
const startForm = reactive({
  exam_paper_id: '',
  user_id: localStorage.getItem('userId')
})

// 表单验证规则
const startRules = {
  exam_paper_id: [
    { required: true, message: '请输入考试ID', trigger: 'blur' }
  ],
  user_id: [
    { required: true, message: '请输入用户ID', trigger: 'blur' }
  ]
}

// 当前题目
const currentTopic = computed(() => {
  if (topics.value.length > 0 && currentQuestion.value < topics.value.length) {
    const topic = topics.value[currentQuestion.value]
    return topic
  }
  return null
})

// 计算属性：按题型分组的题目
const groupedTopics = computed(() => {
  const groups = {}

  topics.value.forEach((topic, index) => {
    const type = topic.topic_type
    if (!groups[type]) {
      groups[type] = []
    }
    groups[type].push({...topic, originalIndex: index})
  })

  return groups
})

// 计算属性：只显示有题目的题型（按固定顺序排列）
const availableQuestionTypes = computed(() => {
  // 定义题型顺序
  const questionTypeOrder = [
    '单项选择题',
    '多项选择题',
    '判断题',
    '案例分析题',
    '计算分析题',
    '综合题'
  ]
  
  // 按顺序过滤并返回题型，每个题型内按题号排序
  return questionTypeOrder
    .filter(type => groupedTopics.value[type] && groupedTopics.value[type].length > 0)
    .map(type => ({ 
      type, 
      items: [...groupedTopics.value[type]].sort((a, b) => a.topic_number - b.topic_number) 
    }))
})

// 计算属性：已答题目数量
const answeredCount = computed(() => {
  return Object.keys(answers).filter(key => answers[key]).length
})

// 计算属性：未答题目数量
const unansweredCount = computed(() => {
  return topics.value.length - answeredCount.value
})

// 计算属性：各题型数量统计
const questionTypeCounts = computed(() => {
  const counts = {}
  topics.value.forEach(topic => {
    const type = topic.topic_type
    counts[type] = (counts[type] || 0) + 1
  })
  return counts
})

// 题型判断方法 - 直接使用后端返回的字符串
const isChoiceQuestion = (topic) => {
  return ['单项选择题', '多项选择题', '判断题'].includes(topic.topic_type)
}

const isSubjectiveQuestion = (topic) => {
  return ['案例分析题', '计算分析题', '综合题'].includes(topic.topic_type)
}

const isMultipleChoice = (topic) => {
  return topic.topic_type === '多项选择题'
}

const isSingleChoice = (topic) => {
  return topic.topic_type === '单项选择题'
}

const isJudgmentQuestion = (topic) => {
  return topic.topic_type === '判断题'
}

// 检查选项是否被选中（用于多选题）
const isSelected = (topicNumber, optionKey) => {
  if (!answers[topicNumber]) return false
  if (isMultipleChoice(currentTopic.value)) {
    return Array.isArray(answers[topicNumber]) && answers[topicNumber].includes(optionKey)
  }
  return answers[topicNumber] === optionKey
}

// 格式化难度显示
const formatDifficulty = (difficulty) => {
  const map = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return map[difficulty] || difficulty
}

// 获取难度标签类型
const getDifficultyType = (difficulty) => {
  const map = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return map[difficulty] || 'info'
}

// 获取题型标签类型
const getQuestionTypeTagType = (type) => {
  const types = {
    '单项选择题': 'info',
    '多项选择题': 'warning',
    '判断题': 'success',
    '案例分析题': 'danger',
    '计算分析题': 'success',
    '综合题': 'primary'
  }
  return types[type] || 'info'
}

// 获取题目选项
const getOptions = (topic) => {
  if (!topic) return {}

  const options = {}
  if (topic.A) options.A = topic.A
  if (topic.B) options.B = topic.B
  if (topic.C) options.C = topic.C
  if (topic.D) options.D = topic.D
  if (topic.E) options.E = topic.E
  if (topic.F) options.F = topic.F

  return options
}

// 组件挂载时从URL参数获取考试ID
onMounted(() => {
  // 从路由参数获取考试ID
  if (route.params.examPaperId) {
    startForm.exam_paper_id = parseInt(route.params.examPaperId)
  }

  // 从查询参数获取参与ID
  if (route.query.participationId) {
    participationId.value = parseInt(route.query.participationId)
    examStarted.value = true
    // 如果已经有参与ID，直接加载考试题目
    loadExamData()
  }
  // 从URL参数获取考试ID
  else if (route.query.exam_id) {
    startForm.exam_paper_id = parseInt(route.query.exam_id)
  }
  // 添加：检查是否有正在进行的考试
  else if (startForm.exam_paper_id) {
    checkExistingParticipation()
  }
})

const loadExamData = async () => {
  try {
    // 获取考试详情
    const examDetail = await examAPI.getExamDetail(startForm.exam_paper_id)
    if (examDetail.data && examDetail.data.status === 'success') {
      examName.value = `在线考试 - ${examDetail.data.exam.name || '未知考试'}`

      // 获取考试题目
      const topicsResponse = await examAPI.getExamTopics(startForm.exam_paper_id)
      if (topicsResponse.data && topicsResponse.data.status === 'success') {
        // 直接使用后端返回的题目数据，不需要转换
        if (topicsResponse.data.topics && Array.isArray(topicsResponse.data.topics)) {
          topics.value = topicsResponse.data.topics.map((topic, index) => ({
            ...topic,
            originalIndex: index
          }))

          // 默认选中第一题
          if (topicsResponse.data.topics.length > 0) {
            currentQuestion.value = 0
          }
        } else {
          topics.value = []
        }
      }

      // 设置结束时间
      const participationResponse = await examAPI.getUserExamParticipation(
        startForm.user_id,
        startForm.exam_paper_id
      )
      console.log('【调试】participationResponse:', participationResponse)
      
      // 修改：判断 data 里面的 status，且读取 participation 数据时需要加上 .data 层级
      if (participationResponse && participationResponse.data && participationResponse.data.status === 'success') {
        const participationData = participationResponse.data.participation
        console.log('【调试】participation data:', participationData)
        
        if (participationData.end_time) {
          endTime.value = new Date(participationData.end_time)
          console.log('【调试】loadExamData: 使用 participation.end_time', endTime.value)
          startTimer()
        } else if (participationData.start_time) {
          const startTime = new Date(participationData.start_time)
          const duration = examDetail.data.exam && examDetail.data.exam.settings ?
                          examDetail.data.exam.settings.duration : 0
          console.log('【调试】duration:', duration)
          endTime.value = new Date(startTime.getTime() + duration * 60000)
          console.log('【调试】loadExamData: 计算得到的 end_time', endTime.value)
          startTimer()
        }
      }

      // 设置考试开始时间（用于120分钟自动交卷）
      examStartTime.value = new Date()
      startAutoSubmitTimer()
    }
  } catch (error) {
    ElMessage.error('加载考试数据失败: ' + (error.message || '未知错误'))
  }
}

// 检查是否有正在进行的考试参与记录
const checkExistingParticipation = async () => {
  if (!startForm.exam_paper_id || !startForm.user_id) return

  try {
    const participationResponse = await examAPI.getUserExamParticipation(
      startForm.user_id,
      startForm.exam_paper_id
    )

    if (participationResponse.status === 'success') {
      const status = participationResponse.participation.status
      if (status === 'in_progress') {
        participationId.value = participationResponse.participation.id
        examStarted.value = true
        loadExamData()
      } else if (status === 'submitted' || status === 'graded') {
        examStarted.value = true
        examSubmitted.value = true // 已提交，设置为已交卷状态
      }
    }
  } catch (error) {
    // 忽略错误，继续正常的考试开始流程
    console.log('检查现有参与记录失败:', error.message)
  }
}

// 开始考试
const startExam = async () => {
  if (!startFormRef.value) return

  await startFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 先获取考试详情检查考试状态和时间
        const examDetail = await examAPI.getExamDetail(startForm.exam_paper_id)
        if (examDetail.data && examDetail.data.status !== 'success') {
          ElMessage.error('获取考试信息失败: ' + (examDetail.data.message || '未知错误'))
          return
        }

        const now = new Date()
        if (!examDetail.data || !examDetail.data.exam) {
          ElMessage.error('考试信息不完整')
          return
        }

        const beginTime = new Date(examDetail.data.exam.begin_time)
        const examEndTime = new Date(examDetail.data.exam.end_time)

        if (now < beginTime) {
          ElMessage.error('考试尚未开始')
          return
        }

        if (now > examEndTime) {
          ElMessage.error('考试已结束')
          return
        }

        // 检查用户是否已参加过该考试
        const participation = await examAPI.getUserExamParticipation(
          startForm.user_id,
          startForm.exam_paper_id
        )

        if (participation.data.status === 'success') {
          const status = participation.participation.status
          console.log('检查用户参与记录:', status)
          if (status === 'in_progress') {
            // 继续考试
            examStarted.value = true
            participationId.value = participation.participation.id
            loadExamData()
            return
          } else if (status === 'submitted' || status === 'graded') {
            ElMessage.error('您已完成该考试，无法再次参加')
            examStarted.value = true
            examSubmitted.value = true
            return
          }
        }

        // 开始考试
        const response = await examAPI.startExam(startForm)
        if (response.data.status === 'success') {
          examStarted.value = true
          participationId.value = response.participation_id

          if (response.topics && Array.isArray(response.topics)) {
            // 直接使用后端返回的题目数据，不进行转换
            topics.value = response.topics.map((topic, index) => ({
              ...topic,
              originalIndex: index
            }))
          } else {
            topics.value = []
          }

          examName.value = `在线考试 - ${examDetail.data.exam.name || '未知考试'}`

          // 默认选中第一题
          if (response.topics && Array.isArray(response.topics) && response.topics.length > 0) {
            currentQuestion.value = 0
          }

          if (response.data.end_time) {
            endTime.value = new Date(response.data.end_time)
            startTimer()
          }

          // 设置考试开始时间（用于120分钟自动交卷）
          examStartTime.value = new Date()
          startAutoSubmitTimer()

          ElMessage.success('考试开始')
        } else {
          ElMessage.error(response.data.message || '开始考试失败')
        }
      } catch (error) {
        ElMessage.error('开始考试失败: ' + (error.message || '未知错误'))
      }
    }
  })
}

// 启动计时器
const startTimer = () => {
  if (timer.value) {
    clearInterval(timer.value)
  }

  if (!endTime.value || !(endTime.value instanceof Date) || isNaN(endTime.value.getTime())) {
    console.error('无效的结束时间:', endTime.value)
    ElMessage.error('考试时间设置有误')
    return
  }

  updateTimeDisplay()

  timer.value = setInterval(() => {
    updateTimeDisplay()
  }, 1000)
}

// 更新时间显示
const updateTimeDisplay = () => {
  const now = new Date()
  const diff = endTime.value - now
  
  // 添加调试日志，在控制台查看具体时间差
  console.log('[Timer Debug] 当前时间:', now)
  console.log('[Timer Debug] 结束时间:', endTime.value)
  console.log('[Timer Debug] 剩余时间(毫秒):', diff) 

  if (diff <= 0) {
    clearInterval(timer.value)
    timeLeft.value = '00:00'
    autoSubmitExam()
  } else {
    const minutes = Math.floor(diff / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    timeLeft.value = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
}

// 自动交卷
const autoSubmitExam = () => {
  ElMessage.warning('考试时间已到，自动交卷')
  submitExam()
}

// 120分钟自动交卷定时器
let autoSubmitTimer = null

const startAutoSubmitTimer = () => {
  if (autoSubmitTimer) {
    clearInterval(autoSubmitTimer)
  }

  // 120分钟 = 120 * 60 * 1000 毫秒
  const AUTO_SUBMIT_DURATION = 120 * 60 * 1000

  autoSubmitTimer = setInterval(() => {
    if (examStartTime.value) {
      const now = new Date()
      const elapsed = now.getTime() - examStartTime.value.getTime()

      if (elapsed >= AUTO_SUBMIT_DURATION) {
        ElMessage.warning('考试已进行120分钟，自动交卷')
        clearInterval(autoSubmitTimer)
        submitExam()
      }
    }
  }, 1000)
}

// 修改 setCurrentQuestion 方法，在切换前保存当前题目
const setCurrentQuestion = (index) => {
  if (examSubmitted.value) return

  // 强制保存当前题目答案
  saveAnswer()

  currentQuestion.value = index
}

// 修改 prevQuestion 方法
const prevQuestion = () => {
  if (currentQuestion.value > 0 && !examSubmitted.value) {
    saveAnswer() // 切换前保存
    currentQuestion.value--
  }
}

// 修改 nextQuestion 方法
const nextQuestion = () => {
  if (currentQuestion.value < topics.value.length - 1 && !examSubmitted.value) {
    saveAnswer() // 切换前保存
    currentQuestion.value++
  }
}

// 防抖函数
const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    if (examSubmitted.value) return
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// 添加防抖功能
const debounceSaveAnswer = debounce(() => {
  saveAnswer()
}, 1000)

// 修改保存答案方法以支持多选题
const saveAnswer = async () => {
  if (!currentTopic.value || !participationId.value || examSubmitted.value) return

  try {
    // 对于多选题，确保答案是字符串形式（例如"A,C,D"）
    let answerValue = answers[currentTopic.value.topic_number]
    if (isMultipleChoice(currentTopic.value) && Array.isArray(answerValue)) {
      answerValue = answerValue.join(',')
    }

    // 如果多选题取消了所有选项（空数组或空字符串），删除该题答案记录
    const topicNumber = currentTopic.value.topic_number
    if (!answerValue || (Array.isArray(answerValue) && answerValue.length === 0)) {
      delete answers[topicNumber]
    }

    const response = await examAPI.saveProgress({
      participation_id: participationId.value,
      topic_id: topicNumber,
      answer: answerValue || '', // 空答案也保存
      is_marked: isMarked(topicNumber),
      type1: currentTopic.value.topic_type
    })

    if (response.data.status !== 'success') {
      console.error('保存答案失败:', response.data.message)
    }
  } catch (error) {
    console.error('保存答案失败:', error.message)
  }
}

// 标记题目
const markQuestion = () => {
  if (!currentTopic.value || examSubmitted.value) return

  const topicNumber = currentTopic.value.topic_number
  if (markedQuestions.has(topicNumber)) {
    markedQuestions.delete(topicNumber)
  } else {
    markedQuestions.add(topicNumber)
  }

  // 保存标记状态
  saveAnswer()
}

// 检查题目是否被标记
const isMarked = (topicNumber) => {
  return markedQuestions.has(topicNumber)
}

// 交卷
const submitExam = async () => {
  if (!participationId.value) {
    ElMessage.error('考试未开始')
    return
  }

  if (examSubmitted.value) {
    ElMessage.info('考试已提交，不能重复提交')
    return
  }

  try {
    await ElMessageBox.confirm('确定要交卷吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await examAPI.submitExam({
      participation_id: participationId.value
    })

    if (response.data.status === 'success') {
      // 停止计时器
      if (timer.value) {
        clearInterval(timer.value)
      }

      // 停止自动交卷定时器
      if (autoSubmitTimer) {
        clearInterval(autoSubmitTimer)
      }

      // 设置已交卷状态
      examSubmitted.value = true

      ElMessage.success('交卷成功')

      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        router.push('/take-exam')
      }, 1500)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('交卷失败: ' + error.message)
    }
  }
}

// 组件卸载前清理定时器
onBeforeUnmount(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }

  if (autoSubmitTimer) {
    clearInterval(autoSubmitTimer)
  }
})
</script>

<style scoped>
.exam-paper-container {
  padding: 20px;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.exam-header-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
}

.exam-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #303133;
}

.exam-info-items {
  display: flex;
  gap: 15px;
}

.timer-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
  font-size: 16px;
  padding: 8px 15px;
}

.timer-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  gap: 20px;
  margin-bottom: 80px; /* 添加底部边距，防止被底部导航栏遮挡 */
  min-height: 0; /* 重要：允许在flex布局中缩小 */
  overflow: hidden; /* 防止内容溢出 */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #606266;
}

.difficulty-tag {
  border-radius: 12px;
}

/* 题目列表区域 */
.question-list-container {
  display: flex;
  flex-direction: column;
}

.question-list-scroll {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow-y: auto; /* 启用垂直滚动 */
  max-height: calc(100vh - 280px); /* 限制最大高度 */
}

/* 自定义滚动条样式 */
.question-list-scroll::-webkit-scrollbar {
  width: 8px;
}

.question-list-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.question-list-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.question-list-scroll::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.question-grid-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  border-radius: 6px;
  background-color: #f4f4f5;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.question-grid-item:hover {
  background-color: #e4e7ed;
  transform: translateY(-2px);
}

.question-grid-item.active {
  background-color: #409eff;
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.4);
}

.question-grid-item.answered {
  background-color: #67c23a;
  color: white;
}

.question-grid-item.marked::after {
  content: "";
  position: absolute;
  top: 2px;
  right: 2px;
  width: 8px;
  height: 8px;
  background-color: #e6a23c;
  border-radius: 50%;
}

.question-index {
  font-weight: 500;
  z-index: 1;
}

.mark-icon {
  position: absolute;
  top: 2px;
  right: 2px;
  font-size: 12px;
  color: #e6a23c;
  z-index: 2;
}

.question-type-tag {
  position: absolute;
  bottom: 2px;
  left: 2px;
  font-size: 8px;
  z-index: 2;
}

.choice-question {
  border-left: 4px solid #409eff; /* 蓝色边框表示客观题 */
}

.subjective-question {
  border-left: 4px solid #67c23a; /* 绿色边框表示主观题 */
}

/* 题目列表分组样式 */
.question-type-group {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.question-type-title {
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.question-count {
  font-size: 14px;
  color: #909399;
}

/* 题目内容区域 */
.question-content-container {
  display: flex;
  flex-direction: column;
  min-height: 0; /* 重要：允许容器在 flex 布局中缩小 */
  max-height: calc(100vh - 280px); /* 限制最大高度，确保底部按钮可见 */
  overflow: hidden;
  padding-bottom: 60px; /* 给标记按钮留出空间 */
}

.question-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  min-height: 0; /* 使卡片内部也能正确处理溢出 */
  max-height: calc(100vh - 350px); /* 限制卡片最大高度 */
}

.question-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 25px;
  overflow-y: auto; /* 当内容过多时允许滚动 */
  max-height: calc(100vh - 400px); /* 限制题目详情区域的最大高度 */
  padding-bottom: 20px; /* 添加底部内边距，防止选项被遮挡 */
}

.question-main {
  flex: 1;
}

.question-title {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-type-tag-in-content {
  font-size: 12px;
}

.question-text {
  margin: 0;
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.attachment-section {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.options-section {
  flex: 1;
  margin-bottom: 20px; /* 添加底部边距，防止被标记按钮遮挡 */
}

.section-title {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
}

.option-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.option-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.option-item.disabled {
  opacity: 0.7;
}

.option-radio {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.option-key {
  font-weight: 600;
  color: #409eff;
}

.option-content {
  flex: 1;
  line-height: 1.6;
}

/* 多选题样式 */
.multiple-choice-section,
.single-choice-section {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.option-item-checkbox,
.option-item-radio {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  padding: 12px 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  transition: all 0.3s;
}

.option-item-checkbox:hover,
.option-item-radio:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.option-item-checkbox.selected,
.option-item-radio.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.option-item-checkbox .el-checkbox__label,
.option-item-radio .el-radio__label {
  display: flex;
  align-items: flex-start;
  width: 100%;
  gap: 10px;
}

.option-key {
  font-weight: 600;
  color: #409eff;
  min-width: 25px;
}

.option-content {
  flex: 1;
  line-height: 1.6;
}

/* 主观题区域 */
.subjective-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.subjective-answer-area {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ebeef5;
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 文本框容器 - 限制高度并添加滚动 */
.textarea-container {
  flex: 1;
  min-height: 150px;
  max-height: 35vh; /* 限制最大高度为视口高度的35%，确保底部按钮可见 */
  overflow-y: auto;
  margin-bottom: 15px;
}

.case-analysis-format,
.calculation-format,
.comprehensive-format {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0; /* 使内部flex项目能正确计算高度 */
}

.answer-textarea {
  width: 100%;
  flex: 1;
}

.answer-textarea :deep(.el-textarea__inner) {
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
  font-family: inherit;
  min-height: 120px; /* 最小高度 */
  max-height: 65vh; /* 最大高度限制 */
}

.analysis-tips,
.calculation-tips,
.comprehensive-tips {
  background: #f0f9ff;
  border-left: 4px solid #409eff;
  padding: 15px;
  border-radius: 0 4px 4px 0;
  font-size: 14px;
  flex-shrink: 0; /* 不允许压缩 */
}

.analysis-tips ul,
.calculation-tips ul,
.comprehensive-tips ul {
  margin: 10px 0;
  padding-left: 20px;
}

.analysis-tips li,
.calculation-tips li,
.comprehensive-tips li {
  margin: 5px 0;
  color: #606266;
}

.no-question {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
}

.question-actions {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  flex-shrink: 0; /* 防止被压缩 */
  padding: 15px 0;
  background: rgba(255, 255, 255, 0.95); /* 半透明背景色 */
  position: fixed; /* 固定在底部导航栏正上方 */
  bottom: 135px; /* 距离底部导航栏上方 */
  left: 240px; /* 从左侧边栏右侧开始 */
  right: 240px; /* 到右侧边栏左侧结束 */
  z-index: 99; /* 确保在内容之上，但在底部导航栏之下 */
  border-top: 1px solid #ebeef5; /* 添加顶部边框 */
  backdrop-filter: blur(5px); /* 添加背景模糊效果 */
}

.action-btn {
  border-radius: 8px;
  padding: 10px 20px;
}

.mark-btn {
  background-color: #fff;
  border: 1px solid #dcdfe6;
}

.mark-btn:hover {
  background-color: #fdf6ec;
  border-color: #e6a23c;
  color: #e6a23c;
}

/* 答题状态区域 */
.status-container {
  display: flex;
  flex-direction: column;
}

.status-card {
  flex: 1;
  border-radius: 8px;
}

.status-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.type-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-top: 15px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
}

.stat-value.answered {
  color: #67c23a;
}

.stat-value.marked {
  color: #e6a23c;
}

.stat-value.unanswered {
  color: #909399;
}

.stat-value.single-choice {
  color: #909399;
}

.stat-value.multiple-choice {
  color: #e6a23c;
}

.stat-value.case-analysis {
  color: #f56c6c;
}

.stat-value.calculation {
  color: #67c23a;
}

.stat-value.comprehensive {
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 导航区域 */
.exam-footer-card {
  border-radius: 12px;
  position: fixed; /* 固定在底部 */
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0 20px 20px 20px; /* 添加左右和底部边距 */
  z-index: 100; /* 确保在最上层 */
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1); /* 添加顶部阴影 */
}

.navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px;
  gap: 15px;
}

.nav-btn {
  border-radius: 8px;
  padding: 10px 20px;
  min-width: 100px;
}

.question-page-info {
  flex: 1;
  text-align: center;
}

.page-text {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
  background: linear-gradient(135deg, #ecf5ff, #f0f9ff);
  padding: 10px 25px;
  border-radius: 20px;
  border: 2px solid #409eff;
  display: inline-block;
}

.submit-btn {
  border-radius: 8px;
  padding: 10px 25px;
  background: linear-gradient(135deg, #f56c6c, #e64980);
  border: none;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #e64980, #f56c6c);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 150px 1fr 150px;
  }
}

@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .question-list-container,
  .status-container {
    order: 2;
  }

  .question-content-container {
    order: 1;
  }

  .question-grid {
    grid-template-columns: repeat(5, 1fr);
  }

  .type-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .exam-paper-container {
    padding: 10px;
  }

  .main-content {
    gap: 10px;
  }

  .exam-header {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .navigation {
    flex-direction: row; /* 保持水平排列 */
    gap: 10px;
  }

  .question-page-info {
    order: 2;
  }

  .nav-btn:first-child {
    order: 1;
  }

  .nav-btn:nth-child(3) {
    order: 3;
  }

  .submit-btn {
    order: 4;
  }

  .question-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>
