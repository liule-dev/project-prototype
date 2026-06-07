<template>
  <div class="learning-center">
    <el-container class="main-container">
      <el-header class="top-header">
        <div class="header-content">
          <div class="header-left">
            <el-button
              class="back-btn"
              icon="ArrowLeft"
              circle
              size="small"
              @click="goBack"
            />
            <h1 class="logo">🎓 学习中心</h1>
          </div>

          <el-menu
            :default-active="activeTab"
            class="top-menu"
            mode="horizontal"
            @select="handleTabChange"
            background-color="#409eff"
            text-color="#ffffffb3"
            active-text-color="#ffffff"
          >
            <el-menu-item index="wrongTopics">
              <el-icon><Document /></el-icon>
              <span>📘 我的错题</span>
            </el-menu-item>
            <el-menu-item index="aiAssistant">
              <el-icon><MagicStick /></el-icon>
              <span>🤖 AI 助手</span>
            </el-menu-item>
          </el-menu>

          <div class="header-right">
            <el-tag type="warning" effect="dark" round size="small">Beta</el-tag>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="content-wrapper">
          <transition name="fade" mode="out-in">
            <WrongTopicsView v-if="activeTab === 'wrongTopics'" />

            <AIAssistantView v-else-if="activeTab === 'aiAssistant'" />
          </transition>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Document, MagicStick, ArrowLeft } from '@element-plus/icons-vue'
import WrongTopicsView from './WrongTopicsView.vue'
import AIAssistantView from './AIAssistantView.vue'

export default {
  name: 'LearningCenter',
  components: {
    Document,
    MagicStick,
    ArrowLeft,
    WrongTopicsView,
    AIAssistantView
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('wrongTopics')

    const handleTabChange = (index) => {
      activeTab.value = index
    }

    const goBack = async () => {
      try {
        await router.push('/main')
      } catch (error) {
        window.history.length > 1 ? router.go(-1) : router.push('/')
      }
    }

    return {
      activeTab,
      handleTabChange,
      goBack
    }
  }
}
</script>

<style scoped>
.learning-center {
  height: 100vh;
  overflow: hidden;
}

.main-container {
  height: 100%;
}

.top-header {
  background-color: #409eff;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(64, 158, 255, 0.3);
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 20px;
}

.back-btn {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
}
.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.4);
  color: white;
}

.logo {
  margin: 0;
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  white-space: nowrap;
}

.top-menu {
  flex: 1;
  border-bottom: none !important;
  height: 60px;
  display: flex;
}

.top-menu :deep(.el-menu-item) {
  height: 60px;
  line-height: 60px;
  border-bottom: none !important;
  font-size: 14px;
  padding: 0 25px;
  transition: all 0.3s;
}

/* 激活状态的下划线美化 */
.top-menu :deep(.el-menu-item.is-active) {
  position: relative;
  font-weight: bold;
}
.top-menu :deep(.el-menu-item.is-active::after) {
  content: "";
  position: absolute;
  bottom: 8px;
  left: 20%;
  right: 20%;
  height: 3px;
  background-color: #ffd04b;
  border-radius: 4px;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px 0; /* 左右留白交给内层 wrapper */
  height: calc(100% - 60px);
}

.content-wrapper {
  max-width: 1000px; /* 限制最大宽度，配合 AI 助手的堆叠布局 */
  margin: 0 auto;
  padding: 0 20px;
}

.header-right {
  margin-left: 20px;
}

/* 组件切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
