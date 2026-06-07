<template>
  <el-container class="full-height">
    <el-header class="app-header">
      <div class="header-wrapper">
        <div class="app-title" @click="goBack">
          <i class="el-icon-book-reader mr-2"></i>
          <span>题库管理系统</span>
        </div>
        <div class="header-right">
          <el-button type="primary" plain size="small" icon="el-icon-back" @click="goBack">返回主页</el-button>
        </div>
      </div>
    </el-header>

    <el-container class="main-container">
      <el-main class="main-content">

        <div class="stats-overview">
          <div class="stat-mini-card">
            <div class="stat-mini-icon blue-deep"><i class="el-icon-folder-opened"></i></div>
            <div class="stat-mini-info">
              <span class="label">题库总数</span>
              <span class="value">{{ tableData.length }}</span>
            </div>
          </div>
          <div class="stat-mini-card">
            <div class="stat-mini-icon blue-mid"><i class="el-icon-eye"></i></div>
            <div class="stat-mini-info">
              <span class="label">公开题库</span>
              <span class="value">{{ publicCount }}</span>
            </div>
          </div>
          <div class="stat-mini-card">
            <div class="stat-mini-icon blue-light"><i class="el-icon-check-circle"></i></div>
            <div class="stat-mini-info">
              <span class="label">已提交</span>
              <span class="value">{{ submittedCount }}</span>
            </div>
          </div>
          <div class="stat-mini-card">
            <div class="stat-mini-icon blue-grey"><i class="el-icon-list"></i></div>
            <div class="stat-mini-info">
              <span class="label">总题数</span>
              <span class="value">{{ totalQuestions }}</span>
            </div>
          </div>
        </div>

        <div class="toolbar-wrapper">
          <div class="action-group">
            <el-button type="primary" @click="showAddDialog" icon="el-icon-plus" class="main-add-btn">添加题库</el-button>

            <el-button @click="grade" icon="el-icon-date" class="white-btn">年份管理</el-button>
            <el-button @click="subject" icon="el-icon-collection" class="white-btn">科目管理</el-button>
          </div>

          <div class="filter-group">
            <el-select v-model="QueryForm.grade_id" placeholder="年份" clearable class="filter-select">
              <el-option label="全部年份" :value="null"></el-option>
              <el-option v-for="grade in grades" :key="grade.id" :label="grade.grade10" :value="grade.id" />
            </el-select>
            <el-select v-model="QueryForm.subject_id" placeholder="科目等级" clearable class="filter-select">
              <el-option label="全部科目" :value="null"></el-option>
              <el-option v-for="subject in subjects" :key="subject.id" :label="subject.subject_name" :value="subject.id" />
            </el-select>
            <el-select v-model="QueryForm.question_type" placeholder="题型" clearable class="filter-select">
              <el-option label="全部题型" :value="null"></el-option>
              <el-option v-for="item in typeList" :key="item" :label="item" :value="item" />
            </el-select>
            <el-select v-model="QueryForm.sorting" placeholder="排序方式" class="filter-select-s">
              <el-option label="升序" :value="null"></el-option>
              <el-option v-for="item in sortings" :key="item" :label="item" :value="item" />
            </el-select>
          </div>
        </div>

        <el-card class="content-card" shadow="never">
          <div class="grid-container">
            <div
              class="bank-card"
              v-for="item in tableData"
              :key="item.Question_number"
              @click="gotoDetail(item)"
            >
              <div class="card-header">
                <span class="subject-tag">{{ item.subject_name }}</span>
                <span class="type-tag">{{ item.question_type }}</span>
              </div>

              <div class="card-body">
                <h3 class="bank-title">{{ item.name }}</h3>
                <div class="bank-info">
                  <div class="info-item">
                    <i class="el-icon-notebook-1"></i>
                    <span>年级：{{ item.grade1_name }}</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-document-copy"></i>
                    <span>题数：{{ item.question_total }} 题</span>
                  </div>
                  <div class="info-item">
                    <i class="el-icon-time"></i>
                    <span>更新：{{ formatTime(item.updated_at).split(' ')[0] }}</span>
                  </div>
                </div>
              </div>

              <div class="card-footer">
                <div class="tags-left">
                  <el-tag size="mini" class="blue-tag">{{ item.status }}</el-tag>
                  <el-tag :type="item.if_public ? '' : 'info'" size="mini" class="status-tag">
                    {{ item.if_public ? '公开' : '私有' }}
                  </el-tag>
                </div>
                <div class="action-buttons">
                  <el-button type="text" size="mini" @click.stop="handleModify(item)" class="edit-link">修改</el-button>
                  <el-button type="text" size="mini" class="del-link" @click.stop="handleDelete(item)">删除</el-button>
                </div>
              </div>
            </div>

            <div v-if="tableData.length === 0" class="empty-state">
              <i class="el-icon-document-delete"></i>
              <p>暂无相关题库数据</p>
              <el-button type="primary" @click="showAddDialog">立即创建</el-button>
            </div>
          </div>

          <div class="pagination-wrapper">
            <el-pagination
              v-if="tableData.length > 0"
              background
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              :page-size="pageSize"
              :current-page="currentPage"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>

    <AddQuestionBankDialog ref="addDialogRef" @refreshList="fetchData"/>
    <ModifyQuestionBank ref="modifyDialogRef" @refreshList="fetchData" topic-id=""/>
    <DeleteDialog ref="deleteDeleteRef" @refreshList="fetchData"/>
  </el-container>
</template>

<script setup>
import { onMounted, reactive, ref, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import AddQuestionBankDialog from './Add.vue';
import DeleteDialog from './delete.vue';
import api from '@/stores/gain';
import dayjs from 'dayjs';
import { ElMessage } from 'element-plus';
import ModifyQuestionBank from './admin_modify.vue';

const router = useRouter();
const route = useRoute();
const activeTab = ref('view-bank');

const formatTime = (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss');

const getStatusTagType = (status) => {
  const types = { '已提交': 'success', '未提交': 'warning', '审核中': 'info', '已拒绝': 'danger' };
  return types[status] || '';
};

const tableData = ref([]);
const grades = ref([]);
const subjects = ref([]);
const typeList = ['单项选择题', '多项选择题', '判断题', '计算分析题', '案例分析题', '综合题'];
const sortings = ['降序'];
const total = ref(0);
const pageSize = ref(10);
const currentPage = ref(1);

const publicCount = computed(() => tableData.value.filter(item => item.if_public).length);
const submittedCount = computed(() => tableData.value.filter(item => item.status === '已提交').length);
const totalQuestions = computed(() => tableData.value.reduce((sum, item) => sum + (item.question_total || 0), 0));

const addDialogRef = ref(null);
const modifyDialogRef = ref(null);
const deleteDeleteRef = ref(null);

const QueryForm = reactive({
  grade_id: '',
  subject_id: '',
  question_type: '',
  sorting: ''
});

const showAddDialog = () => addDialogRef.value.addDialog();
const grade = () => router.push({ name: 'add_grade' });
const subject = () => router.push({ name: 'add_subject' });
const handleModify = (rowData) => modifyDialogRef.value.admin_openDialog(rowData);

const handleDelete = (deleteData) => {
  deleteDeleteRef.value.openDeleteDialog(deleteData, '是否确认删除该题库？', () => {
    fetchData();
    ElMessage.success('题库删除成功');
  });
};

const gotoDetail = (item) => {
  if (!item?.Question_number) return ElMessage.warning('数据不完整');
  router.push({
    name: 'topic_list',
    params: { id: item.Question_number, bankData: JSON.stringify(item) }
  });
};

const goBack = () => router.push("/main");
const handleSizeChange = (val) => { pageSize.value = val; currentPage.value = 1; fetchData(); };
const handleCurrentChange = (val) => { currentPage.value = val; fetchData(); };

const fetchData = () => {
  const params = {
    grade1_id: QueryForm.grade_id,
    subject_id: QueryForm.subject_id,
    question_type: QueryForm.question_type,
    sorting: QueryForm.sorting,
    page: currentPage.value,
    page_size: pageSize.value,
    is_my_bank: activeTab.value === 'my-bank' ? 1 : 0
  };
  const apiUrl = activeTab.value === 'my-bank' ? 'http://localhost:8000/my-questions/' : 'http://localhost:8000/questions/';
  api.fetchData(apiUrl, tableData, '获取题库数据失败', params)
    .then((response) => { total.value = response.total; })
    .catch(() => ElMessage.error('加载题库数据失败'));
};

watch(QueryForm, () => { currentPage.value = 1; fetchData(); }, { deep: true });

onMounted(() => {
  api.fetchData('http://localhost:8000/subjects/', subjects);
  api.fetchData('http://localhost:8000/grades/', grades);
  fetchData();
});
</script>

<style scoped>
/* 1. 基础容器与背景 */
.full-height { height: 100vh; overflow: hidden; background-color: #f4f7fb; }

.app-header {
  background: #ffffff;
  border-bottom: 1px solid #e1eaf5;
  padding: 0 30px;
  height: 64px !important;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 10px rgba(24, 144, 255, 0.05);
}

.header-wrapper { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.app-title { display: flex; align-items: center; font-size: 1.3rem; font-weight: 700; color: #459bea; cursor: pointer; }

/* 2. 统计卡片 - 统一淡蓝色系 */
.stats-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-mini-card {
  background: #ffffff; padding: 18px; border-radius: 12px;
  display: flex; align-items: center; gap: 15px;
  border: 1px solid #e8f1fb; transition: all 0.3s ease;
}
.stat-mini-card:hover { transform: translateY(-3px); border-color: #3999f3; box-shadow: 0 8px 15px rgba(24, 144, 255, 0.08); }

.stat-mini-icon {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.stat-mini-icon.blue-deep  { background: #469ceb; color: #ffffff; }
.stat-mini-icon.blue-mid   { background: #e6f7ff; color: #69b2f6; }
.stat-mini-icon.blue-light { background: #f0f7ff; color: #40a9ff; }
.stat-mini-icon.blue-grey  { background: #f8fafc; color: #64748b; }

.stat-mini-info .label { font-size: 13px; color: #718096; display: block; margin-bottom: 2px; }
.stat-mini-info .value { font-size: 22px; font-weight: 800; color: #2d3748; }

/* 3. 工具栏 - 修正按钮为白色风格 */
.toolbar-wrapper {
  background: #ffffff; padding: 16px 24px; border-radius: 12px;
  margin-bottom: 20px; border: 1px solid #e8f1fb;
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
}

.action-group { display: flex; gap: 12px; }

/* 重点修改：白色按钮样式 */
.white-btn {
  background-color: #ffffff !important;
  color: #4a5568 !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px;
  transition: all 0.2s ease;
}
.white-btn:hover {
  color: #55a5ef !important;
  border-color: #49a0f1 !important;
  background-color: #f0f7ff !important;
}

.filter-group { display: flex; gap: 12px; flex-wrap: wrap; }
.filter-select { width: 140px; }
.filter-select-s { width: 120px; }

/* 4. 网格卡片内容 */
.content-card { border: none; background: transparent; }
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  max-height: calc(100vh - 350px);
  overflow-y: auto;
  padding: 4px;
}

.bank-card {
  background: #ffffff; border-radius: 14px; border: 1px solid #e8f1fb;
  overflow: hidden; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); cursor: pointer;
}
.bank-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(24, 144, 255, 0.12); border-color: #479ae6; }

.card-header {
  padding: 14px 18px; background: #fafdff;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #f0f7ff;
}
.subject-tag { background: #519de4; color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; }
.type-tag { color: #718096; font-size: 12px; font-weight: 500; }

.card-body { padding: 18px; }
.bank-title { font-size: 17px; font-weight: 700; height: 48px; margin: 0 0 12px; line-height: 1.5; color: #1a202c; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.bank-info { display: flex; flex-direction: column; gap: 8px; }
.info-item { font-size: 13px; color: #4a5568; display: flex; align-items: center; gap: 8px; }
.info-item i { color: #47a1f4; font-size: 14px; }

.card-footer {
  padding: 12px 18px; border-top: 1px solid #f0f7ff;
  display: flex; justify-content: space-between; align-items: center;
  background: #ffffff;
}
.blue-tag { background-color: #e6f7ff !important; color: #459ced !important; border-color: #91d5ff !important; }

.edit-link { color: #53a0e8; font-weight: 600; }
.del-link { color: #94a3b8; margin-left: 12px; }
.del-link:hover { color: #eaa0a0; }

/* 5. 分页与空态 */
.pagination-wrapper { display: flex; justify-content: center; padding: 25px 0; background: #fff; border-radius: 12px; border: 1px solid #e8f1fb; }
.empty-state { grid-column: 1 / -1; text-align: center; padding: 60px; color: #a0aec0; }
.empty-state i { font-size: 56px; margin-bottom: 15px; color: #cbd5e0; }

@media (max-width: 1024px) { .stats-overview { grid-template-columns: 1fr 1fr; } .toolbar-wrapper { flex-direction: column; align-items: stretch; } }
</style>
