<template>
  <div class="question-add-page min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部导航栏 -->
    <el-page-header
      @back="handleBack"
      :content="questionType === '单项选择题' ? '添加单项选择题' : '添加多项选择题'"
      class="page-header bg-white border-b border-gray-200 shadow-sm"
    />

    <!-- 主要内容区 -->
    <main class="main-content flex-1 container mx-auto px-4 py-6">
      <el-card class="question-card max-w-3xl mx-auto rounded-xl shadow-lg">
        <!-- 显示当前所属题库ID -->
        <div class="bank-id-info mb-6 p-4 bg-blue-50 rounded-lg">
          <span class="text-gray-600 font-medium">当前题库ID：</span>
          <span class="font-medium text-blue-600">{{ question_bank || '未获取到' }}</span>
        </div>

        <el-form
          ref="questionForm"
          :model="question"
          :rules="rules"
          label-width="100px"
          class="question-form space-y-6"
        >
          <!-- 题目题干 -->
          <el-form-item label="题目题干" prop="stem" required>
            <el-input
              v-model="question.stem"
              type="textarea"
              :rows="4"
              placeholder="请输入题目内容"
              :maxlength="5000"
              show-word-limit
              class="stem-input rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </el-form-item>

          <!-- 题目选项 -->
          <el-form-item label="题目选项" required>
            <div
              v-for="(option, index) in question.options"
              :key="index"
              class="option-item mb-6 p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <el-row :gutter="10" align="middle">
                <el-col :span="1" class="text-center font-medium option-label text-blue-600">
                  {{ String.fromCharCode(65 + index) }}
                </el-col>
                <el-col :span="16">
                  <el-input
                    v-model="option.content"
                    placeholder="输入选项内容"
                    @input="validateOption(index)"
                    class="option-input rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  />
                </el-col>
                <el-col :span="5">
                  <template v-if="questionType === '单项选择题'">
                    <el-radio
                      v-model="correctOption"
                      :label="index"
                      name="correctOption"
                      @change="validateCorrectAnswers"
                      class="correct-radio text-blue-600"
                    >
                      正确答案
                    </el-radio>
                  </template>
                  <template v-else>
                    <el-checkbox
                      v-model="option.isCorrect"
                      @change="validateCorrectAnswers"
                      class="correct-checkbox text-blue-600"
                    >
                      正确答案
                    </el-checkbox>
                  </template>
                </el-col>
                <el-col :span="2" class="text-right">
                  <el-button
                    v-if="question.options.length > 2"
                    icon="Delete"
                    size="small"
                    type="text"
                    text-color="#ff4d4f"
                    @click="removeOption(index)"
                    class="delete-option-btn hover:text-red-600 transition-colors"
                  />
                </el-col>
              </el-row>
              <!-- 选项错误提示 -->
              <el-form-item
                v-if="optionErrors[index]"
                :prop="`options[${index}].content`"
                :error="optionErrors[index]"
                class="option-error mt-2 text-red-500"
              />
            </div>

            <!-- 添加选项按钮 -->
            <div class="flex justify-end mt-4">
              <el-button
                type="primary"
                plain
                size="small"
                @click="addOption"
                :disabled="question.options.length >= 5"
                class="add-option-btn px-4 py-2 rounded-lg"
              >
                添加选项
              </el-button>
            </div>

            <!-- 正确答案验证提示 -->
            <el-form-item
              v-if="hasCorrectAnswerError"
              prop="options"
              :error="correctAnswerError"
              class="correct-answer-error mt-4 text-red-500"
            />
          </el-form-item>

          <el-form-item label="难度">
            <el-select v-model="question.difficulty" placeholder="请选择难度" class="difficulty-select rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500">
              <el-option
                v-for="item in difficultys"
                :key="item"
                :label="item"
                :value="item"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="题目知识点">
            <el-input
              v-model="question.knowledge"
              type="textarea"
              :rows="3"
              placeholder="请输入题目知识点"
              class="knowledge-input rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </el-form-item>

          <el-form-item label="题目解析">
            <el-input
              v-model="question.explanation"
              type="textarea"
              :rows="3"
              placeholder="请输入题目解析内容(如没有请忽略)"
              class="explanation-input rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </el-form-item>

          <!-- 操作按钮 -->
          <el-form-item class="operation-buttons">
            <el-button
              type="primary"
              @click="saveQuestion"
              class="mr-4 px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              :loading="isSaving"
            >
              添加题目
            </el-button>
            <el-button
              type="default"
              @click="resetForm"
              class="px-6 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import {ref, reactive, watch, onMounted, defineEmits} from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import api, {addTopic} from '@/stores/gain';

const router = useRouter();
const route = useRoute();

// 当前题库ID（从路由参数获取）
const question_bank = ref(null);

// 题目类型
const questionType = ref(); // 默认为单选题

// 题目数据模型
const question = reactive({
  stem: '',
  options: [
    { content: '', isCorrect: false },  // A
    { content: '', isCorrect: false },  // B
    { content: '', isCorrect: false },  // C
    { content: '', isCorrect: false }   // D
  ],
  explanation: '',
  difficulty: '',
  knowledge: '',
  analysis: ''
});

// 保存状态
const isSaving = ref(false);

// 正确选项绑定（仅用于单选题）
const correctOption = ref(null);

// 表单验证规则
const rules = {
  stem: [
    { required: true, message: '请输入题目内容', trigger: 'blur' },
    { max: 5000, message: '题目内容不能超过5000个字符', trigger: 'blur' }
  ]
};

// 选项验证错误信息
const optionErrors = ref(new Array(5).fill(''))
const hasCorrectAnswerError = ref(false);
const correctAnswerError = ref('请选择一个正确答案');

// 难度选项
const difficultys = ref(['难', '一般', '简单']);

// 验证选项
const validateOption = (index) => {
  // 允许E选项(索引为4)为空
  if (index === 4 && !question.options[index].content.trim()) {
    optionErrors.value[index] = '';  // 不设置错误信息
    return;
  }

  if (!question.options[index].content.trim()) {
    optionErrors.value[index] = '请输入选项内容';
  } else {
    optionErrors.value[index] = '';
  }
};

// 验证正确答案
const validateCorrectAnswers = () => {
  if (questionType.value === '单项选择题') {
    // 更新选项的isCorrect状态
    question.options.forEach((option, index) => {
      option.isCorrect = index === correctOption.value;
    });
    // 检查是否选择了正确答案
    hasCorrectAnswerError.value = correctOption.value === null;
  } else {
    // 多选题检查是否有至少一个正确答案
    const hasCorrectAnswer = question.options.some(option => option.isCorrect);
    hasCorrectAnswerError.value = !hasCorrectAnswer;

    // 对于多选题，需要更新错误提示文字
    correctAnswerError.value = '请至少选择一个正确答案';
  }
};

// 添加新选项
const addOption = () => {
  if (question.options.length < 5) {
    question.options.push({ content: '', isCorrect: false });
    optionErrors.value.push(''); // 这行已经正确
  } else {
    ElMessage.info('最多只能添加5个选项(A-E)');
  }
};

// 删除选项
const removeOption = (index) => {
  if (question.options.length <= 2) {
    ElMessage.warning('至少保留2个选项');
    return;
  }

  // 处理正确选项索引调整（仅适用于单选题）
  if (questionType.value === '单项选择题') {
    if (correctOption.value === index) {
      correctOption.value = null;
    } else if (correctOption.value > index) {
      correctOption.value--;
    }
  }

  question.options.splice(index, 1);
  optionErrors.value.splice(index, 1);
  validateCorrectAnswers();
};

const refreshCallback = ref(null);
const emit = defineEmits(['refreshList']);

// 保存题目到后端
const saveQuestion = () => {
  // 验证所有选项
  let isValid = true;
  question.options.forEach((_, index) => {
    validateOption(index);
    if (optionErrors.value[index]) {
      isValid = false;
    }
  });

  // 验证正确答案
  validateCorrectAnswers();
  if (hasCorrectAnswerError.value) {
    isValid = false;
  }

  // 验证题库ID
  if (!question_bank.value) {
    ElMessage.error('未获取到题库信息，请返回重试');
    return;
  }

  if (!isValid) {
    // 滚动到第一个错误位置
    const firstError = document.querySelector('.el-form-item__error');
    if (firstError) {
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return;
  }

  // 准备提交数据
  let correctAnswerContent = '';
  if (questionType.value === '单项选择题') {
    correctAnswerContent = question.options[correctOption.value].content;
  } else {
    // 多选题：获取所有正确选项的内容，用逗号连接
    correctAnswerContent = question.options
      .filter(option => option.isCorrect)
      .map(option => option.content)
      .join(',');
  }

  const topicData = {
    topic_content: question.stem,
    topic_answer: correctAnswerContent,
    A: question.options[0]?.content || '',
    B: question.options[1]?.content || '',
    C: question.options[2]?.content || '',
    D: question.options[3]?.content || '',
    E: question.options.length > 4 ? question.options[4].content : '',
    topic_difficulty: question.difficulty,
    topic_analysis: question.explanation,
    topic_knowledge: question.knowledge,
    Q_data: question_bank.value,  // 传递题库ID
    question_type: questionType.value  // 题目类型
  };

  api.addTopic(
      'http://localhost:8000/topic/',
      topicData,
      '添加失败',
      () => {
        if (refreshCallback.value) {
          refreshCallback.value();
        }
        emit('refreshList');
        setTimeout(() => {
          router.push({
            name: 'topic_list',
            params: { id: question_bank.value }
          });
        }, 1000);
      }
  );
};

// 重置表单
const resetForm = () => {
  question.stem = '';
  question.options = [
    {content: '', isCorrect: false},
    {content: '', isCorrect: false},
    {content: '', isCorrect: false},
    {content: '', isCorrect: false},
    {content: '', isCorrect: false}
  ];
  question.explanation = '';
  question.difficulty = '';
  question.knowledge = '';
  optionErrors.value = new Array(4).fill('');
  correctOption.value = null;
  hasCorrectAnswerError.value = false;

  // 根据题目类型设置正确的错误提示
  correctAnswerError.value = questionType.value === '单项选择题'
    ? '请选择一个正确答案'
    : '请至少选择一个正确答案';
};

// 返回上一页
const handleBack = () => {
  ElMessageBox.confirm(
      '您确定要离开吗？当前输入的内容可能不会保存。',
      '确认离开',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
  ).then(() => {
    // 返回题库详情页
    router.push({name: 'topic_list', params: {id: question_bank.value}});
  }).catch(() => {
    // 取消返回
  });
};

// 监听选项变化，自动验证
watch(
    () => question.options,
    () => {
      validateCorrectAnswers();
    },
    {deep: true}
);

// 页面加载时获取题库ID和题目类型
onMounted(() => {
  // 从路由参数中获取题库ID
  const bankId = route.params.bankId;
  questionType.value = route.params.type1;
  // 从路由查询参数获取题目类型
  const routeQuestionType = questionType.value;
  if (routeQuestionType === 'multiple' || routeQuestionType === '多项选择题') {
    questionType.value = '多项选择题';
    correctAnswerError.value = '请至少选择一个正确答案'; // 更新错误提示
  } else {
    questionType.value = '单项选择题';
    correctAnswerError.value = '请选择一个正确答案'; // 更新错误提示
  }

  if (bankId) {
    question_bank.value = bankId;
  } else {
    ElMessage.warning('未获取到题库信息，请从题库详情页进入');
  }
});
</script>

<style scoped lang="scss">
.question-add-page {
  .page-header {
    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    transition: box-shadow 0.3s ease;
  }

  .main-content {
    .question-card {
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
    }

    .bank-id-info {
      transition: background-color 0.3s ease;
      &:hover {
        background-color: #e6f2ff;
      }
    }

    .question-form {
      .stem-input,
      .option-input,
      .knowledge-input,
      .explanation-input,
      .difficulty-select {
        transition: all 0.2s ease;
      }

      .option-item {
        transition: all 0.3s ease;
        &:hover {
          background-color: #f9fafb;
          border-color: #d1d5db;
        }
      }

      .add-option-btn,
      .operation-buttons .el-button {
        transition: all 0.3s ease;
      }

      .delete-option-btn {
        &:hover {
          transform: scale(1.1);
        }
        transition: transform 0.2s ease;
      }
    }
  }
}
</style>
