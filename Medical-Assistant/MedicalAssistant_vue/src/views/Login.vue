<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>医疗知识助手</h1>
        <p>欢迎登录系统</p>
      </div>

      <!-- 登录/注册切换 -->
      <div class="mode-switch">
        <button 
          :class="['switch-btn', { active: isLogin }]" 
          @click="isLogin = true"
        >
          登录
        </button>
        <button 
          :class="['switch-btn', { active: !isLogin }]" 
          @click="isLogin = false"
        >
          注册
        </button>
      </div>

      <!-- 登录表单 -->
      <form v-if="isLogin" @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="loginForm.username"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="loginForm.password"
            placeholder="请输入密码"
            required
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册表单 -->
      <form v-else @submit.prevent="handleRegister" class="login-form">
        <div class="form-group">
          <label for="reg-username">用户名</label>
          <input
            type="text"
            id="reg-username"
            v-model="registerForm.username"
            placeholder="请输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="reg-email">邮箱（可选）</label>
          <input
            type="email"
            id="reg-email"
            v-model="registerForm.email"
            placeholder="请输入邮箱"
          />
        </div>

        <div class="form-group">
          <label for="reg-password">密码</label>
          <input
            type="password"
            id="reg-password"
            v-model="registerForm.password"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="form-group">
          <label for="reg-confirm-password">确认密码</label>
          <input
            type="password"
            id="reg-confirm-password"
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            required
          />
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <!-- 错误提示 -->
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <!-- 成功提示 -->
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

// 当前模式：true为登录，false为注册
const isLogin = ref(true);
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
});

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

// API基础URL
const API_BASE_URL = 'http://localhost:8000';

// 处理登录
const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
      username: loginForm.username,
      password: loginForm.password
    });

    // 保存用户信息到localStorage
    localStorage.setItem('user_id', response.data.user_id);
    localStorage.setItem('username', response.data.username);
    localStorage.setItem('isLoggedIn', 'true');

    successMessage.value = '登录成功！正在跳转...';
    
    // 延迟跳转到主页面
    setTimeout(() => {
      router.push('/main');
    }, 1000);

  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查用户名和密码';
  } finally {
    loading.value = false;
  }
};

// 处理注册
const handleRegister = async () => {
  // 验证密码
  if (registerForm.password !== registerForm.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致';
    return;
  }

  if (registerForm.password.length < 6) {
    errorMessage.value = '密码长度至少为6位';
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, {
      username: registerForm.username,
      password: registerForm.password,
      email: registerForm.email || null
    });

    successMessage.value = '注册成功！请登录';
    
    // 清空注册表单
    registerForm.username = '';
    registerForm.email = '';
    registerForm.password = '';
    registerForm.confirmPassword = '';

    // 切换到登录模式
    setTimeout(() => {
      isLogin.value = true;
      successMessage.value = '';
    }, 1500);

  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '注册失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 450px;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.mode-switch {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: #f5f5f5;
  padding: 5px;
  border-radius: 10px;
}

.switch-btn {
  flex: 1;
  padding: 10px;
  border: none;
  background: transparent;
  color: #666;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
}

.switch-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s;
  outline: none;
}

.form-group input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.submit-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 20px;
  padding: 12px;
  background: #fee;
  color: #c33;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #fcc;
}

.success-message {
  margin-top: 20px;
  padding: 12px;
  background: #efe;
  color: #3c3;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #cfc;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }

  .login-header h1 {
    font-size: 24px;
  }
}
</style>
