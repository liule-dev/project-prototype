<template>
  <div class="short-answer-question-container">
    <!-- 顶部导航 -->
    <div class="header-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>题目面板</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '' }">添加简答题</el-breadcrumb-item>
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
          v-model="questionContent"
          maxlength="5000"
          show-word-limit
        ></el-input>
      </div>

      <!-- 题目答案区域 -->
      <div class="form-section">
        <h3 class="section-title">题目答案</h3>
        <el-input
          type="textarea"
          :rows="6"
          placeholder="请输入参考答案"
          v-model="shortAnswer"
          maxlength="5000"
          show-word-limit
        ></el-input>
      </div>

      <!-- 难度选择区域 -->
      <div class="form-section">
        <h3 class="section-title">难度</h3>
        <el-select
          v-model="difficulty"
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
          v-model="knowledgePoints"
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
          v-model="explanation"
        ></el-input>
      </div>

      <!-- 按钮区域 -->
      <div class="button-group">
        <el-button
          type="success"
          icon="el-icon-check"
          @click="saveQuestion"
          :loading="isSaving"
        >
          添加题目
        </el-button>
        <el-button @click="resetForm">重置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import * as api from "@/stores/gain.js";

const route = useRoute();
const router = useRouter();

// 题库ID
const question_bank = ref(null);

// 表单数据
const questionContent = ref('');
const shortAnswer = ref('');
const difficulty = ref('');
const knowledgePoints = ref('');
const explanation = ref('');
const isSaving = ref(false);

// 难度选项
const difficultyOptions = ref([
  '难',
  '一般',
  '简单'
]);

// 保存题目
const saveQuestion = () => {
  // 验证必填字段
  if (!questionContent.value.trim()) {
    ElMessage.error('请填写题干内容');
    return;
  }

  if (!shortAnswer.value.trim()) {
    ElMessage.error('请填写参考答案');
    return;
  }

  if (!difficulty.value) {
    ElMessage.error('请选择难度');
    return;
  }

  if (!knowledgePoints.value.trim()) {
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
    topic_content: questionContent.value,
    topic_answer: shortAnswer.value,
    topic_difficulty: difficulty.value,
    topic_knowledge: knowledgePoints.value,
    topic_analysis: explanation.value,
    Q_data: question_bank.value
  };

  isSaving.value = true;

  api.addTopic(
    'http://localhost:8000/topic/',
    questionData,
    '添加失败',
    () => {
      resetForm();
      // 跳转回题目列表
      setTimeout(() => {
        router.push({
          name: 'topic_list',
          params: { id: question_bank.value }
        });
      }, 1000);
    },
    () => {
      isSaving.value = false;
    }
  );
};

// 重置表单
const resetForm = () => {
  questionContent.value = '';
  shortAnswer.value = '';
  difficulty.value = '';
  knowledgePoints.value = '';
  explanation.value = '';
};

// 页面加载时获取题库ID
onMounted(() => {
  const bankId = route.params.bankId;
  console.log('添加简答题页接收的题库ID:', bankId);

  if (bankId) {
    question_bank.value = bankId;
  } else {
    ElMessage.warning('未获取到题库信息，请从题库详情页进入');
  }
});
</script>

<style scoped>
.short-answer-question-container {
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
