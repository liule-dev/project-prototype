<template>
  <div class="notification-form">
    <h3>{{ isEditing ? '编辑通知' : '创建新通知' }}</h3>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="title">标题:</label>
        <input
          id="title"
          v-model="formData.title"
          type="text"
          required
        />
      </div>

      <div class="form-group">
        <label for="content">内容:</label>
        <textarea
          id="content"
          v-model="formData.content"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="type">通知类型:</label>
        <select id="type" v-model="formData.type" required>
          <option
            v-for="type in availableNotificationTypes"
            :key="type"
            :value="type"
          >
            {{ type }}
          </option>
        </select>
      </div>

      <div class="form-actions">
        <button type="submit" :disabled="loading">
          {{ loading ? '处理中...' : (isEditing ? '更新通知' : '创建通知') }}
        </button>
        <button type="button" @click="cancel" class="cancel-btn">取消</button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { createNotification, type CreateNotificationRequest, type Notification } from '../../api1/notificationApi'
import { useRouter } from 'vue-router'

// 获取用户角色信息
const userRole = ref<string | null>(null)
const router = useRouter()

// 在组件加载时获取用户信息
onMounted(() => {
  const storedRole = localStorage.getItem('role')
  if (storedRole) {
    userRole.value = storedRole
  }


})

// 根据用户角色定义可创建的通知类型
const getAvailableNotificationTypes = () => {
  if (!userRole.value) return []

  switch (userRole.value) {
    case 'admin':
      return ['考试通知', '成绩通知', '题目审核通知', '系统公告通知', '错题本更新通知', '学习计划推荐通知']
    case 'teacher':
      return ['考试通知', '成绩通知', '题目审核通知', '学习计划推荐通知']
    case 'student':
      return ['题目审核通知']
    default:
      return []
  }
}

// 计算属性，用于模板中动态显示可用的通知类型
const availableNotificationTypes = computed(() => getAvailableNotificationTypes())

const props = defineProps<{
  modelValue: boolean
  notification?: Notification | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', notification: Notification): void
  (e: 'cancel'): void
}>()

const isEditing = ref(false)
const loading = ref(false)
const error = ref('')

const formData = ref<CreateNotificationRequest>({
  title: '',
  content: '',
  type: availableNotificationTypes.value.length > 0 ? availableNotificationTypes.value[0] : '系统公告通知'
})

// 监听notification prop变化
watch(() => props.notification, (newVal) => {
  if (newVal) {
    isEditing.value = true
    formData.value = {
      title: newVal.title,
      content: newVal.content,
      type: newVal.type
    }
  } else {
    isEditing.value = false
    resetForm()
  }
})

const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    type: availableNotificationTypes.value.length > 0 ? availableNotificationTypes.value[0] : '系统公告通知'
  }
  error.value = ''
}

const handleSubmit = async () => {
  try {
    loading.value = true
    error.value = ''

    // 验证用户是否有权限创建该类型的通知
    if (!userRole.value) {
      error.value = '请先登录'
      return
    }

    const availableTypes = getAvailableNotificationTypes()
    if (!availableTypes.includes(formData.value.type)) {
      error.value = `您的角色(${userRole.value})没有权限创建${formData.value.type}类型的通知`
      return
    }

    // 创建新通知
    const response = await createNotification(formData.value)
    emit('save', response.data)
    resetForm()
    emit('update:modelValue', false)

    // 创建通知完成后刷新页面
    setTimeout(() => {
      router.go(0)
    }, 500)
  } catch (err: unknown) {
    console.error('创建通知失败:', err)
    // 添加类型断言以避免类型错误
    if (err instanceof Error) {
      error.value = err.message || '创建通知失败，请稍后重试'
    } else {
      error.value = '创建通知失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const cancel = () => {
  resetForm()
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.notification-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.notification-form h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button[type="submit"] {
  background-color: #2196F3;
  color: white;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #0b7dda;
}

button[type="submit"]:disabled {
  background-color: #bbdefb;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.error-message {
  color: #f44336;
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}
</style>
