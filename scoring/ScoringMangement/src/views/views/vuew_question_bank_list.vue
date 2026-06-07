<template>
  <el-container class="full-height">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-wrapper">
        <div class="app-title">
          <i class="el-icon-book-reader mr-2"></i>
          <span>题库管理系统</span>
        </div>

        <!-- 顶部导航菜单 - 美化的切换按钮 -->
        <div class="nav-tabs">
          <button
            class="nav-tab"
            :class="{ 'active': activeTab === 'view-bank' }"
          >
            <i class="el-icon-edit-outline mr-1"></i>查看题库
          </button>
          <button
            class="nav-tab"
            :class="{ 'active': activeTab === 'my-bank' }"
            @click="switchTab('my-bank')"
          >
            <i class="el-icon-edit-outline mr-1"></i>我的题库
          </button>
        </div>

        <div class="template-buttons">
          <el-input
            v-model="QueryForm.teacher_name"
            placeholder="请输入教师名字"
            class="custom-select"
          ></el-input>
          <el-select
            v-model="QueryForm.grade_id"
            placeholder="请选择年份"
            class="custom-select"
          >
            <el-option label="全部" :value="null"></el-option>
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.grade10"
              :value="grade.id"
            />
          </el-select>
          <el-select
            v-model="QueryForm.subject_id"
            placeholder="请选择等级"
            class="custom-select"
          >
            <el-option label="全部" :value="null"></el-option>
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.subject_name"
              :value="subject.id"
            />
          </el-select>
          <el-select
            v-model="QueryForm.question_type"
            placeholder="请选择题型"
            class="custom-select"
          >
            <el-option label="全部" :value="null"></el-option>
            <el-option
              v-for="item in typeList"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
          <el-select
            v-model="QueryForm.sorting"
            placeholder="请选择排序方式"
            class="custom-select"
          >
            <el-option label="升序" :value="null"></el-option>
            <el-option
              v-for="item in sortings"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 中间主要内容 -->
      <el-main class="main-content">
        <el-card class="content-card">
          <!-- 统计卡片区域 -->
          <div class="stats-container">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="el-icon-folder-opened"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ tableData.length }}</div>
                <div class="stat-desc">题库总数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="el-icon-eye"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ publicCount }}</div>
                <div class="stat-desc">公开题库</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="el-icon-check-circle"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ submittedCount }}</div>
                <div class="stat-desc">已提交题库</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="el-icon-list"></i>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ totalQuestions }}</div>
                <div class="stat-desc">总题数</div>
              </div>
            </div>
          </div>

          <!-- 方格卡片区域 -->
          <div class="grid-container">
            <div
              class="bank-card"
              v-for="item in tableData"
              :key="item.Question_number"
              @click="gotoDetail(item)"
            >
              <!-- 卡片头部：学科和题型 -->
              <div class="card-header">
                <span class="subject-tag">{{ item.subject_name }}</span>
                <span class="type-tag">{{ item.question_type }}</span>
              </div>

              <!-- 卡片主体：标题和基本信息 -->
              <div class="card-body">
                <h3 class="bank-title">{{ item.name }}</h3>
                <div class="bank-info">
                  <div class="info-item">
                    <i class="el-icon-book"></i>
                    <span>编号：{{ item.Question_number }}</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-book"></i>
                    <span>创建人：{{ item.creator_name  }}</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-book"></i>
                    <span>年级：{{ item.grade1_name }}</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-list"></i>
                    <span>题数：{{ item.question_total }} 题</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-time"></i>
                    <span>创建时间：{{ formatTime(item.created_at) }}</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-refresh"></i>
                    <span>更新时间：{{ formatTime(item.updated_at) }}</span>
                  </div>
                </div>
              </div>

              <!-- 卡片底部：状态和操作 -->
              <div class="card-footer">
                <el-tag :type="getStatusTagType(item.status)" class="status-tag">
                  {{ item.status }}
                </el-tag>
                <el-tag :type="item.if_public ? 'success' : 'info'" class="public-tag">
                  {{ item.if_public ? '公开' : '私有' }}
                </el-tag>

              </div>
            </div>

            <!-- 空状态显示 -->
            <div v-if="tableData.length === 0" class="empty-state">
              <i class="el-icon-empty"></i>
              <p>暂无题库数据</p>
              <el-button type="primary" @click="showAddDialog">添加题库</el-button>
            </div>
          </div>

          <!-- 分页 -->
          <el-pagination
            v-if="tableData.length > 0"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            :page-size="pageSize"
            :current-page="currentPage"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            class="pagination"
          >
          </el-pagination>
        </el-card>
      </el-main>
    </el-container>

    <!-- 弹窗组件 -->
    <AddQuestionBankDialog ref="addDialogRef" @refreshList="fetchData"/>
    <ModifyQuestionBank ref="modifyDialogRef" @refreshList="fetchData" topic-id=""/>
    <DeleteDialog ref="deleteDeleteRef" @refreshList="fetchData"/>
  </el-container>
</template>

<script setup>
import {onMounted, reactive, ref, watch, computed} from 'vue';
import {useRouter, useRoute} from 'vue-router';
import AddQuestionBankDialog from './Add.vue';
import ModifyQuestionBank from './Modify.vue';
import DeleteDialog from './delete.vue';
import api from '@/stores/gain';
import dayjs from 'dayjs';
import { ElMessage } from 'element-plus';

// 路由相关
const router = useRouter();
const route = useRoute();

// 新增：当前激活的标签页
const activeTab = ref('view-bank');

// 切换标签页并加载对应数据
const switchTab = (tabName) => {
  activeTab.value = tabName;
  question_list();

  // 重置查询条件
  QueryForm.grade_id = '';
  QueryForm.subject_id = '';
  QueryForm.question_type = '';
  QueryForm.sorting = '';

  // 根据不同标签页加载不同数据
  fetchData();
};
const question_list = () => {
  router.push({
    name: 'QuestionBankList',
  });
}
// 时间格式化函数
const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

// 根据状态获取标签类型
const getStatusTagType = (status) => {
  switch(status) {
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

// 下拉选择相关
const tableData = ref([]);
const grades = ref([]);
const subjects = ref([]);
const typeList = ['选择题', '填空题', '判断题', '计算题'];
const sortings = ['降序']
// 分页相关
const total = ref(0);
const pageSize = ref(10);
const currentPage = ref(1);

// 统计数据
const publicCount = computed(() => {
  return tableData.value.filter(item => item.if_public).length;
});

const submittedCount = computed(() => {
  return tableData.value.filter(item => item.status === '已提交').length;
});

const totalQuestions = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (item.question_total || 0), 0);
});

// 弹窗相关
const addDialogRef = ref(null);
const modifyDialogRef = ref(null);
const deleteDeleteRef = ref(null);

const QueryForm = reactive({
  grade_id: '',
  subject_id: '',
  question_type: '',
  sorting:'',
  teacher_name:''
});

// 显示添加弹窗
const showAddDialog = () => {
  addDialogRef.value.addDialog();
};

// 显示修改弹窗
const handleModify = (rowData) => {
  modifyDialogRef.value.openDialog(rowData);
};

// 处理删除操作
const handleDelete = (deleteData) => {
  console.log('准备删除数据:', deleteData);
  deleteDeleteRef.value.openDeleteDialog(deleteData, '是否确认删除该题库？', () => {
    console.log('删除确认，开始刷新数据');
    try {
      fetchData();
      ElMessage.success('题库删除成功');
      console.log('数据刷新完成');
    } catch (error) {
      ElMessage.error('删除后刷新数据失败');
      console.error('刷新数据失败:', error);
    }
  });
};

// 跳转到题目列表页
const goToQuestionList = () => {
  router.push({
    name: 'view_question',
  }).catch(err => {
    console.error('跳转至题目列表页失败:', err);
    ElMessage.error('页面跳转失败，请重试');
  });
};

// 跳转到题库查看页
const gotoViewTopic = () => {
  router.push({
    name: 'vuew_topic'
  }).catch(err => {
    console.error('跳转至题库查看页失败:', err);
    ElMessage.error('页面跳转失败，请重试');
  });
};

// 进入题库详情页
const gotoDetail = (item) => {
  if (!item || !item.Question_number) {
    ElMessage.warning('题库数据不完整，无法查看详情');
    return;
  }

  router.push({
    name: 'view_topic',
    params: {
      id: item.Question_number,
      bankData: JSON.stringify(item)
    }
  }).catch(err => {
    console.error('跳转至题库详情页失败:', err);
    ElMessage.error('查看详情失败，请重试');
  });
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 分页处理函数
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  fetchData();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchData();
};

// 初始化加载数据
const fetchData = () => {
  // 根据当前标签页设置不同的查询参数
  const params = {
    grade1_id: QueryForm.grade_id,
    subject_id: QueryForm.subject_id,
    question_type: QueryForm.question_type,
    sorting: QueryForm.sorting,
    page: currentPage.value,
    page_size: pageSize.value,
    // 区分"查看题库"和"我的题库"
    is_my_bank: activeTab.value === 'my-bank' ? 1 : 0,
    publicks:1,
    teacher_name:QueryForm.teacher_name
  };

  // 根据标签页选择不同的API端点
  const apiUrl = activeTab.value === 'my-bank'
    ? 'http://localhost:8000/my-questions/'
    : 'http://localhost:8000/questions/';

  api.fetchData(apiUrl, tableData, '获取题库数据失败', params)
      .then((response) => {
        total.value = response.total;
      })
      .catch((error) => {
        ElMessage.error('加载题库数据失败');
      });
};

// 监听QueryForm的变化，自动刷新数据
watch(QueryForm, () => {
  currentPage.value = 1;
  fetchData();
}, {deep: true});

// 监听路由变化，同步标签页状态
watch(() => route.name, (newName) => {
  if (newName === 'my_bank') {
    activeTab.value = 'my-bank';
  } else if (newName === 'view_bank') {
    activeTab.value = 'view-bank';
  }
  fetchData();
});

onMounted(() => {
  // 加载基础数据
  api.fetchData('http://localhost:8000/subjects/', subjects, '获取学科失败')
    .catch(() => ElMessage.error('加载学科数据失败'));

  api.fetchData('http://localhost:8000/grades/', grades, '获取年级失败')
    .catch(() => ElMessage.error('加载年级数据失败'));

  // 初始化页面数据
  fetchData();
});

// 监听数据变化，添加hover状态
watch(tableData, (newVal) => {
  if (Array.isArray(newVal)) {
    newVal.forEach(item => {
      if (item.isHover === undefined) {
        Object.assign(item, {isHover: false});
      }
    });
  }
}, {deep: true, immediate: true});

</script>
<style scoped>
/* 全局容器：使用更具质感的冷灰色调 */
.full-height {
  height: 100vh;
  overflow: hidden;
  background-color: #f4f7fa;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* 顶部导航：沉浸式深靛蓝 + 磨砂效果 */
.app-header {
  background: rgba(15, 23, 42, 0.9); /* 深色半透明 */
  backdrop-filter: blur(8px); /* 关键：磨砂模糊 */
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 40px;
  max-width: 1600px;
  margin: 0 auto;
}

.app-title {
  font-weight: 800;
  font-size: 1.3rem;
  color: #ffffff;
  letter-spacing: -0.02em;
  background: linear-gradient(to right, #ffffff, #94a3b8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 主内容布局优化 */
.main-content {
  padding: 32px;
  overflow-y: auto;
  height: calc(100vh - 64px);
  max-width: 1600px;
  margin: 0 auto;
  box-sizing: border-box;
  scroll-behavior: smooth;
}

/* 信息卡片：悬浮感与呼吸感 */
.info-card {
  background: #ffffff;
  border-radius: 20px; /* 更大的圆角 */
  border: 1px solid #eef2f6;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.02);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.05);
}

.card-header {
  padding: 24px 28px;
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
}

/* 信息条目：去边框，改用背景区分 */
.info-item {
  padding: 16px 28px;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.info-item:hover {
  background-color: #f8fafc;
}

.info-label {
  width: 110px;
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  color: #334155;
  font-size: 0.95rem;
  font-weight: 600;
}

/* 标签系统：胶囊风格 */
.public-tag, .status-tag, .difficulty-tag {
  border: none;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 99px; /* 胶囊形状 */
  font-size: 0.75rem;
  background-color: #f1f5f9;
}

/* 表格重塑：取消外框，增强行对比 */
.custom-table {
  background: transparent;
  border: none;
}

.table-header {
  background: transparent;
  margin-bottom: 12px;
}

.header-row {
  display: flex;
  align-items: center;
  height: 40px;
  padding: 0 12px;
}

.header-cell {
  color: #64748b;
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
}

/* 每一行都是一个独立的“小卡片” */
.body-row {
  background: #ffffff;
  margin-bottom: 12px; /* 行间距 */
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  min-height: 90px;
  transition: all 0.3s ease;
}

.body-row:hover {
  transform: scale(1.005);
  border-color: #78a5ef;
  box-shadow: 0 12px 24px -10px rgba(59, 130, 246, 0.15);
}

.body-cell {
  padding: 16px 24px;
  font-size: 0.95rem;
}

.question-content {
  font-weight: 700;
  color: #1e293b;
  line-height: 1.6;
  font-size: 1rem;
}

/* 分页组件：极简居中 */
.pagination {
  margin-top: 40px;
  padding: 24px;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #0f172a !important; /* 深色激活态 */
  border-radius: 10px;
  font-weight: 800;
}

:deep(.el-pagination.is-background .el-pager li) {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  color: #64748b;
}

/* 弹窗：大圆角与沉浸式内容 */
.question-dialog :deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.question-dialog :deep(.el-dialog__header) {
  background: #f8fafc;
  padding: 24px 32px;
}

.question-dialog :deep(.el-dialog__body) {
  padding: 32px;
}

/* 针对高分辨率屏幕的优化 */
@media (min-width: 1600px) {
  .main-content {
    padding: 40px 0;
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .header-wrapper { padding: 0 20px; }
  .main-content { padding: 16px; }
  .info-item { padding: 12px 16px; }
  .body-row { border-radius: 12px; margin-bottom: 8px; }
  .header-cell { display: none; }
}
</style>
