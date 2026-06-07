<template>
  <div class="notification-item" :class="{ unread: !notification.is_read }">
    <div class="header">
      <div class="title-wrapper">
        <span class="status-indicator" :class="{ unread: !notification.is_read }"></span>
        <span class="title">{{ notification.title }}</span>
        <span class="type-badge" :class="notification.type">{{ getNotificationTypeText(notification.type) }}</span>
      </div>
      <span class="time">{{ formatTime(notification.created_at) }}</span>
    </div>
    <div class="content">{{ notification.content }}</div>
    <div class="actions">
      <button
        v-if="!notification.is_read"
        @click="$emit('mark-read', notification.id)"
        class="mark-read-btn"
      >
        <i class="icon-check"></i>
        标记已读
      </button>
      <button @click="$emit('delete', notification.id)" class="delete-btn">
        <i class="icon-delete"></i>
        删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'
import { Notification } from '../../api1/notificationApi'

interface Props {
  notification: Notification
}

defineProps<Props>()
defineEmits<{
  (e: 'mark-read', id: number): void
  (e: 'delete', id: number): void
}>()

const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

  if (diffInDays === 0) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diffInDays === 1) {
    return '昨天 ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else if (diffInDays < 7) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return weekdays[date.getDay()] + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
}

const getNotificationTypeText = (type: string) => {
  // 后端定义的6种通知类型
  const typeMap: Record<string, string> = {
    '考试通知': '考试通知',
    '成绩通知': '成绩通知',
    '题目审核通知': '题目审核通知',
    '系统公告通知': '系统公告通知',
    '错题本更新通知': '错题本更新通知',
    '学习计划推荐通知': '学习计划推荐通知'
  }
  return typeMap[type] || '通知'
}
</script>

<style scoped>
.notification-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.notification-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.notification-item.unread {
  background-color: #e3f2fd;
  border-left: 4px solid #2196F3;
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: #2196F3;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  background: #9e9e9e;
}

.status-indicator.unread {
  background: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.title {
  font-weight: 600;
  color: #333;
  font-size: 1.1em;
}

.type-badge {
  background: #e0e0e0;
  color: #666;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
  white-space: nowrap;
}

.type-badge.考试通知 {
  background: #2196F3;
  color: white;
}

.type-badge.成绩通知 {
  background: #4CAF50;
  color: white;
}

.type-badge.题目审核通知 {
  background: #FF9800;
  color: white;
}

.type-badge.系统公告通知 {
  background: #9C27B0;
  color: white;
}

.type-badge.错题本更新通知 {
  background: #f44336;
  color: white;
}

.type-badge.学习计划推荐通知 {
  background: #009688;
  color: white;
}

.time {
  color: #666;
  font-size: 0.85em;
  white-space: nowrap;
  margin-left: 10px;
  text-align: right;
}

.content {
  color: #444;
  line-height: 1.6;
  margin-bottom: 16px;
  font-size: 0.95em;
}

.actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.9em;
  transition: all 0.2s ease;
}

.mark-read-btn {
  background: #2196F3;
  color: white;
}

.mark-read-btn:hover {
  background: #0b7dda;
}

.delete-btn {
  background: #f44336;
  color: white;
}

.delete-btn:hover {
  background: #d32f2f;
}

.icon-check::before {
  content: '✓';
}

.icon-delete::before {
  content: '✕';
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notification-item {
    padding: 12px;
  }

  .header {
    flex-direction: column;
    gap: 8px;
  }

  .title-wrapper {
    width: 100%;
  }

  .title {
    font-size: 1rem;
  }

  .time {
    margin-left: 0;
    font-size: 0.8rem;
  }

  .content {
    font-size: 0.9rem;
    margin-bottom: 12px;
  }

  .actions {
    gap: 5px;
  }

  button {
    padding: 5px 10px;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .notification-item {
    padding: 10px;
    margin-bottom: 8px;
  }

  .title {
    font-size: 0.95rem;
  }

  .content {
    font-size: 0.85rem;
  }

  button {
    padding: 4px 8px;
  }
}
</style>
