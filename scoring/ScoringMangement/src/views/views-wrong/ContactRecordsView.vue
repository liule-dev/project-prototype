<!-- src/views-wrong/ContactRecordsView.vue -->
<template>
  <div class="contact-records-view">
    <el-card class="header-card" shadow="hover">
      <div class="header-content">
        <h2>📝 练习记录</h2>
        <el-button type="primary" @click="fetchContactRecords" :icon="Refresh">
          刷新数据
        </el-button>
      </div>
    </el-card>

    <el-card class="content-card" shadow="hover">
      <el-table
        :data="contactRecords"
        style="width: 100%"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="record_time" label="练习时间" width="200" />
        <el-table-column prop="topic_number" label="题目编号" width="150" />
        <el-table-column prop="topic_knowledge" label="知识点" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../../api1/api.js'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

export default {
  name: 'ContactRecordsView',
  components: {
    Refresh
  },
  setup() {
    const contactRecords = ref([])
    const loading = ref(false)

    const fetchContactRecords = async () => {
      loading.value = true
      try {
        const response = await apiService.contactRecords.getByUser(1)
        contactRecords.value = response.data.data
      } catch (error) {
        console.error('获取练习记录失败:', error)
        ElMessage.error('获取练习记录失败')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchContactRecords()
    })

    return {
      contactRecords,
      loading,
      fetchContactRecords
    }
  }
}
</script>

<style scoped>
.contact-records-view {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.header-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.content-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.content-card :deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

.content-card :deep(.el-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
