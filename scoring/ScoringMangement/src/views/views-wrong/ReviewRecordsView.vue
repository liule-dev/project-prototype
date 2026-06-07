<!-- src/views-wrong/ReviewRecordsView.vue -->
<template>
  <div class="review-records-view">
    <el-card class="header-card" shadow="hover">
      <div class="header-content">
        <h2>📚 复习记录</h2>
        <el-button type="primary" @click="fetchReviewRecords" :icon="Refresh">
          刷新数据
        </el-button>
      </div>
    </el-card>

    <el-card class="content-card" shadow="hover">
      <el-table
        :data="reviewRecords"
        style="width: 100%"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="create_record_time" label="创建时间" width="200" />
        <el-table-column prop="topic_number" label="题目编号" width="150" />
        <el-table-column prop="review_time" label="复习时间" width="200" />
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
  name: 'ReviewRecordsView',
  components: {
    Refresh
  },
  setup() {
    const reviewRecords = ref([])
    const loading = ref(false)

    const fetchReviewRecords = async () => {
      loading.value = true
      try {
        const response = await apiService.reviewRecords.getByUser(1)
        reviewRecords.value = response.data.data
      } catch (error) {
        console.error('获取复习记录失败:', error)
        ElMessage.error('获取复习记录失败')
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchReviewRecords()
    })

    return {
      reviewRecords,
      loading,
      fetchReviewRecords
    }
  }
}
</script>

<style scoped>
.review-records-view {
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
