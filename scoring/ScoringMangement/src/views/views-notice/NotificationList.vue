<template>
  <div class="notification-shell">
    <div class="notification-card">
      <NotificationForm
        v-if="showCreateForm"
        v-model="showCreateForm"
        @save="handleNotificationSaved"
        @cancel="showCreateForm = false"
      />

      <header class="header">
        <div class="header-left">
          <div class="title-icon"><el-icon><Bell /></el-icon></div>
          <div class="title-text">
            <h2>系统通知</h2>
            <p class="stats">共 {{ filteredNotifications.length }} 条，{{ unreadCount }} 条未读</p>
          </div>
        </div>

        <div class="header-actions">
          <div class="action-buttons">
            <el-button v-if="hasUnread" @click="handleMarkAllAsRead" type="success" plain round size="default">
              <el-icon><Check /></el-icon>全部标记已读
            </el-button>
            <el-button @click="handleDeleteRead" type="danger" plain round size="default">
              <el-icon><Delete /></el-icon>清空已读
            </el-button>
            <el-button @click="showCreateForm = true" v-if="role != 'student'" type="primary" round size="default">
              <el-icon><Plus /></el-icon>发布通知
            </el-button>
          </div>

          <div class="unread-pill" @click="fetchUnreadCount">
            <span class="pill-label">未读</span>
            <span class="pill-value">{{ unreadCount }}</span>
            <el-icon class="refresh-icon"><Refresh /></el-icon>
          </div>
        </div>
      </header>

      <div class="controls-bar">
        <el-radio-group v-model="filter" size="default" class="modern-radio">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="unread">未读</el-radio-button>
          <el-radio-button label="read">已读</el-radio-button>
        </el-radio-group>
      </div>

      <div class="content-body">
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="error" class="error-state">
          <el-result icon="error" title="加载失败" :sub-title="error">
            <template #extra>
              <el-button type="primary" @click="fetchNotifications">重试</el-button>
            </template>
          </el-result>
        </div>

        <template v-else>
          <div class="pagination-wrapper top" v-if="totalPages > 1">
            <el-pagination
              @current-change="handlePageChange"
              :current-page="currentPage"
              :page-size="pageSize"
              :total="filteredNotifications.length"
              layout="prev, pager, next"
              background
            />
          </div>

          <transition-group name="list-stagger" tag="ul" class="notification-items">
            <li v-for="notification in paginatedNotifications" :key="notification.id">
              <NotificationItem
                :notification="notification"
                @mark-read="handleMarkRead"
                @delete="handleDelete"
              />
            </li>
          </transition-group>

          <div v-if="paginatedNotifications.length === 0" class="empty-state">
            <el-empty description="暂无通知记录" :image-size="160" />
          </div>

          <div class="pagination-wrapper bottom" v-if="totalPages > 1">
            <el-pagination
              @current-change="handlePageChange"
              :current-page="currentPage"
              :page-size="pageSize"
              :total="filteredNotifications.length"
              layout="total, prev, pager, next, jumper"
              background
            />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/* 你的逻辑部分完全保持不动，仅引入必要的图标 */
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Check, Delete, Plus, Refresh } from '@element-plus/icons-vue'
import {
  getNotifications,
  markAsRead,
  deleteNotification,
  markAllAsRead,
  getUnreadCount,
  batchMarkAsRead,
  deleteReadNotifications,
  type Notification
} from '../../api1/notificationApi'
import NotificationItem from './NotificationItem.vue'
import NotificationForm from './NotificationForm.vue'

const notifications = ref<Notification[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const filter = ref<'all' | 'read' | 'unread'>('all')
const unreadCountRef = ref(0)
const router = useRouter()
const showCreateForm = ref(false)
const role = localStorage.getItem('role')
const currentPage = ref(1)
const pageSize = ref(10)

// ... 以下逻辑代码与你提供的完全一致 ...
const fetchNotifications = async () => {
  try {
    error.value = null
    loading.value = true
    const response = await getNotifications()
    notifications.value = response.data
  } catch (err: any) {
    console.error('获取通知失败:', err)
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('access_token')
      router.push('/login')
      return
    }
    error.value = '获取通知失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const fetchUnreadCount = async () => {
  try {
    const response = await getUnreadCount()
    unreadCountRef.value = response.data.unread_count
  } catch (err: any) {
    console.error('获取未读通知数量失败:', err)
  }
}

watch(() => router.currentRoute.value, () => {
  fetchNotifications()
  fetchUnreadCount()
})

onMounted(() => {
  fetchNotifications()
  fetchUnreadCount()
})

const filteredNotifications = computed(() => {
  if (filter.value === 'all') return notifications.value
  if (filter.value === 'unread') return notifications.value.filter(n => !n.is_read)
  return notifications.value.filter(n => n.is_read)
})

const totalPages = computed(() => Math.ceil(filteredNotifications.value.length / pageSize.value))
const paginatedNotifications = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredNotifications.value.slice(start, start + pageSize.value)
})

const handlePageChange = (page: number) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(filter, () => { currentPage.value = 1 })

const handleMarkRead = async (id: number) => {
  try {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) notifications.value[index].is_read = true
    await batchMarkAsRead({ notification_ids: [id] })
    fetchUnreadCount()
  } catch (err: any) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) notifications.value[index].is_read = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await deleteNotification(id)
    notifications.value = notifications.value.filter(n => n.id !== id)
    fetchUnreadCount()
  } catch (err: any) {}
}

const hasUnread = computed(() => notifications.value.some(notification => !notification.is_read))
const unreadCount = computed(() => unreadCountRef.value)

const handleMarkAllAsRead = async () => {
  try {
    await markAllAsRead()
    notifications.value.forEach(notification => { notification.is_read = true })
    fetchUnreadCount()
  } catch (err: any) {}
}

const handleDeleteRead = async () => {
  try {
    await deleteReadNotifications()
    notifications.value = notifications.value.filter(n => !n.is_read)
    fetchUnreadCount()
  } catch (err: any) {}
}

const handleNotificationSaved = (notification: Notification) => {
  notifications.value.unshift(notification)
  fetchUnreadCount()
  showCreateForm.value = false
}
</script>

<style scoped>
/* 样式设计遵循上一条回答的沉浸式风格 */

.notification-shell {
  padding: 24px;
  background: transparent; /* 依托背景主页的渐变 */
  min-height: 100%;
}

.notification-card {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  max-width: 1000px;
  margin: 0 auto;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #4c77a0, #8ea3ca);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.title-text h2 {
  margin: 0;
  font-size: 22px;
  color: #334155;
  font-weight: 700;
}

.stats {
  margin: 4px 0 0;
  font-size: 13px;
  color: #94a3b8;
}

/* 按钮与药丸 */
.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.unread-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 50px;
  cursor: pointer;
  transition: 0.3s;
}

.unread-pill:hover {
  background: #f1f5f9;
  border-color: #4c77a0;
}

.pill-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.pill-value {
  font-size: 14px;
  color: #4c77a0;
  font-weight: 700;
}

.refresh-icon {
  font-size: 14px;
  color: #94a3b8;
}

/* 筛选条 */
.controls-bar {
  padding: 15px 0;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 20px;
}

/* 现代单选按钮样式 */
:deep(.modern-radio .el-radio-button__inner) {
  border-radius: 8px !important;
  margin-right: 8px;
  border: 1px solid #e2e8f0 !important;
  box-shadow: none !important;
}

:deep(.modern-radio .el-radio-button:first-child .el-radio-button__inner) {
  border-left: 1px solid #e2e8f0 !important;
}

:deep(.modern-radio .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #4c77a0;
  border-color: #4c77a0 !important;
  color: #fff;
}

/* 列表动画 */
.notification-items {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.pagination-wrapper.top {
  border-bottom: 1px solid #f8fafc;
  margin-bottom: 20px;
}

/* 列表进入/离开动画 */
.list-stagger-enter-active,
.list-stagger-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-stagger-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.list-stagger-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 20px;
  }
  .header-actions {
    align-items: flex-start;
    width: 100%;
  }
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
