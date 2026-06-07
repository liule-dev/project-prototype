<template>
  <el-container class="full-height">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-wrapper">
        <div class="app-title"></div>
      </div>
    </el-header>

    <el-main class="main-content">
      <!-- 题库基本信息卡片 -->


      <!-- 题目列表 -->
      <el-card class="questions-card" v-if="!loading">
        <div slot="header" class="card-header">
          <span></span>
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
          <div class="table-body" style="height: calc(100vh - 400px); overflow-y: auto;">
            <div
              class="body-row"
              v-for="(item) in questions"
              :key="item.topic_number"
              :class="{ 'row-hover': item.isHover }"
              @mouseenter="item.isHover = true"
              @mouseleave="item.isHover = false"
            >
              <div class="body-cell" :style="{ width: '5%' }">{{ item.topic_number}}</div>
              <div class="body-cell" :style="{ width: '50%' }">
                <div class="question-content">{{ item.topic_content }}</div>
              </div>
              <div class="body-cell" :style="{ width: '10%' }">
                <el-tag class="difficulty-tag">{{ item.topic_difficulty || '未设置' }}</el-tag>
              </div>
              <div class="body-cell" :style="{ width: '15%' }">{{ formatTime(item.created_at) }}</div>
              <div class="body-cell" :style="{ width: '15%' }">{{ formatTime(item.updated_at) }}</div>
              <div class="body-cell text-right" :style="{ width: '20%' }">
                <div class="btn-group">
                  <el-button size="small" @click.stop="viewTopic(item)" class="view-btn">查看</el-button>
                </div>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="questions.length === 0" class="empty-state">
              <i class="el-icon-s-data empty-icon"></i>
              <p>当前题库暂无题目</p>
              <el-button type="primary" @click="gotoAddTopic" class="empty-add-btn">添加题目</el-button>
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
        />
      </el-card>
    </el-main>
  </el-container>
<el-dialog
  v-model="dialogVisible"
  :title="dialogTitle"
  width="60%"
  class="question-dialog"
>
  <div v-if="currentQuestion" class="question-detail">
          <!-- 选择题详情（包括单选和多选） -->
      <div v-if="['单项选择题', '多项选择题'].includes(topicInfo.question_type)">
        <el-descriptions title="题目详情" :column="1" border>
          <el-descriptions-item label="题干">{{ currentQuestion.topic_content }}</el-descriptions-item>
          <el-descriptions-item label="选项">
            <div class="options-list">
              <p v-if="currentQuestion.A"><strong>A.</strong> {{ currentQuestion.A }}</p>
              <p v-if="currentQuestion.B"><strong>B.</strong> {{ currentQuestion.B }}</p>
              <p v-if="currentQuestion.C"><strong>C.</strong> {{ currentQuestion.C }}</p>
              <p v-if="currentQuestion.D"><strong>D.</strong> {{ currentQuestion.D }}</p>
              <p v-if="currentQuestion.E"><strong>E.</strong> {{ currentQuestion.E }}</p>
              <p v-if="currentQuestion.F"><strong>F.</strong> {{ currentQuestion.F }}</p>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="正确答案">{{ currentQuestion.topic_answer }}</el-descriptions-item>
          <el-descriptions-item label="难度">{{ currentQuestion.topic_difficulty }}</el-descriptions-item>
          <el-descriptions-item label="知识点">{{ currentQuestion.topic_knowledge }}</el-descriptions-item>
          <el-descriptions-item label="解析">{{ currentQuestion.topic_analysis }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 案例分析题、计算分析题、综合题详情 -->
      <div v-else-if="['案例分析题', '计算分析题', '综合题'].includes(topicInfo.question_type)">
        <el-descriptions title="题目详情" :column="1" border>
          <el-descriptions-item label="题干">{{ currentQuestion.topic_content }}</el-descriptions-item>
          <el-descriptions-item label="答案">{{ currentQuestion.topic_answer }}</el-descriptions-item>
          <el-descriptions-item label="难度">{{ currentQuestion.topic_difficulty }}</el-descriptions-item>
          <el-descriptions-item label="知识点">{{ currentQuestion.topic_knowledge }}</el-descriptions-item>
          <el-descriptions-item label="解析">{{ currentQuestion.topic_analysis }}</el-descriptions-item>
        </el-descriptions>
      </div>
  </div>
</el-dialog>
</template>

<script setup>
import {ref, onMounted} from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '@/stores/gain';
import dayjs from 'dayjs';
import axios from "axios";

// 路由相关
const router = useRouter();

// 数据存储
const questions = ref([]);  // 题目列表
const total = ref(0);       // 题目总数
const loading = ref(true);  // 加载状态
const topicInfo = ref({});


// 时间格式化
const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '未知';
};

const fetchQuestionsList = async () => {

  try {
    const params = {
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

// 分页相关
const pageSize = ref(10);
const currentPage = ref(1);

const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchQuestionsList();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchQuestionsList();
};

// 弹窗相关数据
const dialogVisible = ref(false);
const currentQuestion = ref(null);

// 查看题目详情
const viewTopic = (item) => {
  alert(item)
  alert(item.topic_content)
  currentQuestion.value = item;
  dialogVisible.value = true;
};

// 跳转到添加题目页面
const gotoAddTopic = () => {
  // 根据你的路由配置进行跳转
  router.push({ name: 'add_topic', params: { bankId: 1 } }); // 需要传入合适的bankId
};

// 页面加载时初始化数据
onMounted(async () => {
  await fetchQuestionsList();
});
</script>


<style scoped>
/* 基础容器：改为更清爽的浅灰蓝色调 */
.full-height {
  height: 100vh;
  overflow: hidden;
  background-color: #f1f5f9;
}

/* 顶部导航：从大面积渐变转为精致的深靛蓝 */
.app-header {
  background: #1e293b; /* 深靛蓝：更有专业感 */
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 32px;
  max-width: 1500px;
  margin: 0 auto;
}

.app-title {
  font-weight: 700;
  font-size: 1.25rem;
  color: #f8fafc;
  letter-spacing: -0.5px;
}

/* 主内容区：增加自适应呼吸感 */
.main-content {
  padding: 24px;
  overflow: auto; /* 允许纵向滚动 */
  background-color: transparent;
  height: calc(100vh - 64px);
  max-width: 1500px;
  margin: 0 auto;
  box-sizing: border-box;
}

/* 信息卡片：极简边框化 */
.info-card {
  background-color: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: none; /* 移除阴影，改用边框 */
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: #6f9ce6; /* 悬浮时边框高亮 */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  }
}

.mb-4 {
  margin-bottom: 20px;
}

/* 信息项优化 */
.info-item {
  margin-bottom: 0;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f8fafc;

  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  width: 100px;
  color: #64748b;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #1e293b;
  font-size: 0.95rem;
  font-weight: 600;
  flex: 1;
}

/* 标签：更柔和的背景色 */
.public-tag, .status-tag, .difficulty-tag {
  border: none;
  font-weight: 600;
  padding: 0 10px;
  border-radius: 6px;
  background-color: #f1f5f9;
  color: #475569;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

/* 表格重构：类似 Github 的清单风格 */
.custom-table {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  background-color: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.header-row {
  display: flex;
  align-items: center;
  height: 52px;
}

.header-cell {
  padding: 0 20px;
  color: #64748b;
  font-weight: 700;
  font-size: 0.85rem;
  letter-spacing: 0.025em;
}

.table-body {
  background-color: white;
}

.body-row {
  display: flex;
  align-items: center;
  min-height: 88px;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f8fafc;
  }

  &:last-child {
    border-bottom: none;
  }
}

.body-cell {
  padding: 16px 20px;
  color: #1e293b;
  font-size: 0.95rem;
}

.question-content {
  font-weight: 600;
  color: #0f172a;
  line-height: 1.6;
  margin-bottom: 4px;
}

.small-text {
  font-size: 0.8rem;
  color: #94a3b8;
}

/* 空状态：插画感设计 */
.empty-state {
  padding: 80px 0;
  text-align: center;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 20px;
    color: #e2e8f0;
  }

  p {
    color: #64748b;
    font-weight: 500;
  }
}

/* 分页：圆角极简 */
.pagination {
  margin-top: 32px;
  padding: 20px 0;

  :deep(.el-pager li) {
    background: transparent;
    border: 1px solid #e2e8f0;
    margin: 0 4px;
    border-radius: 6px;
    transition: all 0.2s;

    &.is-active {
      background-color: #76a2eb !important;
      border-color: #97b1dd;
      color: #fff;
    }
  }
}

/* 弹窗：卡片式排版 */
.question-dialog {
  :deep(.el-dialog) {
    border-radius: 16px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  }

  :deep(.el-dialog__header) {
    padding: 24px;
    border-bottom: 1px solid #f1f5f9;
  }

  .el-dialog__body {
    padding: 32px;
  }

  .el-descriptions {
    padding: 16px;
    background-color: #f8fafc;
    border-radius: 12px;

    :deep(.el-descriptions__label) {
      color: #64748b;
      font-weight: 600;
      width: 120px;
    }
  }
}

/* 针对移动端的深层优化 */
@media (max-width: 768px) {
  .header-wrapper { padding: 0 16px; }
  .main-content { padding: 16px; }
  .body-row { min-height: 120px; }
  .header-cell { display: none; } /* 移动端隐藏复杂表头 */
}
</style>
