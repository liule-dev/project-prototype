<template>
  <el-container class="full-height">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-wrapper">
        <!-- 面包屑导航 -->
        <el-breadcrumb separator="/" class="bread-crumb">
          <el-breadcrumb-item :to="{ name: 'QuestionBankList' }">题库列表</el-breadcrumb-item>
          <el-breadcrumb-item>{{ topicInfo.name || '题库详情' }}</el-breadcrumb-item>
        </el-breadcrumb>

        <div class="header-actions">
          <el-button
            type="default"
            @click="handleBack"
            class="back-btn"
            icon="el-icon-arrow-left"
          >
            返回
          </el-button>
        </div>
      </div>
    </el-header>

    <el-main class="main-content">
      <!-- 加载状态 -->
      <el-loading
        v-if="loading"
        target=".main-content"
        text="正在加载数据..."
        background="rgba(255, 255, 255, 0.9)"
        spinner="el-icon-loading"
        :custom-class="['loading-container']"
      />

      <!-- 题库基本信息卡片 -->
      <el-card class="info-card mb-4" v-if="!loading" :shadow="hoverShadow">
        <div class="card-header">
          <h3 class="card-title">题库基本信息</h3>
          <div class="status-badge">
            <el-tag :type="getStatusTagType(topicInfo.status)" effect="dark">
              {{ topicInfo.status || '未知状态' }}
            </el-tag>
          </div>
        </div>

        <el-row :gutter="24" class="info-row">
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">题库编号</span>
              <span class="info-value">{{ topicInfo.Question_number || '未知' }}</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">所属年分</span>
              <span class="info-value">{{ topicInfo.grade1_name || '未知' }}</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">等级分类</span>
              <span class="info-value">{{ topicInfo.subject_name || '未知' }}</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">题目类型</span>
              <span class="info-value">{{ topicInfo.question_type || '未知' }}</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">公开状态</span>
              <span class="info-value">
                <el-tag :type="topicInfo.if_public ? 'success' : 'info'" size="small">
                  {{ topicInfo.if_public ? '公开' : '私有' }}
                </el-tag>
              </span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">题目总数</span>
              <span class="info-value count-badge">{{ topicInfo.question_total || 0 }} 题</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatTime(topicInfo.created_at) }}</span>
            </div>
          </el-col>
          <el-col :xs="12" :sm="8" :md="6" :lg="4" class="info-col">
            <div class="info-item">
              <span class="info-label">更新时间</span>
              <span class="info-value">{{ formatTime(topicInfo.updated_at) }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 题目列表 -->
      <el-card class="questions-card" v-if="!loading" :shadow="hoverShadow">
        <div slot="header" class="card-header flex items-center justify-between">
          <span class="card-title">题目列表</span>
          <div class="total-count">
            共 <span class="count">{{ topicInfo.question_total || 0 }}</span> 题
          </div>
        </div>

        <div class="custom-table">
          <!-- 表头 -->
          <div class="table-header">
            <div class="header-row">
              <div class="header-cell" :style="{ width: '5%' }">序号</div>
              <div class="header-cell" :style="{ width: '35%' }">题目内容</div>
              <div class="header-cell" :style="{ width: '10%' }">难度</div>
              <div class="header-cell" :style="{ width: '15%' }">创建时间</div>
              <div class="header-cell" :style="{ width: '15%' }">更新时间</div>
              <div class="header-cell text-right" :style="{ width: '20%' }">操作</div>
            </div>
          </div>

          <!-- 表体 -->
          <div class="table-body" style="height: calc(100vh - 480px); overflow-y: auto;">
            <div
              class="body-row"
              v-for="(item, index) in filteredQuestions"
              :key="item.topic_number"
              :class="{ 'row-hover': item.isHover, 'row-active': currentActiveRow === index }"
              @mouseenter="item.isHover = true"
              @mouseleave="item.isHover = false"
              @click="currentActiveRow = index"
            >
              <div class="body-cell" :style="{ width: '5%' }">{{ index + 1 }}</div>
              <div class="body-cell" :style="{ width: '35%' }">
                <div class="question-content">
                  <span v-html="highlightKeyword(item.topic_content)"></span>
                </div>
              </div>
              <div class="body-cell" :style="{ width: '10%' }">
                <el-tag :type="getDifficultyTagType(item.topic_difficulty)" size="small">
                  {{ item.topic_difficulty || '未设置' }}
                </el-tag>
              </div>
              <div class="body-cell" :style="{ width: '15%' }">{{ formatTime(item.created_at) }}</div>
              <div class="body-cell" :style="{ width: '15%' }">{{ formatTime(item.updated_at) }}</div>
              <div class="body-cell text-right" :style="{ width: '20%' }">
                <div class="btn-group">
                  <el-button
                    size="small"
                    @click.stop="viewTopic(item)"
                    class="view-btn"
                  >查看</el-button>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="filteredQuestions.length === 0" class="empty-state">
              <div class="empty-icon-container">
                <i class="el-icon-s-data empty-icon"></i>
              </div>
              <p class="empty-text">暂无匹配的题目</p>
              <p class="empty-subtext" v-if="searchKeyword">
                您搜索的关键词 "{{ searchKeyword }}" 没有找到相关结果
              </p>
              <el-button
                type="primary"
                @click="gotoAddTopic"
                class="empty-add-btn mt-4"
                icon="el-icon-plus"
              >
                添加题目
              </el-button>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <el-pagination
          v-if="total > 0"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="pagination"
          background
          :disabled="loading"
        />
      </el-card>
    </el-main>
  </el-container>

  <!-- 题目详情弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="70%"
    :before-close="handleDialogClose"
    class="question-dialog"
    :modal-opacity="0.1"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    center
  >
    <div v-if="currentQuestion" class="question-detail">
      <!-- 题目类型标识 -->
      <div class="question-type-badge">
        <el-tag :type="getQuestionTypeTagType()" effect="dark">
          {{ topicInfo.question_type || '题目' }}
        </el-tag>
      </div>

      <!-- 选择题详情 -->
      <div v-if="topicInfo.question_type === '选择题'" class="question-content-container">
        <el-descriptions title="题目详情" :column="1" border class="detail-descriptions">
          <el-descriptions-item label="题干" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_content }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="选项" class="content-item">
            <div class="options-list">
              <div class="option-item" v-if="currentQuestion.A">
                <span class="option-label">A.</span>
                <span class="option-content">{{ currentQuestion.A }}</span>
              </div>
              <div class="option-item" v-if="currentQuestion.B">
                <span class="option-label">B.</span>
                <span class="option-content">{{ currentQuestion.B }}</span>
              </div>
              <div class="option-item" v-if="currentQuestion.C">
                <span class="option-label">C.</span>
                <span class="option-content">{{ currentQuestion.C }}</span>
              </div>
              <div class="option-item" v-if="currentQuestion.D">
                <span class="option-label">D.</span>
                <span class="option-content">{{ currentQuestion.D }}</span>
              </div>
              <div class="option-item" v-if="currentQuestion.E">
                <span class="option-label">E.</span>
                <span class="option-content">{{ currentQuestion.E }}</span>
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="正确答案" class="content-item">
            <div class="answer-wrapper">
              <el-tag type="success" size="medium">{{ currentQuestion.topic_answer || '未设置' }}</el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="难度" class="content-item">
            <el-tag :type="getDifficultyTagType(currentQuestion.topic_difficulty)" size="medium">
              {{ currentQuestion.topic_difficulty || '未设置' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="知识点" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_knowledge || '未设置' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="解析" class="content-item">
            <div class="analysis-wrapper">
              {{ currentQuestion.topic_analysis || '暂无解析' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 判断题详情 -->
      <div v-else-if="topicInfo.question_type === '判断题'" class="question-content-container">
        <el-descriptions title="题目详情" :column="1" border class="detail-descriptions">
          <el-descriptions-item label="题干" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_content }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="答案" class="content-item">
            <div class="answer-wrapper">
              <el-tag type="success" size="medium">{{ currentQuestion.topic_answer || '未设置' }}</el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="难度" class="content-item">
            <el-tag :type="getDifficultyTagType(currentQuestion.topic_difficulty)" size="medium">
              {{ currentQuestion.topic_difficulty || '未设置' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="知识点" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_knowledge || '未设置' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="解析" class="content-item">
            <div class="analysis-wrapper">
              {{ currentQuestion.topic_analysis || '暂无解析' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 填空题详情 -->
      <div v-else-if="topicInfo.question_type === '填空题'" class="question-content-container">
        <el-descriptions title="题目详情" :column="1" border class="detail-descriptions">
          <el-descriptions-item label="题干" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_content }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="答案" class="content-item">
            <div class="answer-wrapper">
              <el-tag type="success" size="medium">{{ currentQuestion.topic_answer || '未设置' }}</el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="难度" class="content-item">
            <el-tag :type="getDifficultyTagType(currentQuestion.topic_difficulty)" size="medium">
              {{ currentQuestion.topic_difficulty || '未设置' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="知识点" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_knowledge || '未设置' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="解析" class="content-item">
            <div class="analysis-wrapper">
              {{ currentQuestion.topic_analysis || '暂无解析' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 简答题详情 -->
      <div v-else-if="topicInfo.question_type === '简答题'" class="question-content-container">
        <el-descriptions title="题目详情" :column="1" border class="detail-descriptions">
          <el-descriptions-item label="题干" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_content }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="参考答案" class="content-item">
            <div class="answer-wrapper">
              <div class="answer-content">{{ currentQuestion.topic_answer || '未设置' }}</div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="难度" class="content-item">
            <el-tag :type="getDifficultyTagType(currentQuestion.topic_difficulty)" size="medium">
              {{ currentQuestion.topic_difficulty || '未设置' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="知识点" class="content-item">
            <div class="content-wrapper">{{ currentQuestion.topic_knowledge || '未设置' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="解析" class="content-item">
            <div class="analysis-wrapper">
              {{ currentQuestion.topic_analysis || '暂无解析' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="editTopic(currentQuestion)">编辑题目</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '@/stores/gain';
import dayjs from 'dayjs';

// 路由相关
const router = useRouter();
const route = useRoute();

// 数据存储
const topicInfo = ref({});  // 题库基本信息
const questions = ref([]);  // 题目列表
const total = ref(0);       // 题目总数
const loading = ref(true);  // 加载状态
const hoverShadow = ref('hover'); // 卡片悬停阴影效果

// 搜索相关
const searchKeyword = ref('');
const currentActiveRow = ref(-1);

// 分页相关
const pageSize = ref(10);
const currentPage = ref(1);

// 获取题库ID
const bankId = route.params.id;

// 弹窗相关数据
const dialogVisible = ref(false);
const currentQuestion = ref(null);
const dialogTitle = computed(() => {
  if (!topicInfo.value.question_type) return '题目详情';
  return `${topicInfo.value.question_type}详情`;
});

// 过滤后的题目列表（带搜索功能）
const filteredQuestions = computed(() => {
  if (!searchKeyword.value.trim()) {
    return questions.value;
  }

  const keyword = searchKeyword.value.trim().toLowerCase();
  return questions.value.filter(item => {
    return item.topic_content.toLowerCase().includes(keyword);
  });
});

// 时间格式化
const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '未知';
};

// 根据状态获取标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case '已提交':
      return 'success';
    case '未提交':
      return 'warning';
    case '审核中':
      return 'info';
    case '已拒绝':
      return 'danger';
    default:
      return '';
  }
};

// 根据难度获取标签类型
const getDifficultyTagType = (difficulty) => {
  switch (difficulty) {
    case '简单':
      return 'success';
    case '中等':
      return 'warning';
    case '困难':
      return 'danger';
    default:
      return 'info';
  }
};

// 根据题目类型获取标签类型
const getQuestionTypeTagType = () => {
  switch (topicInfo.value.question_type) {
    case '选择题':
      return 'primary';
    case '判断题':
      return 'info';
    case '填空题':
      return 'warning';
    case '简答题':
      return 'success';
    default:
      return '';
  }
};

// 关键词高亮处理
const highlightKeyword = (content) => {
  if (!searchKeyword.value.trim() || !content) {
    return content;
  }

  const keyword = searchKeyword.value.trim();
  const regex = new RegExp(keyword, 'gi');
  return content.replace(regex, match => `<span class="highlight">${match}</span>`);
};

// 获取题库基本信息
const fetchTopicInfo = async () => {
  if (!bankId) {
    ElMessage.warning('未获取到题库ID，请返回列表页重试');
    loading.value = false;
    return;
  }

  try {
    const params = {
      Question_number: bankId
    };

    const response = await api.fetchData(
      'http://localhost:8000/questions/',
      topicInfo,
      '获取题库信息失败',
      params
    );

    if (response) {
      topicInfo.value = topicInfo.value.length > 0 ? topicInfo.value[0] : {};
      console.log('题库信息获取成功:', topicInfo.value);
    }
  } catch (error) {
    console.error('获取题库信息异常:', error);
    ElMessage.error('获取题库信息失败，请刷新重试');
  }
};

// 获取题库下的题目列表
const fetchQuestionsList = async () => {
  if (!bankId) {
    ElMessage.warning('未获取到题库ID，无法加载题目');
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    const params = {
      Q_data: bankId,
      page: currentPage.value,
      page_size: pageSize.value
    };

    const response = await api.fetchData(
        'http://localhost:8000/topic/',
        questions,
        '获取题目列表失败',
        params
    );

    if (response) {
      total.value = questions.value.total || 0;
      questions.value = questions.value.results || questions.value;
      console.log('题目列表获取成功:', questions.value);

      // 初始化行悬停状态
      questions.value.forEach(item => {
        item.isHover = false;
      });
    }
  } catch (error) {
    console.error('获取题目列表异常:', error);
    ElMessage.error('获取题目列表失败，请刷新重试');
  } finally {
    loading.value = false;
  }
};

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1; // 重置到第一页
  // 本地搜索无需重新请求接口
};

// 跳转至添加题目页
const gotoAddTopic = () => {
  if (!bankId) {
    ElMessage.warning('未获取到题库信息，无法添加题目');
    return;
  }

  switch (topicInfo.value.question_type) {
    case '选择题':
      router.push({ name: 'add_topic', params: { bankId } });
      break;
    case '填空题':
      router.push({ name: 'add_gap_topic', params: { bankId } });
      break;
    case '判断题':
      router.push({ name: 'add_judge_topic', params: { bankId } });
      break;
    case '简答题':
      router.push({ name: 'add_short_topic', params: { bankId } });
      break;
    default:
      ElMessage.warning('未识别的题目类型');
  }
};


// 返回题库列表
const handleBack = () => {
  router.push("/main");
};

// 查看题目详情
const viewTopic = (item) => {
  currentQuestion.value = item;
  dialogVisible.value = true;
};

// 编辑题目
const editTopic = (item) => {
  dialogVisible.value = false; // 关闭详情弹窗

  if (!item || !item.topic_number) {
    ElMessage.warning('未获取到题目信息，无法编辑');
    return;
  }

  switch (topicInfo.value.question_type) {
    case '选择题':
      router.push({
        name: 'topic_modify',
        params: { bankId, id: item.topic_number }
      });
      break;
    case '填空题':
      router.push({
        name: 'edit_gap_topic',
        params: { bankId, id: item.topic_number }
      });
      break;
    case '判断题':
      router.push({
        name: 'edit_judge_topic',
        params: { bankId, id: item.topic_number }
      });
      break;
    case '简答题':
      router.push({
        name: 'edit_short_topic',
        params: { bankId, id: item.topic_number }
      });
      break;
    default:
      ElMessage.warning('未识别的题目类型');
  }
};

// 删除题目
const handleDelete = (item) => {
  ElMessageBox.confirm(
      '确定要删除这道题目吗？删除后不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
  ).then(async () => {
    try {
      loading.value = true;
      const success = await api.deleteData(`http://localhost:8000/topic/${item.topic_number}/`, '删除题目失败');
      if (success) {
        ElMessage.success('删除成功');
        // 重新获取列表，保持当前页码
        await fetchQuestionsList();
      }
    } catch (error) {
      console.error('删除题目失败:', error);
      ElMessage.error('删除失败，请重试');
    } finally {
      loading.value = false;
    }
  }).catch(() => {
    // 取消删除
  });
};

// 分页相关
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchQuestionsList();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchQuestionsList();
};

// 关闭弹窗
const handleDialogClose = (done) => {
  ElMessageBox.confirm('确认关闭详情弹窗吗？')
    .then(() => {
      done();
    })
    .catch(() => {
      // 取消关闭
    });
};

// 监听搜索关键词变化
watch(searchKeyword, (newVal) => {
  // 当搜索词清空时，如果有分页，重置到第一页
  if (!newVal.trim() && currentPage.value > 1) {
    currentPage.value = 1;
  }
});

// 页面加载时初始化数据
onMounted(async () => {
  await fetchTopicInfo();
  await fetchQuestionsList();
});
</script>

<style scoped>
/* 基础容器优化 */
.full-height {
  height: 100vh;
  overflow: hidden;
  background-color: #f0f2f5; /* 略微加深底色，衬托白色卡片 */
}

/* 顶部导航栏 - 引入磨砂玻璃质感 */
.app-header {
  background: rgba(133, 165, 239, 0.95);
  backdrop-filter: blur(10px); /* 现代感核心：背景模糊 */
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 32px; /* 增加内边距，更有呼吸感 */
}

.bread-crumb {
  font-size: 14px;
}

.bread-crumb :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.7) !important;
  transition: color 0.3s;
}

.bread-crumb :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #ffffff !important;
  font-weight: 600;
}

/* 按钮精细化设计 */
.add-topic-btn {
  background: #ffffff !important;
  color: #90aef3 !important;
  border-radius: 8px !important;
  padding: 10px 20px !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.back-btn {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(4px);
}

/* 主内容区优化 */
.main-content {
  padding: 32px;
  height: calc(100vh - 64px);
  width: 100%;
  box-sizing: border-box;
  overflow-y: overlay; /* 现代浏览器滚动条不占位 */
}

/* 信息卡片 - 采用 Bento Grid 风格 */
.info-card {
  background: #ffffff;
  border-radius: 16px; /* 更圆润的圆角 */
  border: 1px solid rgba(235, 238, 245, 1);
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.05);
  margin-bottom: 24px;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f2f3f5;
}

.card-title {
  font-size: 18px; /* 标题加粗加大 */
  letter-spacing: -0.5px;
}

/* 题目表格样式升级 */
.questions-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 8px; /* 给内部表格留出一点呼吸空间 */
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.05);
}

.custom-table {
  border: none !important;
}

.header-row {
  background: #f8fafc;
  border-radius: 12px; /* 表头圆角化 */
  margin-bottom: 8px;
}

.header-cell {
  color: #4e5969;
  font-weight: 700;
  text-transform: uppercase; /* 增强表头辨识度 */
  letter-spacing: 0.5px;
}

.body-row {
  margin: 4px 0;
  border-radius: 12px; /* 每一行都独立圆角化 */
  border: 1px solid transparent;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.body-row:hover {
  background: #ffffff !important;
  border-color: #6389e1; /* 悬浮时描边 */
  transform: translateY(-2px); /* 轻微浮起 */
  box-shadow: 0 10px 20px rgba(22, 93, 255, 0.08);
  z-index: 1;
}

.question-content {
  color: #1d2129;
  font-weight: 500;
  line-height: 1.6;
}

/* 按钮样式重塑 */
.el-button {
  border-radius: 8px; /* 全局圆角统一 */
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-btn {
  background: #f2f3f5 !important;
  color: #4e5969 !important;
}

.view-btn:hover {
  background: #e5e6eb !important;
  color: #1d2129 !important;
}

/* 详情弹窗样式精修 */
.question-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.answer-content {
  background-color: #f0fff4 !important;
  border: 1px solid #b7eb8f !important;
  color: #1b8d4e !important; /* 加深对比度提升可读性 */
  border-radius: 12px !important;
}

.analysis-wrapper {
  background-color: #f0f7ff !important;
  border: 1px solid #adc6ff !important;
  border-radius: 12px !important;
}

/* 空状态美化 */
.empty-state {
  padding: 120px 0;
}

.empty-icon-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #e5e9f0 100%);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}

/* 分页器精简化 */
.pagination :deep(.el-pager li) {
  border-radius: 6px;
  margin: 0 4px;
  background: #f4f4f5;
}

.pagination :deep(.el-pager li.is-active) {
  background: #7191db !important;
  color: #fff !important;
}

/* 响应式微调 */
@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .header-wrapper {
    padding: 0 16px;
  }
}
</style>
