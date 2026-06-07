<template>
  <div class="edit-gap-question-container">
    <!-- 顶部导航 -->
    <div class="header-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item>题目面板</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '' }">编辑填空题</el-breadcrumb-item>
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

        <!-- 单个填空项 -->
        <div class="blank-item">
          <div class="blank-header">
            <span class="blank-label">*答案</span>
          </div>
          <el-input
            placeholder="输入答案内容"
            v-model="blankContent"
            class="blank-input"
          ></el-input>
        </div>
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
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import * as api from "@/stores/gain.js";
import {fetchData, updateQuestionBank} from "@/stores/gain.js";

const route = useRoute();
const router = useRouter();

// 题库ID和题目ID
const question_bank = ref(null);
const topicId = ref(null);

// 表单数据
const questionContent = ref('');
const blankContent = ref('');
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

// 获取题目详情
const fetchTopicDetail = async () => {
  if (!topicId.value) {
    ElMessage.error('未获取到题目信息');
    return;
  }
  console.log('请求的URL:', `http://localhost:8000/topics/${topicId.value}/`);
  await api.getTopicDetail(
      `http://localhost:8000/topic/${topicId.value}/`,
      (data) => {
        console.log('API返回的数据:', data);
        // 填充表单数据
        questionContent.value = data.topic_content || '';
        blankContent.value = data.topic_answer || '';
        difficulty.value = data.topic_difficulty || '';
        knowledgePoints.value = data.topic_knowledge || '';
        explanation.value = data.topic_analysis || '';
        question_bank.value = data.Q_data || '';
      },
      () => {
        ElMessage.error('获取题目详情失败');
      }
  );
};

// 更新题目
const updateQuestion = async () => {
  // 验证必填字段
  if (!questionContent.value.trim()) {
    ElMessage.error('请填写题干内容');
    return;
  }

  if (!blankContent.value.trim()) {
    ElMessage.error('请填写答案内容');
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
    topic_answer: blankContent.value,
    topic_difficulty: difficulty.value,
    topic_knowledge: knowledgePoints.value,
    topic_analysis: explanation.value,
    Q_data: question_bank.value
  };
  console.log('准备提交的数据:', questionData.topic_content);
  isSaving.value = true;
  const updateResult = ref(null);
  await api.updateQuestionBank(
      `http://localhost:8000/topic/${topicId.value}/`,
      updateResult,
      questionData,
      '更新失败',
      () => {
        ElMessage.success('题目更新成功');
        // 跳转回题目列表
        setTimeout(() => {
          router.push({
            name: 'topic_list',
            params: {id: question_bank.value}
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
  fetchTopicDetail();
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

// 页面加载时获取题库ID和题目ID
onMounted(() => {
  const bankId = route.params.bankId;
  const id = route.params.id;

  console.log('编辑填空题页接收的题库ID:', bankId);
  console.log('编辑填空题页接收的题目ID:', id);

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
.edit-gap-question-container {
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

.blank-item {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.blank-header {
  margin-bottom: 10px;
}

.blank-label {
  color: #333;
  font-weight: 500;
}

.blank-input, .difficulty-select {
  width: 100%;
}

.button-group {
  margin-top: 10px;
  padding: 0 20px;
  display: flex;
  gap: 15px;
}
</style>
