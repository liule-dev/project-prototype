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
            <i class="el-icon-edit-outline mr-1"></i>我的题库
          </button>
          <button
            class="nav-tab"
            :class="{ 'active': activeTab === 'my-bank' }"
            @click="switchTab('view-bank')"
          >
            <i class="el-icon-edit-outline mr-1"></i>查看题库
          </button>
        </div>

        <div class="template-buttons">
          <el-button
            type="primary"
            @click="showAddDialog"
            class="add-btn"
          >
            <i class="el-icon-plus mr-1"></i>添加题库
          </el-button>
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
                <div class="action-buttons">
                  <el-button
                    type="text"
                    size="mini"
                    @click.stop="handleModify(item)"
                    class="modify-btn"
                  >修改
                    <i class="el-icon-edit"></i>
                  </el-button>
                  <el-button
                    type="text"
                    size="mini"
                    @click.stop="handleDelete(item)"
                    class="delete-btn"
                  >删除
                    <i class="el-icon-delete"></i>
                  </el-button>
                    <el-button
                      type="text"
                      size="mini"
                      @click.stop="getstatus(item)"
                      class="delete-btn"
                      :disabled="item.status === '审核中' || item.status === '正常'"
                    >
                      提交
                      <i class="el-icon-check"></i>
                    </el-button>
                </div>
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
import {useRouter} from 'vue-router';
import AddQuestionBankDialog from './Add.vue';
import ModifyQuestionBank from './modify.vue';

import DeleteDialog from './delete.vue';
import api from '@/stores/gain';
import dayjs from 'dayjs';
import {ElMessageBox} from "element-plus";

// 新增：当前激活的标签页
const activeTab = ref('view-bank');

// 切换标签页
const switchTab = (tabName) => {
  activeTab.value = tabName;
  question_list(); // 保持原有的页面切换逻辑
};

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

const router = useRouter();

// 下拉选择相关
const tableData = ref([]);
const grades = ref([]);
const subjects = ref([]);
const typeList = ['单项选择题', '多项选择题', '判断题', '计算分析题', '案例分析题', '综合题'];
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
  sorting:''
});

// 显示添加弹窗
const showAddDialog = () => {
  addDialogRef.value.addDialog();
};

// 显示修改弹窗
const handleModify = (rowData) => {
  modifyDialogRef.value.openDialog(rowData);
};

const handleDelete = (deleteData) => {
  console.log('准备删除数据:', deleteData);
  deleteDeleteRef.value.openDeleteDialog(deleteData, '是否确认删除该题库？', () => {
    console.log('删除确认，开始刷新数据');
    try {
      fetchData();
      console.log('数据刷新完成');
    } catch (error) {
      console.error('刷新数据失败:', error);
    }
  });
};

const question_list = () => {
  router.push({
    name: 'view_question',
  });
}

// 进入题库详情页
const gotoDetail = (item) => {
  router.push({
    name: 'topic_list',
    params: {
      id: item.Question_number,
      bankData: JSON.stringify(item)
    }
  });
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

const getstatus = (item) => {
  ElMessageBox.confirm('确定要提交该题库吗？提交后将进入审核流程。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      // 构造提交URL
      const submitUrl = `http://localhost:8000/questions/${item.Question_number}/`;

      // 更新题库状态为"审核中"
      const requestData = {
        ...item,
        status: '审核中'
      };

      // 调用更新API
      const success = await api.updateQuestionBank(
        submitUrl,
        tableData,
        requestData,
        '提交失败'
      );

      if (success) {
        ElMessage.success('提交成功，题库已进入审核流程');
        // 刷新数据
        fetchData();
      }
    } catch (error) {
      console.error('提交失败:', error);
      ElMessage.error('提交失败');
    }
  }).catch(() => {
    // 用户取消操作
    ElMessage.info('已取消提交');
  });
};
// 初始化加载数据
const fetchData = () => {
  const params = {
    grade1_id: QueryForm.grade_id,
    subject_id: QueryForm.subject_id,
    question_type: QueryForm.question_type,
    sorting: QueryForm.sorting,
    users:true,
    page: currentPage.value,
    page_size: pageSize.value
  };
  api.fetchData('http://localhost:8000/questions/', tableData, '获取题库数据失败', params)
      .then((response) => {
        total.value = response.total;
      })
      .catch((error) => {
        console.error(error);
      });
};

// 监听QueryForm的变化，自动刷新数据
watch(QueryForm, () => {
  currentPage.value = 1;
  fetchData();
}, {deep: true});

onMounted(() => {
  api.fetchData('http://localhost:8000/subjects/', subjects, '获取学科失败');
  api.fetchData('http://localhost:8000/grades/', grades, '获取年级失败');
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
/* 基础容器 */
.full-height {
  height: 100vh;
  background-color: #f4f7fa; /* 更高级的灰底色 */
  overflow: hidden;
}

/* --- 顶部导航栏美化 --- */
.app-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px); /* 玻璃拟态 */
  border-bottom: 1px solid rgba(24, 144, 255, 0.1);
  padding: 0;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.header-wrapper {
  display: flex;
  align-items: center;
  height: 70px; /* 稍微缩小高度更精致 */
  padding: 0 30px;
  gap: 25px;
}

.app-title {
  font-weight: 800;
  font-size: 1.4rem;
  background: linear-gradient(135deg, #98bfe2 0%, #69a3ea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 导航切换按钮组 */
.nav-tabs {
  display: flex;
  background-color: #f0f2f5;
  border-radius: 12px;
  padding: 4px;
  border: 1px solid #e8e8e8;
}

.nav-tab {
  padding: 8px 24px;
  border: none;
  color: #595959;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: transparent;
}

.nav-tab.active {
  background-color: #fff;
  color: #60b0fa;
  box-shadow: 0 4px 10px rgba(131, 155, 230, 0.15);
}

.nav-tab:not(.active):hover {
  background-color: rgba(24, 144, 255, 0.05);
  color: #59a9f3;
}

/* 筛选器样式 */
.custom-select {
  width: 130px;
  transition: all 0.3s;
}

.custom-select :deep(.el-input__wrapper) {
  background-color: #f9fafb;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e5e7eb inset !important;
}

.custom-select :deep(.el-input__wrapper):hover {
  box-shadow: 0 0 0 1px #66a8e6 inset !important;
}

/* --- 统计卡片区 --- */
.stats-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 25px;
  background-color: #fff;
}

.stat-card {
  padding: 20px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 54px;
  height: 54px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 800;
  line-height: 1;
  color: #1f1f1f;
}

.stat-desc {
  font-size: 0.85rem;
  color: #8c8c8c;
  margin-top: 6px;
}

/* --- 题库格点卡片 --- */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  padding: 25px;
  overflow-y: auto;
  max-height: calc(100vh - 350px);
  scrollbar-width: thin;
  scrollbar-color: #e8e8e8 transparent;
}

.bank-card {
  background: #fff;
  border-radius: 20px;
  border: 1px solid #f0f0f0;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.bank-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(24, 144, 255, 0.12);
  border-color: #bae7ff;
}

.card-header {
  padding: 16px 20px;
  background: #fafafa;
  display: flex;
  gap: 10px;
}

.subject-tag {
  background: #e6f7ff;
  color: #60aaef;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.type-tag {
  background: #f6ffed;
  color: #52c41a;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
}

.card-body {
  padding: 20px;
  flex-grow: 1;
}

.bank-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #262626;
  margin-bottom: 15px;
  line-height: 1.4;
}

.bank-info {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  color: #595959;
}

.info-item i {
  color: #bfbfbf;
  margin-right: 10px;
  font-size: 1rem;
}

/* 卡片底部按钮区 */
.card-footer {
  padding: 15px 20px;
  background: #fff;
  border-top: 1px dashed #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.action-buttons .el-button {
  margin: 0;
  padding: 4px 8px;
  font-weight: 600;
}

.modify-btn:hover { color: #6badea; background: #e6f7ff; border-radius: 6px; }
.delete-btn:hover { color: #f19b9c; background: #fff1f0; border-radius: 6px; }

/* 状态标签美化 */
.status-tag, .public-tag {
  border: none;
  font-weight: 600;
  border-radius: 6px;
}

/* 分页美化 */
.pagination {
  margin-top: 20px;
  padding: 20px;
  justify-content: flex-end;
  background: #fff;
  border-radius: 0 0 16px 16px;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 100px 0;
}

.empty-state i {
  font-size: 4rem;
  color: #f0f0f0;
  margin-bottom: 15px;
}

/* 针对大屏幕的微调 */
@media (min-width: 1600px) {
  .grid-container {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 响应式适配 */
@media (max-width: 768px) {
  .header-wrapper { height: auto; padding: 20px; flex-direction: column; align-items: flex-start; }
  .template-buttons { width: 100%; justify-content: space-between; }
  .stats-container { grid-template-columns: repeat(2, 1fr); }
  .grid-container { grid-template-columns: 1fr; }
}
</style>
