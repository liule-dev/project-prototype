<script setup>
import { useRouter } from 'vue-router';
import { onMounted, onUnmounted, ref } from 'vue';
import { LoginAPI, Query2API, RegisterAPI, SendCodeAPI, ResetPasswordAPI } from "@/api1/api1.js";
import { ElMessage } from "element-plus";
import { categoryStore } from "@/stores/stores1";

const c = categoryStore();
const router1 = useRouter();
// 忘记密码表单数据
const forgotPasswordForm = ref({
  username: '',
  email: '',
  verifyCode: '',
  newPassword: '',
  confirmPassword: ''
});

// 忘记密码对话框显示状态
const showForgotPasswordDialog = ref(false);

// 忘记密码验证码状态
const forgotPasswordCodeStatus = ref({
  isSending: false,
  countDown: 0,
  timer: null
});

// 忘记密码处理函数
const sendForgotPasswordCode = async () => {
  const emailReg = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
  if (!forgotPasswordForm.value.username) {
    ElMessage.warning('请输入用户名');
    return;
  }
  if (!forgotPasswordForm.value.email) {
    ElMessage.warning('请输入邮箱');
    return;
  }
  if (!emailReg.test(forgotPasswordForm.value.email)) {
    ElMessage.warning('请输入正确的邮箱格式');
    return;
  }
  if (forgotPasswordCodeStatus.value.isSending || forgotPasswordCodeStatus.value.countDown > 0) return;

  try {
    // 发送验证码（使用用户名和邮箱）
    const res = await SendCodeAPI('/send_code/', {
      username: forgotPasswordForm.value.username,
      email: forgotPasswordForm.value.email
    });
    ElMessage.success(res.message || '验证码已发送');

    forgotPasswordCodeStatus.value.isSending = true;
    forgotPasswordCodeStatus.value.countDown = 60;
    forgotPasswordCodeStatus.value.timer = setInterval(() => {
      forgotPasswordCodeStatus.value.countDown--;
      if (forgotPasswordCodeStatus.value.countDown <= 0) {
        clearInterval(forgotPasswordCodeStatus.value.timer);
        forgotPasswordCodeStatus.value.isSending = false;
        forgotPasswordCodeStatus.value.timer = null;
      }
    }, 1000);
  } catch (err) {
    ElMessage.error('验证码发送失败，请检查用户名和邮箱是否正确');
  }
};

const handleForgotPassword = async () => {
  const emailReg = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
  if (!forgotPasswordForm.value.username) {
    ElMessage.warning('请输入用户名');
    return;
  }
  if (!forgotPasswordForm.value.email) {
    ElMessage.warning('请输入邮箱');
    return;
  }
  if (!emailReg.test(forgotPasswordForm.value.email)) {
    ElMessage.warning('请输入正确的邮箱格式');
    return;
  }
  if (!forgotPasswordForm.value.verifyCode) {
    ElMessage.warning('请输入验证码');
    return;
  }
  if (!forgotPasswordForm.value.newPassword) {
    ElMessage.warning('请输入新密码');
    return;
  }
  if (forgotPasswordForm.value.newPassword !== forgotPasswordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  if (forgotPasswordForm.value.newPassword.length < 6) {
    ElMessage.warning('密码长度不能少于6位');
    return;
  }

  try {
    // 调用重置密码API
    const res = await ResetPasswordAPI('/login/reset_password/', forgotPasswordForm.value);
    ElMessage.success(res.message || '密码重置成功，请使用新密码登录');
    showForgotPasswordDialog.value = false;
    // 清空表单
    forgotPasswordForm.value = {
      username: '',
      email: '',
      verifyCode: '',
      newPassword: '',
      confirmPassword: ''
    };
    if (forgotPasswordCodeStatus.value.timer) {
      clearInterval(forgotPasswordCodeStatus.value.timer);
    }
  } catch (err) {
    ElMessage.error('密码重置失败，请检查用户名、邮箱或验证码是否正确');
  }
};

// 打开忘记密码对话框
const openForgotPassword = () => {
  showForgotPasswordDialog.value = true;
};

// 角色选择：student-学生, teacher-教师, admin-管理员
const selectedRole = ref('student');

// 登录模式切换标志
const isLoginMode = ref(true);

// 是否显示注册选项（根据角色决定）
const showRegister = ref(true);

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  remember: false
});

// 注册表单数据（新增：verifyCode 字段）
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  verifyCode: '' // 验证码输入框绑定字段
});

// 新增：验证码相关状态
const codeStatus = ref({
  isSending: false, // 是否正在发送验证码
  countDown: 0,     // 倒计时（秒）
  timer: null       // 倒计时定时器
});

// 登录处理函数
const handleLogin = async () => {
  if (loginForm.value.username === '' || loginForm.value.password === '') {
    alert('用户名或密码不能为空');
    return;
  }
  try {
    const res = await LoginAPI('/login/login1/', loginForm.value)

    // 验证用户身份是否与选择的角色一致
    const roleMap = {
      'student': 'student',
      'teacher': 'teacher',
      'admin': 'admin'
    };

    // 后端返回的角色可能与前端选择不一致，需要进行验证
    if (res.role !== selectedRole.value) {
      ElMessage.error(`登录失败:您选择的身份是「${roleNames[selectedRole.value]}」,但您的账号身份是「${roleNames[res.role] || res.role}」,请重新选择身份`);
      return;
    }

    localStorage.setItem('access_token', res.access)
    localStorage.setItem('refresh_token', res.refresh)
    localStorage.setItem('userId', res.id)
    localStorage.setItem('username1', res.username)
    localStorage.setItem('role', res.role)
    
    // 处理"记住我"功能
    if (loginForm.value.remember) {
      // 保存用户名和密码到 localStorage（注意：实际项目中建议加密存储）
      localStorage.setItem('remembered_username', loginForm.value.username)
      localStorage.setItem('remembered_password', loginForm.value.password)
      localStorage.setItem('remembered_role', selectedRole.value)
      localStorage.setItem('remember_me', 'true')
      console.log('✓ 已保存登录信息')
    } else {
      // 清除之前保存的密码
      localStorage.removeItem('remembered_username')
      localStorage.removeItem('remembered_password')
      localStorage.removeItem('remembered_role')
      localStorage.removeItem('remember_me')
      console.log('✓ 已清除保存的登录信息')
    }
    
    ElMessage.success(res.username + '登录成功\n' + '身份' + res.role);
    try {
      // const classData = await Query2API('/query/query_class/');
      const classnameData = await Query2API('/query/query_classname/');
      const gradeData = await Query2API('/query/query_grade/');
      const specialtyData = await Query2API('/query/query_specialty/');

      // await c.addClass(classData);
      await c.addClassName(classnameData);
      await c.addGrade(gradeData);
      await c.addSpecialty(specialtyData);

    } catch (error) {
      ElMessage.error('加载数据失败');
      console.error(error);
    }
    await router1.push('/main')
  } catch (err) {
    console.error('登录错误:', err)
    ElMessage.error('登录失败,请检查用户名或密码')
  }
};

// 社交登录处理函数
const socialLogin = (type) => {
  if (type === 'wechat') {
    window.location.href = "http://127.0.0.1:8000/quickauth_wechat_login";
  }
};

// 新增：发送验证码函数
const sendVerifyCode = async () => {
  // 1. 校验邮箱格式
  const emailReg = /^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/;
  if (!registerForm.value.email) {
    ElMessage.warning('请先输入邮箱地址');
    return;
  }
  if (!emailReg.test(registerForm.value.email)) {
    ElMessage.warning('请输入正确的邮箱格式（如：xxx@xxx.com）');
    return;
  }

  // 2. 防止重复发送
  if (codeStatus.value.isSending || codeStatus.value.countDown > 0) return;

  try {
    // 3. 调用发送验证码接口（需确保后端接口支持按邮箱发送）
    const res = await SendCodeAPI('/send_code/', registerForm.value);
    ElMessage.success(res.message);

    // 4. 启动倒计时（60秒）
    codeStatus.value.isSending = true;
    codeStatus.value.countDown = 60;
    codeStatus.value.timer = setInterval(() => {
      codeStatus.value.countDown--;
      // 倒计时结束重置状态
      if (codeStatus.value.countDown <= 0) {
        clearInterval(codeStatus.value.timer);
        codeStatus.value.isSending = false;
        codeStatus.value.timer = null;
      }
    }, 1000);
  } catch (err) {
    ElMessage.error('验证码发送失败，请稍后重试');
  }
};

// 注册处理函数（新增：验证码校验）
const handleRegister = async () => {
  // 1. 原有校验逻辑保留
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    ElMessage.warning('用户名、邮箱或密码不能为空');
    return;
  }

  // 2. 新增：验证码校验
  if (!registerForm.value.verifyCode) {
    ElMessage.warning('请输入验证码');
    return;
  }

  try {
    // 3. 提交注册（携带验证码参数给后端）

    const res = await RegisterAPI('/login/register1/', registerForm.value)
    ElMessage.success(res.message);
    await router1.push('/login')
  } catch (err) {
    ElMessage.error('注册失败，请检查邮箱或验证码是否正确')
  }
};

// 角色选择下拉菜单状态
const showRoleDropdown = ref(false);

// 切换角色下拉菜单显示
const toggleRoleDropdown = () => {
  showRoleDropdown.value = !showRoleDropdown.value;
};

// 页面卸载时清除定时器和隐藏下拉菜单
onUnmounted(async () => {
  if (codeStatus.value.timer) {
    clearInterval(codeStatus.value.timer);
  }
  showRoleDropdown.value = false;
});

// 页面加载时获取数据
onMounted(async () => {
  // 获取下拉列表数据
  
  // 自动填充已保存的登录信息
  const rememberMe = localStorage.getItem('remember_me')
  if (rememberMe === 'true') {
    const savedUsername = localStorage.getItem('remembered_username')
    const savedPassword = localStorage.getItem('remembered_password')
    const savedRole = localStorage.getItem('remembered_role')
    
    if (savedUsername && savedPassword) {
      loginForm.value.username = savedUsername
      loginForm.value.password = savedPassword
      loginForm.value.remember = true
      
      // 恢复上次选择的角色
      if (savedRole && ['student', 'teacher', 'admin'].includes(savedRole)) {
        selectedRole.value = savedRole
        showRegister.value = savedRole === 'student'
      }
      
      console.log('✓ 已自动填充登录信息')
    }
  }
});

// 切换角色
const switchRole = (role) => {
  selectedRole.value = role;
  // 只有学生角色可以注册，教师和管理员只能登录
  showRegister.value = role === 'student';
  // 切换到角色时，默认显示登录页面
  isLoginMode.value = true;
  // 点击角色后关闭下拉菜单
  showRoleDropdown.value = false;
};

// 角色名称映射
const roleNames = {
  student: '学生',
  teacher: '教师',
  admin: '管理员'
};
</script>

<template>
  <div class="auth-page">
    <div class="bg-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <div class="main-container">
      <div class="info-panel">
        <header class="hero-header">
          <div class="icon-box"><i class="fas fa-university"></i></div>
          <div class="text-box">
            <h1>会计模考系统</h1>
            <p>PROFESSIONAL ACCOUNTING EXAM SYSTEM</p>
          </div>
        </header>

        <div class="feature-grid">
          <div class="feature-card">
            <i class="fas fa-bolt"></i>
            <div class="inner">
              <h3>全真模拟</h3>
              <p>1:1 还原真实考场交互体验</p>
            </div>
          </div>
          <div class="feature-card">
            <i class="fas fa-brain"></i>
            <div class="inner">
              <h3>AI辅助</h3>
              <p>解决考试中各种不规范不确定问题</p>
            </div>
          </div>
        </div>

        <div class="data-dashboard">
          <div class="data-item">
            <span class="num">50k+</span>
            <span class="lab">精选试题</span>
          </div>
          <div class="divider-v"></div>
          <div class="data-item">
            <span class="num">95%</span>
            <span class="lab">提分率</span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="glass-card">
          <div class="form-header">
            <h2>{{ isLoginMode ? '欢迎回来' : '开启学习之旅' }}</h2>

            <!-- 角色选择按钮 -->
            <div class="role-selector">
              <div class="role-dropdown">
                <button class="role-btn" @click="toggleRoleDropdown">
                  <i class="fas fa-user"></i>
                  <span>{{ roleNames[selectedRole] }}</span>
                  <i class="fas fa-chevron-down"></i>
                </button>
                <div class="role-menu" v-show="showRoleDropdown">
                  <div
                    class="role-option"
                    :class="{ active: selectedRole === 'student' }"
                    @click="switchRole('student')"
                  >
                    <i class="fas fa-user-graduate"></i>
                    <span>学生登录</span>
                  </div>
                  <div
                    class="role-option"
                    :class="{ active: selectedRole === 'teacher' }"
                    @click="switchRole('teacher')"
                  >
                    <i class="fas fa-chalkboard-teacher"></i>
                    <span>教师登录</span>
                  </div>
                  <div
                    class="role-option"
                    :class="{ active: selectedRole === 'admin' }"
                    @click="switchRole('admin')"
                  >
                    <i class="fas fa-user-shield"></i>
                    <span>管理员登录</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 登录/注册切换（只在学生角色时显示） -->
            <div class="tab-switcher" v-show="showRegister">
              <button :class="{ active: isLoginMode }" @click="isLoginMode = true">账号登录</button>
              <button :class="{ active: !isLoginMode }" @click="isLoginMode = false">新用户注册</button>
            </div>
          </div>

          <transition name="fade-slide" mode="out-in">
            <form v-if="isLoginMode" class="form-body" name="loginForm" @submit.prevent="handleLogin">
              <div class="input-group">
                <i class="fas fa-user-circle"></i>
                <input v-model="loginForm.username" type="text" name="username" autocomplete="username" placeholder="用户名/邮箱" required>
              </div>
              <div class="input-group">
                <i class="fas fa-key"></i>
                <input v-model="loginForm.password" type="password" name="password" autocomplete="current-password" placeholder="请输入密码" required>
              </div>
              <div class="form-utils">
                <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                <a href="#" class="forgot-pwd" @click.prevent="openForgotPassword">忘记密码？</a>
              </div>
              <button type="submit" class="btn-primary">立即登录 <i class="fas fa-sign-in-alt"></i></button>
            </form>

            <form v-else class="form-body reg-grid" @submit.prevent="handleRegister">
              <div class="input-group full">
                <i class="fas fa-id-card"></i>
                <input v-model="registerForm.username" type="text" placeholder="设置用户名" required>
              </div>

              <div class="input-group full">
                <i class="fas fa-envelope"></i>
                <input v-model="registerForm.email" type="email" placeholder="电子邮箱" required>
              </div>

              <div class="verify-row full">
                <div class="input-group">
                  <i class="fas fa-shield-alt"></i>
                  <input v-model="registerForm.verifyCode" type="text" placeholder="验证码" maxlength="6">
                </div>
                <button
                  type="button"
                  class="btn-send"
                  :disabled="codeStatus.countDown > 0"
                  @click="sendVerifyCode"
                >
                  {{ codeStatus.countDown > 0 ? `${codeStatus.countDown}s` : '获取' }}
                </button>
              </div>

              <div class="input-group">
                <i class="fas fa-lock"></i>
                <input v-model="registerForm.password" type="password" placeholder="密码" required>
              </div>
              <div class="input-group">
                <i class="fas fa-check-double"></i>
                <input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" required>
              </div>

              <button type="submit" class="btn-primary full">完成注册 <i class="fas fa-user-check"></i></button>
            </form>
          </transition>

          <footer class="form-footer">
            <p>登录即代表同意 <a href="#">服务协议</a> 与 <a href="#">隐私政策</a></p>
          </footer>
        </div>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog
      v-model="showForgotPasswordDialog"
      title="重置密码"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="forgotPasswordForm" label-width="100px" class="forgot-password-form">
        <el-form-item label="用户名">
          <el-input 
            v-model="forgotPasswordForm.username" 
            placeholder="请输入用户名" 
            prefix-icon="el-icon-user"
          />
        </el-form-item>
        
        <el-form-item label="邮箱地址">
          <el-input 
            v-model="forgotPasswordForm.email" 
            placeholder="请输入注册邮箱" 
            prefix-icon="el-icon-message"
          />
        </el-form-item>
        
        <el-form-item label="验证码">
          <div style="display: flex; gap: 10px;">
            <el-input 
              v-model="forgotPasswordForm.verifyCode" 
              placeholder="请输入验证码" 
              maxlength="6"
              style="flex: 1;"
            />
            <el-button 
              @click="sendForgotPasswordCode" 
              :disabled="forgotPasswordCodeStatus.countDown > 0"
              :loading="forgotPasswordCodeStatus.isSending"
            >
              {{ forgotPasswordCodeStatus.countDown > 0 ? `${forgotPasswordCodeStatus.countDown}s后重发` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="新密码">
          <el-input 
            v-model="forgotPasswordForm.newPassword" 
            type="password" 
            placeholder="请输入新密码（至少6位）" 
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码">
          <el-input 
            v-model="forgotPasswordForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入新密码" 
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showForgotPasswordDialog = false">取消</el-button>
          <el-button type="primary" @click="handleForgotPassword">重置密码</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
<style scoped>
/* 核心布局 */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f7ff;
  overflow: hidden;
  position: relative;
}

.main-container {
  width: 100%;
  max-width: 1100px;
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 60px;
  padding: 20px;
  z-index: 2;
}

/* 左侧品牌区设计 */
.info-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 50px;
}

.icon-box {
  width: 64px;
  height: 64px;
  background: #1890ff;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  box-shadow: 0 10px 20px rgba(24, 144, 255, 0.3);
}

.hero-header h1 {
  font-size: 32px;
  color: #1a3353;
  margin: 0;
  letter-spacing: 1px;
}

.hero-header p {
  font-size: 12px;
  color: #8cc1f9;
  margin: 4px 0 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 60px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.6);
  padding: 20px;
  border-radius: 15px;
  display: flex;
  gap: 15px;
  transition: transform 0.3s;
}

.feature-card:hover { transform: translateY(-5px); }

.feature-card i { color: #1890ff; font-size: 20px; }

.feature-card h3 { font-size: 16px; margin: 0 0 5px; color: #1a3353; }

.feature-card p { font-size: 13px; color: #647d9c; margin: 0; line-height: 1.4; }

.data-dashboard {
  display: flex;
  align-items: center;
  gap: 40px;
  background: white;
  width: fit-content;
  padding: 15px 30px;
  border-radius: 50px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.num { font-size: 24px; font-weight: 800; color: #1890ff; display: block; }

.lab { font-size: 12px; color: #94a3b8; }

/* 右侧卡片设计 */
.glass-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 25px 50px rgba(0, 50, 100, 0.1);
}

.form-header h2 {
  text-align: center;
  color: #1a3353;
  margin-bottom: 20px;
}

/* 角色选择器样式 */
.role-selector {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}

.role-dropdown {
  position: relative;
}

.role-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #1a3353;
  transition: all 0.3s;
}

.role-btn:hover {
  background: #e2e8f0;
  border-color: #1890ff;
}

.role-btn i.fa-chevron-down {
  font-size: 12px;
  transition: transform 0.3s;
}

.role-menu {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 6px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  padding: 6px;
  z-index: 100;
  min-width: 150px;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #64748b;
  font-size: 13px;
}

.role-option:hover {
  background: #f1f5f9;
  color: #1890ff;
}

.role-option.active {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: 600;
}

.role-option i {
  font-size: 14px;
  width: 16px;
  text-align: center;
}

.tab-switcher {
  display: flex;
  background: #f1f5f9;
  padding: 5px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.tab-switcher button {
  flex: 1;
  padding: 10px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 600;
  color: #64748b;
  transition: all 0.3s;
}

.tab-switcher button.active {
  background: white;
  color: #1890ff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* 输入框通用样式 */
.form-body { display: flex; flex-direction: column; gap: 20px; }

.reg-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.full { grid-column: span 2; }

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group i {
  position: absolute;
  left: 15px;
  color: #94a3b8;
}

.input-group input {
  width: 100%;
  padding: 12px 12px 12px 45px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  outline: none;
  transition: all 0.3s;
}

.input-group input:focus {
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.1);
}

/* 验证码行 */
.verify-row {
  display: flex;
  gap: 10px;
}

.btn-send {
  white-space: nowrap;
  padding: 0 15px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #1890ff;
  border-radius: 10px;
  cursor: pointer;
}

.btn-send:disabled { color: #bfbfbf; cursor: not-allowed; }

/* 按钮样式 */
.btn-primary {
  padding: 14px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: opacity 0.3s;
}

.btn-primary:hover { opacity: 0.9; }

.form-utils {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.forgot-pwd { color: #1890ff; text-decoration: none; }

/* 背景点缀 */
.bg-blobs .blob {
  position: absolute;
  filter: blur(80px);
  z-index: 1;
  border-radius: 50%;
}

.blob-1 { width: 500px; height: 500px; background: #dbeafe; top: -100px; left: -100px; }
.blob-2 { width: 400px; height: 400px; background: #e0f2fe; bottom: -50px; right: 0; }

/* 动画 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s;
}
.fade-slide-enter-from { opacity: 0; transform: translateX(20px); }
.fade-slide-leave-to { opacity: 0; transform: translateX(-20px); }

/* 移动端适配 */
@media (max-width: 900px) {
  .main-container { grid-template-columns: 1fr; }
  .info-panel { display: none; }
}
</style>
