<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { manageDeleteAPI, manageUpdateAPI, Query2API, QueryUserAPI } from "@/api1/api1.js";
import { categoryStore } from "@/stores/stores1";

const c = categoryStore();
const loading = ref(false);

// 搜索参数
const searchParams = reactive({
  username: '',
  role: ''
});

// 分页参数
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
});

// 用户列表数据
const userList = ref([]);

// 弹窗控制
const dialogVisible = ref(false);
const dialogTitle = ref('');
const isEdit = ref(true);

// 表单数据
const formData = reactive({
  id: '',
  username: '',
  password: '',
  email: '',
  phone: '',
  role: '',
  grade1_name: '',
  specialty1_name: '',
  class1_name: 1
});

const userForm = ref(null);
const searchForm = ref(null);

onMounted(async () => {
  getUserList();
  try {
    const classnameData = await Query2API('/query/query_classname/');
    const gradeData = await Query2API('/query/query_grade/');
    const specialtyData = await Query2API('/query/query_specialty/');

    c.classnames = [];
    c.grades = [];
    c.specialties = [];
    await c.addClassName(classnameData);
    await c.addGrade(gradeData);
    await c.addSpecialty(specialtyData);
  } catch (error) {
    ElMessage.error('加载基础配置失败');
  }
});

const getUserList = () => {
  loading.value = true;
  try {
    setTimeout(async () => {
      const mockData = await QueryUserAPI('/manage/query_all_user/');
      const filteredData = mockData.filter(user => {
        const matchName = !searchParams.username || user.username.includes(searchParams.username);
        const matchRole = !searchParams.role || user.role === searchParams.role;
        return matchName && matchRole;
      });
      userList.value = filteredData;
      pagination.total = filteredData.length;
      loading.value = false;
    }, 400);
  } catch (error) {
    loading.value = false;
    ElMessage.error('数据获取失败');
  }
};

const handleDialogClose = () => {
  dialogVisible.value = false;
  userForm.value?.resetFields();
};

const formRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ required: true, type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  phone: [{ required: true, pattern: /^1[0-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
});

const openAddDialog = () => {
  dialogTitle.value = '新增系统用户';
  isEdit.value = false;
  Object.keys(formData).forEach(key => formData[key] = '');
  dialogVisible.value = true;
};

const openEditDialog = (row) => {
  dialogTitle.value = '编辑用户信息';
  isEdit.value = true;
  // 数据回显逻辑
  if (row.class1?.class1) formData.class1_name = row.class1.class1.class_name;
  if (row.class1?.specialty1) formData.specialty1_name = row.class1.specialty1.specialty10;
  if (row.class1?.grade1) formData.grade1_name = row.class1.grade1.grade10;

  Object.assign(formData, { ...row, password: '' });
  dialogVisible.value = true;
};

const submitForm = () => {
  userForm.value.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      if (isEdit.value) {
        const index = userList.value.findIndex(item => item.id === formData.id);
        // 保持原ID逻辑
        if (isNaN(Number(formData.grade1_name)) && index !== -1) formData.grade1_name = userList.value[index].class1.grade1.id;
        if (isNaN(Number(formData.class1_name)) && index !== -1) formData.class1_name = userList.value[index].class1.class1.id;
        if (isNaN(Number(formData.specialty1_name)) && index !== -1) formData.specialty1_name = userList.value[index].class1.specialty1.id;

        const res = await manageUpdateAPI('/manage/update_user/', formData);
        ElMessage.success(res.message || '更新成功');
      } else {
        const res = await manageUpdateAPI('/manage/add_user/', formData);
        ElMessage.success('用户创建成功');
      }
      getUserList();
      dialogVisible.value = false;
    } catch (err) {
      ElMessage.error('提交失败，请重试');
    } finally {
      loading.value = false;
    }
  });
};

const handleDelete = (id) => {
  ElMessageBox.confirm('此操作将永久删除该用户，是否继续？', '严重警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error',
    center: true
  }).then(async () => {
    const res = await manageDeleteAPI('/manage/delete_user/', id);
    ElMessage.success('用户已成功移除');
    getUserList();
  });
};

const handlePageChange = (page) => {
  pagination.currentPage = page;
};

const resetSearch = () => {
  searchParams.role = '';
  searchParams.username = '';
  getUserList();
};

const clearClass = () => {
  formData.class1_name = '';
  formData.grade1_name = '';
  formData.specialty1_name = '';
};
</script>

<template>
  <div class="page-container">
    <div class="bg-blobs">
      <div class="blob blob-primary"></div>
      <div class="blob blob-secondary"></div>
    </div>

    <div class="content-layout">
      <header class="glass-header">
        <div class="title-group">
          <div class="icon-box"><i class="fas fa-user-gear"></i></div>
          <div>
            <h1>用户管理</h1>
            <p>系统权限用户管理中心</p>
          </div>
        </div>
        <el-button type="primary" class="add-btn" @click="openAddDialog">
          <i class="fas fa-plus"></i> 新增系统用户
        </el-button>
      </header>

      <section class="glass-card search-card">
        <el-form :inline="true" :model="searchParams" ref="searchForm" class="search-form">
          <el-form-item label="姓名查询">
            <el-input v-model="searchParams.username" placeholder="输入关键字..." clearable />
          </el-form-item>
          <el-form-item label="角色筛选">
            <el-select v-model="searchParams.role" placeholder="全部角色" clearable style="width: 160px">
              <el-option label="管理员" value="admin" />
              <el-option label="教师" value="teacher" />
              <el-option label="学生" value="student" />
            </el-select>
          </el-form-item>
          <el-form-item class="search-btns">
            <el-button type="primary" @click="getUserList" icon="Search">检索</el-button>
            <el-button @click="resetSearch" icon="Refresh">重置</el-button>
          </el-form-item>
        </el-form>
      </section>

      <section class="glass-card table-section">
        <el-table
          :data="userList"
          v-loading="loading"
          class="custom-table"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="username" label="用户名" min-width="120">
            <template #default="{row}">
              <div class="user-info">
                <el-avatar :size="28" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
                <span class="name">{{ row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="权限角色" width="100" align="center">
            <template #default="{row}">
              <el-tag :class="['role-tag', row.role]">{{ row.role === 'admin' ? '管理员' : row.role === 'teacher' ? '教师' : '学员' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="联系方式" min-width="200">
            <template #default="{row}">
              <div class="contact-cell">
                <p><i class="far fa-envelope"></i> {{ row.email }}</p>
                <p><i class="fas fa-mobile-screen-button"></i> {{ row.phone }}</p>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="scope">
              <el-button type="primary" link @click="openEditDialog(scope.row)">编辑</el-button>
              <el-divider direction="vertical" />
              <el-button type="danger" link @click="handleDelete(scope.row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="table-footer">
          <span class="total-info">共检索到 <b>{{ pagination.total }}</b> 位活跃用户</span>
          <el-pagination
            v-model:current-page="pagination.currentPage"
            :page-size="pagination.pageSize"
            layout="prev, pager, next"
            :total="pagination.total"
            @current-change="handlePageChange"
          />
        </div>
      </section>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="560px"
      class="styled-dialog"
      :before-close="handleDialogClose"
    >
      <el-form :model="formData" :rules="formRules" ref="userForm" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户账号" prop="username">
              <el-input v-model="formData.username" placeholder="账户ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="访问角色" prop="role">
              <el-select v-model="formData.role" placeholder="选择权限" style="width: 100%">
                <el-option label="系统管理员" value="admin" />
                <el-option label="教师" value="teacher" />
                <el-option label="学生" value="student" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="安全密码" prop="password">
          <el-input v-model="formData.password" type="password" show-password placeholder="请填写" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="mail@example.com" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="11位手机号码" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="form-divider">学籍归属绑定</div>

        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="年份">
              <el-select v-model="formData.grade1_name" placeholder="请选择">
                <el-option v-for="g in c.grades" :key="g.id" :label="g.grade10" :value="g.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="专业">
              <el-select v-model="formData.specialty1_name" placeholder="请选择">
                <el-option v-for="s in c.specialties" :key="s.id" :label="s.specialty10" :value="s.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="footer-btns">
          <el-button link @click="clearClass" class="clear-link">重置信息</el-button>
          <div class="flex-spacer"></div>
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="submitForm" class="submit-btn">确认提交</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* 核心容器与背景 - 统一蓝紫渐变主题 */
.page-container {
  min-height: 100vh;
  padding: 30px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Inter', -apple-system, sans-serif;
}

.bg-blobs {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
}
.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.25;
  border-radius: 50%;
}
.blob-primary { width: 500px; height: 500px; background: linear-gradient(135deg, #667eea, #764ba2); top: -100px; right: -50px; }
.blob-secondary { width: 400px; height: 400px; background: linear-gradient(135deg, #a3bffa, #c7d2fe); bottom: -100px; left: -50px; }

.content-layout { position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; }

/* 头部样式 - 玻璃态效果 */
.glass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1);
}
.title-group { display: flex; align-items: center; gap: 15px; }
.icon-box {
  width: 50px; height: 50px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 22px;
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
}
.title-group h1 { font-size: 24px; margin: 0; color: #1f2937; font-weight: 700; }
.title-group p { font-size: 14px; color: #6b7280; margin: 4px 0 0; }
.add-btn { 
  padding: 12px 24px; 
  border-radius: 10px; 
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}
.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* 卡片通用 - 玻璃态设计 */
.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.glass-card:hover {
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
}

/* 搜索栏 */
.search-form :deep(.el-form-item__label) { font-weight: 600; color: #4b5563; }
.search-form :deep(.el-input__wrapper) { 
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e5e7eb inset;
  transition: all 0.3s ease;
}
.search-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #a3bffa inset;
}
.search-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2), 0 0 0 1px #667eea inset;
}

/* 表格样式 - 现代化设计 */
.custom-table { 
  border-radius: 12px; 
  background: transparent !important;
  overflow: hidden;
}
.custom-table :deep(.el-table__header th) {
  background: linear-gradient(135deg, #f9fafb, #f3f4f6);
  color: #4b5563;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}
.custom-table :deep(.el-table__body tr) {
  transition: all 0.2s ease;
}
.custom-table :deep(.el-table__body tr:hover) {
  background: rgba(102, 126, 234, 0.05);
}
.user-info { display: flex; align-items: center; gap: 10px; }
.user-info .name { font-weight: 600; color: #1f2937; }

.contact-cell p { margin: 2px 0; font-size: 13px; color: #6b7280; }
.contact-cell i { width: 16px; color: #9ca3af; }

.org-cell { font-size: 13px; color: #4b5563; }
.org-tag { 
  background: rgba(102, 126, 234, 0.1); 
  color: #667eea; 
  padding: 2px 8px; 
  border-radius: 6px; 
  font-weight: 600;
}
.org-split { margin: 0 6px; color: #d1d5db; }

.role-tag { 
  font-weight: 700; 
  border: none; 
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
}
.role-tag.admin { 
  background: linear-gradient(135deg, #fee2e2, #fecaca); 
  color: #dc2626;
}
.role-tag.teacher { 
  background: linear-gradient(135deg, #dcfce7, #bbf7d0); 
  color: #16a34a;
}
.role-tag.student { 
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb); 
  color: #6b7280;
}

.table-footer {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb;
}
.total-info { font-size: 14px; color: #6b7280; }
.total-info b { color: #667eea; font-weight: 700; }

/* 弹窗定制 - 圆角设计 */
.styled-dialog :deep(.el-dialog) { 
  border-radius: 20px; 
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.styled-dialog :deep(.el-dialog__header) { 
  margin-right: 0; 
  padding-bottom: 10px; 
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(135deg, #f0f9ff, #e6f7ff);
}
.styled-dialog :deep(.el-dialog__title) {
  color: #1f2937;
  font-weight: 700;
}
.form-divider {
  margin: 25px 0 15px; 
  font-size: 14px; 
  font-weight: 700; 
  color: #667eea;
  display: flex; align-items: center;
}
.form-divider::after { content: ''; flex: 1; height: 1px; background: linear-gradient(to right, #e5e7eb, transparent); margin-left: 10px; }

.footer-btns { display: flex; align-items: center; gap: 12px; }
.flex-spacer { flex: 1; }
.clear-link { color: #9ca3af; font-size: 13px; transition: all 0.3s ease; }
.clear-link:hover { color: #ef4444; }
.submit-btn { 
  padding: 10px 30px; 
  border-radius: 10px; 
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}
.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.el-table__row) { transition: 0.2s; }
:deep(.el-table__row:hover) { transform: scale(1.002); cursor: default; }

/* 按钮样式统一 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
}
:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}
</style>
