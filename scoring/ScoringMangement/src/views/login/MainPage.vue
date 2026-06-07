<template>
  <div class="app-shell">
    <div class="bg-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <header class="top-navbar">
      <div class="nav-left">
        <div class="logo-area">
          <div class="logo-icon"><el-icon><Reading /></el-icon></div>
          <div class="logo-text">
            <h2>会计考试管理系统</h2>
            <span>Smart Accounting Platform</span>
          </div>
        </div>
      </div>

      <div class="nav-right">

        <div class="notification-wrapper">
          <el-badge :value="unreadCount" :max="99" :hidden="unreadCount <= 0">
            <el-button class="icon-btn" @click="showNotifications" circle>
              <el-icon size="18"><Bell /></el-icon>
            </el-button>
          </el-badge>
        </div>

        <el-dropdown placement="bottom-end" class="profile-dropdown">
          <div class="user-pill">
            <el-avatar :src="userAvatar" :size="32" class="avatar-border" />
            <span class="user-name">{{ userName }}</span>
            <el-icon class="arrow-icon"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="modern-dropdown">
              <el-dropdown-item @click="handleGoToPersonalCenter">
                <el-icon><User /></el-icon>个人中心
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout" class="logout-item">
                <el-icon><SwitchButton /></el-icon>退出系统
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <main class="main-layout">
      <aside class="sidebar-wrapper">
        <div class="sidebar-scroller">
          <div
            class="menu-section"
            v-for="(group, groupIndex) in functionalModules"
            :key="groupIndex"
          >
            <h3 class="section-title">{{ group.groupName }}</h3>
            <nav class="menu-list">
              <div
                class="nav-item"
                v-for="(item, itemIndex) in group.items"
                :key="item.key"
                :class="{ active: currentActiveMenu === item.key }"
                @click="goToFunction(item.route, item.key, item.component)"
              >
                <div class="nav-icon" :style="{ backgroundColor: item.style.bgColor, color: item.style.borderColor }">
                  <el-icon><component :is="iconMap[item.icon]" /></el-icon>
                </div>
                <span class="nav-label">{{ item.name }}</span>
                <div class="active-indicator"></div>
              </div>
            </nav>
          </div>
        </div>
      </aside>

      <section class="viewport-container">
        <div class="content-wrapper">
          <div v-show="currentActiveMenu === 'question-bank'" class="component-card">
            <component :is="questionBankComponent" />
          </div>
          <div v-show="currentActiveMenu === 'exam'" class="component-card">
            <component :is="examComponent" />
          </div>
          <div v-show="currentActiveMenu === 'user'" class="component-card">
            <component :is="userComponent" />
          </div>
          <div v-show="currentActiveMenu === 'log'" class="component-card">
            <component :is="logComponent" />
          </div>
          <div v-show="currentActiveMenu === 'review'" class="component-card">
            <component :is="reviewComponent" />
          </div>
          <div v-show="currentActiveMenu === 'error'" class="component-card">
            <component :is="errorComponent" />
          </div>
          <div v-show="currentActiveMenu === 'student-review'" class="component-card">
            <component :is="StudentPersonalReport" />
          </div>
          <div v-show="currentActiveMenu === 'my-exam'" class="component-card">
            <component :is="examComponent" />
          </div>
          <div v-show="currentActiveMenu === 'ai-assistant'" class="component-card">
            <component :is="aiComponent" />
          </div>

          <div v-show="!currentActiveMenu" class="welcome-card">
            <div class="welcome-content">
              <img src="https://img.icons8.com/bubbles/200/000000/learning.png" alt="welcome" />
              <h2>欢迎回来，{{ userName }}</h2>
              <p>请选择左侧功能模块开始您的智慧办公之旅</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
/* 你的 JS 逻辑完全保持不变 ... */
import { onMounted, ref, shallowRef, computed } from 'vue';
import {
  Bell,
  Calendar,
  CircleClose,
  Document,
  Reading,
  RefreshLeft,
  RefreshRight,
  Search,
  SwitchButton,
  Ticket,
  User,
  UserFilled,
  ArrowDown
} from '@element-plus/icons-vue';

import { useRouter } from 'vue-router';
import { logoutAPI } from "@/api1/api1.js";
import StudentPersonalReport from "@/views/reports/StudentPersonalReport.vue";
import AdminQuestion from "@/views/views/admin_question_list.vue";
import ManageUser from "@/views/login/ManageUser.vue";
import Audit from "@/views/views/Audit.vue";
import Review from "@/views/Review.vue";
import ErrorBook from "@/views/views-wrong/App1.vue";
import examComponent1 from "@/views/viewshu/HomeView.vue";
import AiComponent from "@/views/login/ai.vue";

const aiComponent = computed(() => AiComponent);
const router1 = useRouter();
const role1 = ref("");
const searchQuery = ref('');
const currentComponent = shallowRef(null);
const unreadCount = ref(3);
const userName = localStorage.getItem('username1') || 'Admin';
const userAvatar = ref('https://picsum.photos/id/1027/200/200');
const currentActiveMenu = ref('');

const iconMap = { Reading, User, SwitchButton, Document, Ticket, UserFilled, CircleClose, RefreshLeft, RefreshRight, Calendar, Bell, Search };
const questionBankComponent = computed(() => AdminQuestion);
const userComponent = computed(() => ManageUser);
const logComponent = computed(() => Audit);
const reviewComponent = computed(() => Review);
const errorComponent = computed(() => ErrorBook);
const examComponent = computed(() => examComponent1);
const topicListComponent = computed(() => TopicListComponent);

const functionalModules = ref([]);
const initFunctionalModules = () => {
  const role = localStorage.getItem('role');
  const styles = {
    'question-bank': { bgColor: 'rgba(64, 158, 255, 0.1)', borderColor: '#409eff' },
    'exam': { bgColor: 'rgba(103, 194, 58, 0.1)', borderColor: '#67c23a' },
    'user': { bgColor: 'rgba(250, 173, 20, 0.1)', borderColor: '#fadb14' },
    'log': { bgColor: 'rgba(191, 136, 255, 0.1)', borderColor: '#bf88ff' },
    'review': { bgColor: 'rgba(230, 126, 34, 0.1)', borderColor: '#e67e22' },
    'error': { bgColor: 'rgba(235, 64, 52, 0.1)', borderColor: '#eb4034' },
    'practice': { bgColor: 'rgba(0, 184, 148, 0.1)', borderColor: '#00b894' },
    'my-exam': { bgColor: 'rgba(52, 152, 219, 0.1)', borderColor: '#3498db' },
    'ai-assistant': { bgColor: 'rgba(124, 58, 237, 0.1)', borderColor: '#7c3aed' }
  };

  if (role === 'admin') {
    functionalModules.value = [
      {
        groupName: '系统管理',
        items: [
          { name: '题库管理', icon: 'Document', route: '/admin_question', key: 'question-bank', style: styles['question-bank'] },
          { name: '考试管理', icon: 'Ticket', route: '/exam-teacher', key: 'exam', style: styles['exam'] },
          { name: '用户管理', icon: 'UserFilled', route: '/manageuser', key: 'user', style: styles['user'] },
          { name: '日志查看', icon: 'Calendar', route: '/audit', key: 'log', style: styles['log'] },
        ]
      },
      {
        groupName: 'AI助手',
        items: [
          { name: 'AI智能助手', icon: 'Reading', route: '/ai', key: 'ai-assistant', style: styles['ai-assistant'] }
        ]
      }
    ];
  } else if (role === 'teacher') {
    functionalModules.value = [
      {
        groupName: '教学管理',
        items: [
          { name: '题库管理', icon: 'Document', route: '/admin_question', key: 'question-bank', style: styles['question-bank'] },
          { name: '试卷评阅', icon: 'Ticket', route: '/review', key: 'review', style: styles['review'] },
        ]
      },
      {
        groupName: 'AI 助手',
        items: [
          { name: 'AI 智能助手', icon: 'Reading', route: '/ai', key: 'ai-assistant', style: styles['ai-assistant'] }
        ]
      }
    ];
  } else if (role === 'student') {
    functionalModules.value = [
      {
        groupName: '学习中心',
        items: [
          { name: '复习记录', icon: 'CircleClose', route: '/error-book', key: 'error', style: styles['error'] }
        ]
      },
      {
        groupName: '评审中心',
        items: [
          { name: '学生报告', icon: 'Ticket', route: '/student-report', key: 'student-review', component: StudentPersonalReport, style: styles['review'] },
        ]
      },
      {
        groupName: '考试参与',
        items: [
          { name: '我的考试', icon: 'Ticket', route: '/my-exam', key: 'my-exam', style: styles['my-exam'] },
        ]
      },
      {
        groupName: 'AI助手',
        items: [
          { name: 'AI智能助手', icon: 'Reading', route: '/ai', key: 'ai-assistant', style: styles['ai-assistant'] }
        ]
      }
    ];
  }
};

const handleLogout = async () => {
  try { await logoutAPI('/logout/'); } catch (error) {}
  localStorage.clear();
  router1.push('/login');
};

const goToFunction = (route, key, component) => {
  currentActiveMenu.value = key;
  if (component) { currentComponent.value = component; }
};

const handleGoToPersonalCenter = () => router1.push('/person');
const showNotifications = () => router1.push('/notification');
const handleSearch = () => console.log('搜索:', searchQuery.value);

onMounted(() => {
  const role = localStorage.getItem('role') || 'student';
  role1.value = role;
  initFunctionalModules();
  if (role === 'admin') {
  currentActiveMenu.value = 'question-bank';
    } else if (role === 'teacher') { // 教师默认选中评审管理
  currentActiveMenu.value = 'review';
    } else { // 学生保持原有逻辑
  currentActiveMenu.value = 'error';
    }
});
</script>

<style scoped>
/* 核心容器 */
.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f4f7fc;
  overflow: hidden;
  position: relative;
  font-family: 'Inter', -apple-system, sans-serif;
}

/* 动态背景保持不变 */
.bg-blobs {
  position: absolute;
  width: 100%; height: 100%;
  z-index: 0; pointer-events: none;
}
.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.2;
  border-radius: 50%;
}
.blob-1 { width: 500px; height: 500px; background: #4c77a0; top: -100px; right: -50px; }
.blob-2 { width: 400px; height: 400px; background: #8ea3ca; bottom: -100px; left: -50px; }

/* 顶部导航：微调边框，移除底部阴影以减少割裂感 */
.top-navbar {
  height: 60px; /* 稍微压缩高度 */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 100;
}

.logo-area { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #4c77a0, #8ea3ca);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 16px;
}
.logo-text h2 { margin: 0; font-size: 15px; color: #334155; font-weight: 700; }
.logo-text span { font-size: 10px; color: #94a3b8; text-transform: uppercase; }

.nav-right { display: flex; align-items: center; gap: 12px; }
.header-search { width: 180px; }
:deep(.header-search .el-input__wrapper) {
  border-radius: 8px; background: #f1f5f9; box-shadow: none;
}

.user-pill {
  display: flex; align-items: center; gap: 8px;
  padding: 3px 10px 3px 4px;
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 50px; cursor: pointer;
}

/* 主体布局：移除可能存在的间隙 */
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* 侧边栏：微调宽度和内边距 */
.sidebar-wrapper {
  width: 220px; /* 稍微调窄一点 */
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-right: 1px solid #e2e8f0;
  padding: 12px 8px; /* 减少内边距 */
}

.section-title {
  padding: 0 12px; font-size: 11px;
  text-transform: uppercase; color: #94a3b8;
  letter-spacing: 1px; margin: 12px 0 8px;
}

.nav-item {
  display: flex; align-items: center;
  padding: 8px 12px; border-radius: 10px;
  cursor: pointer; transition: 0.2s;
  position: relative; margin-bottom: 2px;
}
.nav-item:hover { background: rgba(255, 255, 255, 0.9); }
.nav-item.active {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.nav-label { font-size: 13px; color: #64748b; }

.nav-icon {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  margin-right: 10px; font-size: 14px;
}

/* --- 核心优化点：内容视口 --- */
.viewport-container {
  flex: 1;
  padding: 12px; /* 原来是 20px，缩小内边距让内容更靠近边框 */
  overflow-y: auto;
  background: rgba(241, 245, 249, 0.5);
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.component-card {
  background: #fff;
  border-radius: 12px; /* 稍微减小圆角，增强严谨感 */
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05); /* 减弱阴影，让卡片看起来更像页面一部分 */
  flex: 1; /* 撑满容器高度 */
  min-height: auto; /* 移除固定的 min-height，由内容撑开 */
}

/* 欢迎页 */
.welcome-card {
  flex: 1; display: flex; align-items: center; justify-content: center;
  background: #fff; border-radius: 12px;
}
.welcome-content { text-align: center; }
.welcome-content img { width: 150px; } /* 缩小欢迎图 */

/* 消息按钮 */
.icon-btn { border: 1px solid #e2e8f0; color: #64748b; }

/* 滚动条美化 */
.sidebar-scroller::-webkit-scrollbar { width: 4px; }
.sidebar-scroller::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
