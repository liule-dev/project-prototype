<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'

import { onMounted } from 'vue'



</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="centered-title">通知中心</h1>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* 全局样式保留 */
:root {
  --color-background: #f5f7fa;
  --color-border: #ddd;
  --color-text: #333;
  --section-gap: 160px;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
}

#app {
  min-height: 100vh;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem 2rem;
  display: flex;
  /* 改为居中对齐而非两端对齐 */
  justify-content: center;
  align-items: center;
}

/* 标题样式优化 */
.centered-title {
  margin: 0;
  color: #2c3e50;
  text-align: center;
  font-size: 1.8rem;
}

.refresh-btn {
  margin-right: 20px;
  color: #2196F3;
  background: none;
  border: 1px solid #2196F3;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.refresh-btn:hover {
  background-color: #2196F3;
  color: white;
}

.unread-count {
  background: #f44336;
  color: white;
  border-radius: 12px;
  padding: 0.25rem 0.75rem;
  font-size: 0.9rem;
}

.app-main {
  flex: 1;
  padding: 1rem 0;
}
</style>
