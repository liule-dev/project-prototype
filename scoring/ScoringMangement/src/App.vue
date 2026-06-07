<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { onMounted } from 'vue'
import authService from '@/services/authService'

const store = useStore()
const router = useRouter()

// 页面加载时获取用户信息
</script>

<template>
  <div class="common-layout">
    <router-view />
  </div>
</template>

<style scoped>
.common-layout {
  height: 100vh;
}

.header-right {
  float: right;
  height: 100%;
  display: flex;
  align-items: center;
  padding-right: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #333;
  display: flex;
  align-items: center;
}
</style>
