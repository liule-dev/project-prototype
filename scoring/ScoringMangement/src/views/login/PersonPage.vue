
<script setup>
import {ref, onMounted, computed, reactive} from "vue";
import { Query1API, Query2API, userUpdateAPI} from "@/api1/api1.js";
import { ElMessage } from "element-plus";
import { categoryStore } from "@/stores/stores1.js";
import { Edit, User, Message, Phone, Check, Close } from "@element-plus/icons-vue";

const c = categoryStore();

// 用户信息
const id = ref('');
const role = ref('');
const username = ref('');
const email = ref('');
const phone = ref('');
const class1_id = ref('');
const class1_name = ref('');
const grade1_id = ref('');
const grade1_name = ref('');
const specialty1_id = ref('');
const specialty1_name = ref('');
const avatarUrl = ref('https://picsum.photos/id/1027/200/200');

// 表单数据
const formData = reactive({
  username: '',
  email: '',
  phone: '',
  role: '',
  grade1_name: '',
  specialty1_name: '',
  class1_name: 1
});



const roleTagType = computed(() => {
  const typeMap = {
    'admin': 'danger',
    'teacher': 'primary',
    'student': 'success'
  };
  return typeMap[role.value] || 'info';
});

// 查询用户信息
const user_name = localStorage.getItem('username1');
const QueryUser = async () => {
  try {
    const response = await Query1API('/query/query_user/', user_name);
    id.value = response.id;
    username.value = response.username;
    email.value = response.email;
    phone.value = response.phone;
    role.value = response.role;
    // 班级信息

    if (response.class1 && response.class1.class1) {
      class1_id.value = response.class1.class1.id;
      class1_name.value = response.class1.class1.class_name;
    }

    // 年级信息
    if (response.class1 && response.class1.grade1) {
      grade1_id.value = response.class1.grade1.id;
      grade1_name.value = response.class1.grade1.grade10;
    }

    // 专业信息
    if (response.class1 && response.class1.specialty1) {
      specialty1_id.value = response.class1.specialty1.id;
      specialty1_name.value = response.class1.specialty1.specialty10;
    }

    // 更新表单数据
    formData.username = username.value;
    formData.email = email.value;
    formData.phone = phone.value;
    formData.role = role.value;
    if (response.class1 === ''){
      class1_id.value = '';
      class1_name.value = '';
      grade1_id.value = '';
    }
    formData.class1_name = class1_id.value;
    formData.grade1_name = grade1_id.value;
    formData.specialty1_name = specialty1_id.value;
  } catch (error) {
    ElMessage.error('查询失败，请稍后重试');
    console.error(error);
  }
};



// 保存修改的方法
const handleSave = async () => {
  try {
  // 这里编写保存修改的逻辑，比如提交表单数据到后端
    const res = await userUpdateAPI('/student/user_update/', formData);
    // 可添加接口请求等逻辑，示例中用消息提示模拟
    ElMessage.success('操作'+ res.message);
    await QueryUser();
  } catch (error) {
    ElMessage.error('操作失败，请稍后重试');
    await QueryUser();
  }
};

// 取消的方法
const handleCancel = async () => {
  // 这里编写取消的逻辑，比如重置表单、关闭弹窗等
  await QueryUser();
  // 可添加重置表单等逻辑，示例中用消息提示模拟
  ElMessage.info('已取消修改');
};


// 页面加载时获取数据
onMounted(async () => {
  await QueryUser();
  // 获取下拉列表数据
  try {
    const classData = await Query2API('/query/query_class/');
    const classnameData = await Query2API('/query/query_classname/');
    const gradeData = await Query2API('/query/query_grade/');
    const specialtyData = await Query2API('/query/query_specialty/');
    c.classnames=[]
    c.grades=[]
    c.specialties=[]
    await c.addClass(classData);
    await c.addClassName(classnameData);
    await c.addGrade(gradeData);
    await c.addSpecialty(specialtyData);

  } catch (error) {
    ElMessage.error('加载数据失败');
    console.error(error);
  }
});

const clearClass = async () => {
  formData.class1_name = '';
  formData.grade1_name = '';
  formData.specialty1_name = '';
  class1_id.value =1;
  class1_name.value = '';
  grade1_id.value = '';
}
</script>

<template>
  <div class="personal-center-container">
    <!-- 顶部信息卡片 -->
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-container">
          <el-avatar :src="avatarUrl" size="large" class="avatar">
            <span class="avatar-text">{{ formData.username.substring(0, 1) }}</span>
          </el-avatar>
          <div class="avatar-actions">
            <el-button size="small" type="primary" class="edit-btn">
              <el-icon><Edit /></el-icon> 编辑资料
            </el-button>
          </div>
        </div>

        <div class="user-info">
          <h2 class="username">{{ formData.username }}</h2>
          <div class="user-role">
            <el-tag :type="roleTagType" class="role-tag">{{ role }}</el-tag>
          </div>
          <div class="user-details">
            <div class="detail-item">
              <el-icon class="detail-icon"><Message /></el-icon>
              <span class="detail-label">邮箱：</span>
              <span class="detail-value">{{ formData.email|| '未设置' }}</span>
            </div>
            <div class="detail-item">
              <el-icon class="detail-icon"><Phone /></el-icon>
              <span class="detail-label">手机：</span>
              <span class="detail-value">{{ formData.phone || '未设置' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 个人资料表单 -->
    <div class="profile-form-card">
      <div class="card-title">
        <el-icon class="title-icon"><User /></el-icon>
        <h3>个人资料</h3>
      </div>

      <el-form :v-model="formData" label-width="120px" class="profile-form">
        <el-form-item label="用户名" disabled>
          <el-input v-model="formData.username" disabled class="form-input" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="formData.email" class="form-input" />
        </el-form-item>

        <el-form-item label="手机号">
          <el-input v-model="formData.phone" class="form-input" />
        </el-form-item>

        <el-form-item label="角色" disabled>
          <el-input v-model="formData.role" disabled class="form-input" />
        </el-form-item>

        <el-form-item label="年级">
          <el-select v-model="formData.grade1_name" placeholder="选择年级" class="form-select">
            <el-option
              v-for="grade in c.grades"
              :key="grade.id"
              :label="grade.grade10"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="专业">
          <el-select v-model="formData.specialty1_name" placeholder="选择专业" class="form-select">
            <el-option
              v-for="spec in c.specialties"
              :key="spec.id"
              :label="spec.specialty10"
              :value="spec.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item class="form-actions">
      <el-button type="primary" class="save-btn" @click="handleSave">
        <el-icon><Check /></el-icon> 保存修改
      </el-button>
      <el-button type="default" class="cancel-btn" @click="handleCancel">
        <el-icon><Close /></el-icon> 取消
      </el-button>
          <el-button v-if="formData.role === 'admin'" type="default" class="cancel-btn" @click="clearClass">
        <el-icon><Close /></el-icon> 清除班级专业年级
      </el-button>
    </el-form-item>
      </el-form>
    </div>
  </div>
</template>
<style scoped>
/* --- 页面背景：更柔和的背景渐变 --- */
.personal-center-container {
  max-width: 100%;
  margin: 0;
  padding: 40px 20px;
  background-color: #f6f8fb; /* 浅灰底色，减轻压力 */
  background-image: radial-gradient(at 0% 0%, rgba(102, 126, 234, 0.05) 0px, transparent 50%),
                    radial-gradient(at 50% 0%, rgba(118, 75, 162, 0.05) 0px, transparent 50%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

/* --- 统一卡片基础样式 --- */
.profile-card,
.profile-form-card {
  width: 100%;
  max-width: 850px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.8);
  transition: transform 0.3s ease;
}

/* --- 顶部信息区 --- */
.profile-card {
  padding: 40px;
  background: linear-gradient(to right, #ffffff, #fcfdff);
  overflow: visible;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 40px;
}

.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 130px;
  height: 130px;
  border: 6px solid #fff;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
  background: #f0f2f5;
}

.avatar-text {
  font-size: 40px;
  font-weight: 800;
  color: #667eea;
}

/* 头像上的编辑按钮 */
.edit-btn {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.edit-btn:hover {
  background: #764ba2;
  transform: rotate(90deg) scale(1.1);
}

.username {
  font-size: 32px;
  font-weight: 800;
  color: #2d3748;
  margin: 0 0 10px 0;
  letter-spacing: -1px;
}

.role-tag {
  background: rgba(102, 126, 234, 0.1) !important;
  color: #667eea !important;
  border: none;
  font-weight: 700;
  padding: 5px 15px;
  border-radius: 8px;
  text-transform: uppercase;
  font-size: 12px;
}

.user-details {
  margin-top: 20px;
  display: flex;
  gap: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #718096;
  background: #f8fafc;
  padding: 8px 16px;
  border-radius: 10px;
}

.detail-icon {
  margin-right: 8px;
  color: #a0aec0;
}

/* --- 表单卡片区 --- */
.profile-form-card {
  padding: 40px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 35px;
}

.title-icon {
  font-size: 24px;
  color: #667eea;
  padding: 10px;
  background: rgba(102, 126, 234, 0.08);
  border-radius: 12px;
}

.card-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
}

/* --- Element Plus 表单重塑 --- */
:deep(.el-form-item) {
  margin-bottom: 25px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #4a5568;
  padding-bottom: 8px;
}

:deep(.el-input__wrapper),
:deep(.el-select .el-input__wrapper) {
  background-color: #fdfdff;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
  border-radius: 12px;
  padding: 5px 15px;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #667eea inset !important;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2), 0 0 0 1px #667eea inset !important;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f7fafc;
  color: #a0aec0;
}

/* --- 底部操作区 --- */
.form-actions {
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #edf2f7;
  display: flex;
  justify-content: flex-start;
  gap: 15px;
}

.save-btn {
  height: 46px;
  padding: 0 30px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.3s;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  opacity: 0.9;
}

.cancel-btn {
  height: 46px;
  padding: 0 25px;
  border-radius: 12px;
  font-weight: 600;
  color: #718096;
  border: 1px solid #e2e8f0;
}

.cancel-btn:hover {
  background-color: #f7fafc;
  color: #2d3748;
  border-color: #cbd5e0;
}

/* --- 响应式适配 --- */
@media (max-width: 768px) {
  .personal-center-container {
    padding: 20px 15px;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .user-details {
    flex-direction: column;
    gap: 10px;
  }

  .form-actions {
    flex-direction: column;
  }

  .save-btn, .cancel-btn {
    width: 100%;
  }
}
</style>
