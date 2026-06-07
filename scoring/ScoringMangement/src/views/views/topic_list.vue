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
            type="primary"
            @click="gotoAddTopic"
            :disabled="!topicInfo.Question_number"
            class="add-topic-btn"
            icon="el-icon-plus"
          >
            添加题目
          </el-button>
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
              <span class="info-label">所属年份</span>
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
                  <el-button
                      style="width: 50px"
                    size="small"
                    type="primary"
                    @click.stop="editTopic(item)"
                    class="edit-btn"
                  >编辑
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click.stop="handleDelete(item)"
                    class="delete-btn"
                  >删除</el-button>
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
      <div v-if="['单项选择题', '多项选择题'].includes(topicInfo.question_type)" class="question-content-container">
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


      <div v-else-if="['案例分析题', '计算分析题', '综合题'].includes(topicInfo.question_type)" class="question-content-container">
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
  const type1 = topicInfo.value.question_type;
  switch (topicInfo.value.question_type) {
    case '单项选择题':
    case '多项选择题':
      router.push({ name: 'add_topic', params: { bankId, type1} });
      break;
    case '判断题':
      router.push({ name: 'add_judge_topic', params: { bankId } });
      break;
    case '计算分析题':
    case '案例分析题':
    case '综合题':
      router.push({ name: 'add_short_topic', params: { bankId } });
      break;
    default:
      ElMessage.warning('未识别的题目类型');
  }
};


// 返回题库列表
const handleBack = () => {
  if (localStorage.getItem('role') === 'teacher') {
  router.push("/main");}
  else {
    router.push("/main");
  }
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
    case '单项选择题':
    case '多项选择题':
      router.push({
        name: 'topic_modify',
        params: { bankId, id: item.topic_number,type: topicInfo.value.question_type}

      });
      break;
    case '判断题':
      router.push({
        name: 'edit_judge_topic',
        params: { bankId, id: item.topic_number }
      });
      break;
    case '计算分析题':
    case '案例分析题':
    case '综合题':
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
.full-height {
  height: 100vh;
  overflow: hidden;
  background-color: #f5f7fa;
}

/* 顶部导航栏样式 */
.app-header {
  background: linear-gradient(135deg, #9db2e2 0%, #567de8 100%);
  border-bottom: none;
  padding: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.bread-crumb {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;

  .el-breadcrumb__item:last-child .el-breadcrumb__inner {
    color: #fff;
    font-weight: 500;
  }

  .el-breadcrumb__separator {
    color: rgba(255, 255, 255, 0.7);
    margin: 0 8px;
  }
}

.header-actions {
  display: flex;
  gap: 12px;
}

.add-topic-btn {
  transition: all 0.3s ease;
  background-color: white;
  color: #8ba9ed;
  border: none;
  font-weight: 500;

  &:hover {
    background-color: #f0f7ff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgb(170, 175, 230);
  }

  &:disabled {
    background-color: #f5f7fa;
    color: #c0c4cc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
}

.back-btn {
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;

  &:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
}

/* 主内容区样式 - 关键修改：让中间内容覆盖整个屏幕 */
.main-content {
  padding: 24px;
  overflow: auto;
  background-color: #f5f7fa;
  height: calc(100vh - 64px); /* 减去顶部导航栏高度 */
  width: 100vw; /* 宽度占满整个视口 */
  margin: 0; /* 移除自动外边距 */
  box-sizing: border-box;
  position: relative; /* 确保内容正确定位 */
}

/* 加载状态样式 */
.loading-container {
  .el-loading-spinner {
    font-size: 24px;
  }

  .el-loading-text {
    margin-top: 16px;
    font-size: 16px;
    color: #666;
  }
}

/* 信息卡片样式 */
.info-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: none;
  overflow: hidden;
  margin-bottom: 24px;
}

.mb-4 {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin: 0;
}

.status-badge {
  .el-tag {
    font-size: 12px;
    padding: 3px 8px;
  }
}

.info-row {
  padding: 16px 20px 4px;
}

.info-col {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  color: #86909c;
  font-size: 12px;
  margin-bottom: 4px;
  font-weight: 500;
}

.info-value {
  color: #1d2129;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.5;
}

.count-badge {
  color: #658eed;
  font-weight: 600;
}

/* 题目列表卡片样式 */
.questions-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: none;
  overflow: hidden;
}

.total-count {
  color: #86909c;
  font-size: 14px;

  .count {
    color: #5e83d8;
    font-weight: 600;
    margin: 0 4px;
  }
}

/* 表格样式 */
.custom-table {
  width: 100%;
  overflow-x: auto;
  border-radius: 8px;
}

.table-header {
  background-color: #f5f7fa;
  border: 1px solid #e5e6eb;
  border-bottom: none;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.header-row {
  display: flex;
  align-items: center;
  height: 56px;
}

.header-cell {
  padding: 0 16px;
  box-sizing: border-box;
  color: #4e5969;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid #e5e6eb;

  &:last-child {
    border-right: none;
  }
}

.table-body {
  border: 1px solid #e5e6eb;
  border-top: none;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  background-color: white;
}

.body-row {
  display: flex;
  align-items: center;
  min-height: 80px;
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.2s ease;

  &:last-child {
    border-bottom: none;
  }
}

.row-hover {
  background-color: #f5faff;
}

.row-active {
  background-color: #e8f3ff;
}

.body-cell {
  padding: 12px 16px;
  box-sizing: border-box;
  color: #1d2129;
  font-size: 14px;
  white-space: normal;
  line-height: 1.5;
  border-right: 1px solid #f0f0f0;

  &:last-child {
    border-right: none;
  }
}

.question-content {
  margin-bottom: 6px;
  font-weight: 500;
  line-height: 1.5;
  color: #444;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.highlight {
  color: #82a0e4;
  font-weight: 600;
  background-color: rgba(22, 93, 255, 0.1);
  padding: 0 2px;
  border-radius: 2px;
}

/* 按钮组样式 */
.btn-group {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  opacity: 0.9;
  transition: opacity 0.3s ease;
}

.body-row:hover .btn-group {
  opacity: 1;
}

.view-btn {
  color: #4e5969;
  background-color: #f2f3f5;
  border-color: #e5e6eb;
  transition: all 0.3s ease;

  &:hover {
    background-color: #e5e6eb;
    color: #1d2129;
    transform: translateY(-1px);
  }
}

.edit-btn {
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(168, 151, 244, 0.3);
  }
}

.el-button {
  border-radius: 4px;
  font-size: 14px;
  padding: 8px 16px;
  transition: none;
  border: none;
  box-shadow: none;
}

/* 修改按钮样式 - 蓝色 */
.edit-btn,
.add-topic-btn,
.el-button--primary {
  background-color: #ffffff;
  color: #7f9cdf;
  border: 1px solid #6d95f1;
}

.edit-btn:hover,
.add-topic-btn:hover,
.el-button--primary:hover {
  background-color: #f0f7ff;
  color: #809fe6;
  border-color: #7a9ded;
}

/* 删除按钮样式 - 红色 */
.delete-btn,
.el-button--danger {
  background-color: #ffffff;
  color: #eaa5a5;
  border: 1px solid #dfb0b0;
}

.delete-btn:hover,
.el-button--danger:hover {
  background-color: #fff5f5;
  color: #e29f9f;
  border-color: #f6a5a5;
}

/* 小按钮样式调整 */
.el-button--small {
  padding: 4px 12px;
  font-size: 12px;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #86909c;
  text-align: center;
}

.empty-icon-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-icon {
  font-size: 40px;
  color: #c9cdD4;
}

.empty-text {
  font-size: 16px;
  color: #4e5969;
  margin-bottom: 8px;
  font-weight: 500;
}

.empty-subtext {
  font-size: 14px;
  color: #86909c;
  margin-bottom: 24px;
  max-width: 300px;
}

.empty-add-btn {
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(168, 178, 239, 0.2);
  }
}

/* 分页样式 */
.pagination {
  margin-top: 24px;
  padding: 16px 0;
  display: flex;
  justify-content: center;

  .el-pagination__sizes {
    margin-right: 16px;
  }

  .el-pagination__total {
    margin-right: 16px;
    color: #86909c;
  }
}

/* 题目详情弹窗样式 */
.question-dialog {
  .el-dialog__header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0f0f0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: #1d2129;
    }
  }

  .el-dialog__body {
    padding: 24px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;
  }
}

.question-type-badge {
  margin-bottom: 16px;
}

.question-content-container {
  margin-top: 16px;
}

.detail-descriptions {
  .el-descriptions__header {
    font-size: 16px;
    color: #1d2129;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .el-descriptions__row {
    border-bottom: 1px dashed #f0f0f0;

    &:last-child {
      border-bottom: none;
    }
  }

  .el-descriptions__label {
    width: 100px;
    font-weight: 600;
    color: #4e5969;
    background-color: #f5f7fa;
  }

  .el-descriptions__content {
    padding-left: 16px;
    color: #1d2129;
  }
}

.content-item {
  padding: 12px 0;
}

.content-wrapper {
  line-height: 1.8;
  white-space: pre-line;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  line-height: 1.8;
}

.option-label {
  font-weight: 600;
  color: #7da1f3;
  min-width: 24px;
}

.option-content {
  flex: 1;
  white-space: pre-line;
}

.answer-wrapper {
  line-height: 1.8;
}

.answer-content {
  white-space: pre-line;
  background-color: #f0fff4;
  border: 1px solid #c9e7d0;
  border-radius: 4px;
  padding: 12px;
  color: #27ae60;
}

.analysis-wrapper {
  line-height: 1.8;
  white-space: pre-line;
  background-color: #f0f7ff;
  border: 1px solid #bed6ff;
  border-radius: 4px;
  padding: 12px;
  color: #7d9eea;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .search-input {
    width: 240px;

    &:focus-within {
      width: 300px;
    }
  }
}

@media (max-width: 992px) {
  .main-content {
    padding: 16px;
  }

  .search-input {
    width: 100%;

    &:focus-within {
      width: 100%;
    }
  }

  .info-col {
    margin-bottom: 12px;
  }
}

@media (max-width: 768px) {
  .header-wrapper {
    padding: 0 12px;
  }

  .app-title {
    font-size: 1rem;
  }

  .header-actions {
    gap: 8px;
  }

  .el-button span {
    display: none;
  }

  .el-button {
    width: 36px;
    height: 36px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-header {
    padding: 12px 16px;
  }

  .card-title {
    font-size: 14px;
  }

  .header-cell, .body-cell {
    padding: 0 8px;
    font-size: 12px;
  }

  .question-dialog {
    width: 95% !important;
  }
}

@media (max-width: 480px) {
  .question-content {
    -webkit-line-clamp: 1;
  }

  .btn-group {
    gap: 4px;
  }

  .pagination {
    .el-pagination__total,
    .el-pagination__sizes {
      display: none;
    }
  }
}
</style>
