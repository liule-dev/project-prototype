<template>
  <div class="edit-choice-question-container">
    <!-- 顶部导航 -->
    <div class="header-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>题目面板</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '' }">编辑选择题</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 主要内容区域 -->
    <el-card class="question-card">
      <!-- 显示当前所属题库ID -->
      <div class="bank-id-info mb-6 p-4 bg-blue-50 rounded-lg">
        <span class="text-gray-600 font-medium">当前题库ID：</span>
        <span class="font-medium text-blue-600">{{ question_bank || '未获取到' }}</span>
      </div>

      <!-- 题干输入区域 -->
      <div class="form-section">
        <h3 class="section-title">题目题干</h3>
        <el-input
          type="textarea"
          :rows="6"
          placeholder="请输入题干内容"
          v-model="question.stem"
          maxlength="5000"
          show-word-limit
        ></el-input>
      </div>

      <!-- 题目选项区域 -->
      <div class="form-section">
        <h3 class="section-title">题目选项</h3>

        <div
          v-for="(option, index) in question.options"
          :key="index"
          class="option-item"
        >
          <div class="option-header">
            <span class="option-label">{{ String.fromCharCode(65 + index) }}选项</span>
          </div>
          <el-input
            placeholder="输入选项内容"
            v-model="option.content"
            class="option-input"
          ></el-input>

          <el-radio
            v-model="correctOption"
            :label="index"
            name="correctOption"
            @change="setCorrectAnswer"
            class="correct-radio"
          >
            设为正确答案
          </el-radio>

          <el-button
            v-if="question.options.length > 2"
            type="danger"
            icon="el-icon-delete"
            size="small"
            @click="removeOption(index)"
            class="remove-option-btn"
          >
            删除
          </el-button>
        </div>

        <el-button
          type="primary"
          icon="el-icon-plus"
          @click="addOption"
          :disabled="question.options.length >= 5"
          class="add-option-btn"
        >
          添加选项
          <template v-if="question.options.length >= 5">
            <span>(最多5个选项)</span>
          </template>
        </el-button>
      </div>

      <!-- 难度选择区域 -->
      <div class="form-section">
        <h3 class="section-title">难度</h3>
        <el-select
          v-model="question.difficulty"
          placeholder="请选择难度"
          class="difficulty-select"
        >
          <el-option
            v-for="item in difficultyOptions"
            :key="item"
            :label="item"
            :value="item"
          ></el-option>
        </el-select>
      </div>

      <!-- 知识点输入区域 -->
      <div class="form-section">
        <h3 class="section-title">题目知识点</h3>
        <el-input
          type="textarea"
          :rows="3"
          placeholder="请输入题目知识点，多个知识点用逗号分隔"
          v-model="question.knowledge"
          maxlength="500"
          show-word-limit
        ></el-input>
      </div>

      <!-- 题目解析区域 -->
      <div class="form-section">
        <h3 class="section-title">题目解析</h3>
        <el-input
          type="textarea"
          :rows="4"
          placeholder="请输入题目解析内容(如没有请忽略)"
          v-model="question.explanation"
        ></el-input>
      </div>

      <!-- 按钮区域 -->
      <div class="button-group">
        <el-button
          type="success"
          icon="el-icon-check"
          @click="updateQuestion"
          :loading="isSaving"
        >
          保存修改
        </el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import * as api from "@/stores/gain.js";

const route = useRoute();
const router = useRouter();

// 题库ID和题目ID
const question_bank = ref(null);
const topicId = ref(null);

// 表单数据
const question = reactive({
  stem: '',
  options: [
    { content: '' },
    { content: '' },
    { content: '' },
    { content: '' }
  ],
  explanation: '',
  difficulty: '',
  knowledge: ''
});

const correctOption = ref(null);
const isSaving = ref(false);

// 难度选项
const difficultyOptions = ref([
  '难',
  '一般',
  '简单'
]);

// 设置正确答案
const setCorrectAnswer = () => {
  // 正确答案会在保存时处理
};

// 添加选项
const addOption = () => {
  if (question.options.length < 5) {
    question.options.push({ content: '' });
  } else {
    ElMessage.info('最多只能添加5个选项');
  }
};

// 删除选项
const removeOption = (index) => {
  if (question.options.length <= 2) {
    ElMessage.warning('至少保留2个选项');
    return;
  }

  question.options.splice(index, 1);

  // 调整正确答案索引
  if (correctOption.value === index) {
    correctOption.value = null;
  } else if (correctOption.value > index) {
    correctOption.value--;
  }
};

// 获取题目详情
const fetchTopicDetail = async () => {
  if (!topicId.value) {
    ElMessage.error('未获取到题目信息');
    return;
  }

  await api.getTopicDetail(
    `http://localhost:8000/topic/${topicId.value}/`,
    (data) => {
      console.log('API返回的数据:', data);

      // 填充表单数据
      question.stem = data.topic_content || '';
      question.difficulty = data.topic_difficulty || '';
      question.knowledge = data.topic_knowledge || '';
      question.explanation = data.topic_analysis || '';
      question_bank.value = data.Q_data || '';

      // 处理选项
      const options = [];
      let correctIndex = null;

      ['A', 'B', 'C', 'D', 'E'].forEach((key, index) => {
        if (data[key]) {
          options.push({ content: data[key] });

          // 检查是否为正确答案
          if (data.topic_answer === data[key]) {
            correctIndex = index;
          }
        }
      });

      // 确保至少有2个选项
      while (options.length < 2) {
        options.push({ content: '' });
      }

      question.options = options;
      correctOption.value = correctIndex;
    },
    () => {
      ElMessage.error('获取题目详情失败');
    }
  );
};

// 更新题目
const updateQuestion = async () => {
  // 验证必填字段
  if (!question.stem.trim()) {
    ElMessage.error('请填写题干内容');
    return;
  }

  // 验证选项
  let hasEmptyOption = false;
  question.options.forEach(option => {
    if (!option.content.trim()) {
      hasEmptyOption = true;
    }
  });

  if (hasEmptyOption) {
    ElMessage.error('请填写所有选项内容');
    return;
  }

  if (correctOption.value === null) {
    ElMessage.error('请选择正确答案');
    return;
  }

  if (!question.difficulty) {
    ElMessage.error('请选择难度');
    return;
  }

  if (!question.knowledge.trim()) {
    ElMessage.error('请填写题目知识点');
    return;
  }

  // 验证题库ID
  if (!question_bank.value) {
    ElMessage.error('未获取到题库信息，请返回重试');
    return;
  }

  // 准备提交数据
  const questionData = {
    topic_number: topicId.value,
    topic_content: question.stem,
    topic_answer: question.options[correctOption.value].content,
    topic_difficulty: question.difficulty,
    topic_knowledge: question.knowledge,
    topic_analysis: question.explanation,
    Q_data: question_bank.value
  };

  // 添加选项字段
  question.options.forEach((option, index) => {
    const key = String.fromCharCode(65 + index); // A, B, C, D, E
    questionData[key] = option.content;
  });

  isSaving.value = true;

  try {
    // 使用 await 等待更新完成
    const success = await api.updateQuestionBank(
      `http://localhost:8000/topic/${topicId.value}/`,
      ref(null),
      questionData,
      '更新失败'
    );

    if (success) {
      ElMessage.success('题目更新成功');
      // 更新成功后跳转
      setTimeout(() => {
        router.push({
          name: 'topic_list',
          params: { id: question_bank.value }
        });
      }, 1000);
    }
  } catch (error) {
    console.error('更新失败:', error);
    ElMessage.error('更新失败');
  } finally {
    isSaving.value = false;
  }
};

// 重置表单
const resetForm = () => {
  fetchTopicDetail();
};

// 返回上一页
const goBack = () => {
  router.push("/main");
};

// 页面加载时获取题库ID和题目ID
onMounted(() => {
  const bankId = route.params.bankId || route.query.Question_number;
  const id = route.params.id || route.params.topicId;

  if (bankId) {
    question_bank.value = bankId;
  } else {
    ElMessage.warning('未获取到题库信息，请从题库详情页进入');
  }

  if (id) {
    topicId.value = id;
    fetchTopicDetail();
  } else {
    ElMessage.warning('未获取到题目信息，请从题目列表页进入');
  }
});
</script>

<style scoped>
.edit-choice-question-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.header-nav {
  margin-bottom: 20px;
}

.question-card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  padding-bottom: 20px;
}

.bank-id-info {
  margin: 0 20px 20px;
}

.form-section {
  margin-bottom: 30px;
  padding: 0 20px;
}

.section-title {
  color: #409eff;
  font-size: 16px;
  margin-bottom: 15px;
  padding-top: 15px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 5px;
}

.option-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.option-header {
  margin-bottom: 10px;
}

.option-label {
  color: #333;
  font-weight: 500;
  min-width: 60px;
}

.option-input {
  flex: 1;
  min-width: 200px;
}

.correct-radio {
  margin-right: 15px;
}

.remove-option-btn {
  margin-left: auto;
}

.add-option-btn {
  width: 100%;
  margin-top: 10px;
}

.difficulty-select {
  width: 100%;
}

.button-group {
  margin-top: 10px;
  padding: 0 20px;
  display: flex;
  gap: 15px;
}
</style>
