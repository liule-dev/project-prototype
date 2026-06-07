<template>
  <header class="main-header">
    <div class="header-container">
      <h1 class="system-title">
        <i class="icon-doc"></i> 医疗问答系统
      </h1>
    </div>
  </header>

</template>

<script setup>
import { ref, watch } from 'vue';
import router from "@/router/router.js";
// 必须先获取路由实例，再调用push
// 正确示例：必须调用next()放行
const goToAI = () => {
  // Vue3 中可通过catch捕获导航异常
  router.push('/ai').catch(err => {
    console.log('跳转异常：', err); // 若重复跳转，会捕获到导航异常信息
  });
};

const props = defineProps({
  searchInput: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['modelDialog', 'update:searchInput']);

const isSearchFocused = ref(false);
const localSearchInput = ref(props.searchInput);

// 监听外部值变化
watch(() => props.searchInput, (newVal) => {
  localSearchInput.value = newVal;
});

// 监听内部值变化并同步到父组件
watch(localSearchInput, (newVal) => {
  emit('update:searchInput', newVal);
});

const emitModelDialog = () => {
  emit('modelDialog');
};
</script>

<style scoped>
.main-header {
  background: linear-gradient(135deg, #2d6a4f, #1b4332);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px 0;
}

.header-container {
  width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.system-title {
  color: #ffffff;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.system-title .icon-doc {
  display: inline-block;
  width: 28px;
  height: 28px;
  background-color: #ffffff;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='currentColor' d='M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm12 6v2h-8v-2h8z'/%3E%3C/svg%3E") no-repeat center;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='currentColor' d='M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm12 6v2h-8v-2h8z'/%3E%3C/svg%3E") no-repeat center;
}

.search-area {
  width: 500px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 8px;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.search-wrapper:focus-within {
  border-color: #74c69d;
  box-shadow: 0 0 0 3px rgba(116, 198, 157, 0.2);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 10px 12px;
  font-size: 14px;
  color: #2d3748;
  background: transparent;
}

.search-input::placeholder {
  color: #a0aec0;
}

.model-btn {
  background: linear-gradient(135deg, #40916c, #2d6a4f);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.model-btn .icon-chat {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: #ffffff;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='currentColor' d='M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z'/%3E%3C/svg%3E") no-repeat center;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='currentColor' d='M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z'/%3E%3C/svg%3E") no-repeat center;
}

.model-btn:hover {
  background: linear-gradient(135deg, #48bb78, #38a169);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.model-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
</style>
