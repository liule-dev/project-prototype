<!-- src/views-wrong/WrongTopicsView.vue -->
<template>
  <div class="wrong-topics-view">
    <el-card class="header-card" shadow="hover">
      <div class="header-content">
        <h2>📘 错题本</h2>
        <el-button type="primary" @click="fetchWrongTopics" :icon="Refresh">
          刷新数据
        </el-button>
      </div>
    </el-card>

    <el-card class="content-card" shadow="hover">
      <el-table
        :data="wrongTopics"
        style="width: 100%"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="topic_number" label="题目编号" width="120" />
        <el-table-column prop="error_times" label="错误次数" width="100" align="center">
          <template #default="scope">
            <el-tag type="danger">{{ scope.row.error_times }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="topic_knowledge" label="知识点" />
        <el-table-column prop="active" label="掌握状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.active ? 'danger' : 'success'">
              {{ scope.row.active ? '未掌握' : '已掌握' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              @click="viewTopicDetail(scope.row)"
              round
              style="margin-right: 8px;"
            >
              查看题目
            </el-button>
            <el-button
              size="small"
              type="success"
              @click="markAsMastered(scope.row.id)"
              :disabled="!scope.row.active"
              round
            >
              标记掌握
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="ai-card" v-if="analysisResult" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>🤖 AI分析结果</h3>
        </div>
      </template>
      <div class="analysis-content" v-html="analysisResult"></div>
    </el-card>

    <!-- 题目详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="题目详情" 
      width="70%"
      top="5vh"
    >
      <div v-if="currentTopic" class="topic-detail">
        <!-- 题目内容 -->
        <div class="detail-section question-content">
          <h4>📝 题目内容</h4>
          <p>{{ currentTopic.topic_content }}</p>
        </div>

        <!-- 标准答案 -->
        <div class="detail-section standard-answer">
          <h4>✅ 标准答案</h4>
          <p>{{ currentTopic.topic_answer || '暂无' }}</p>
        </div>

        <!-- 题目解析 -->
        <div class="detail-section analysis">
          <h4>💡 题目解析</h4>
          <p>{{ currentTopic.topic_analysis || '暂无解析' }}</p>
        </div>

        <!-- 用户答案 -->
        <div class="detail-section user-answer">
          <h4>👤 你的答案</h4>
          <p>{{ currentUserAnswer || '未作答' }}</p>
        </div>

        <!-- 知识点 -->
        <div class="detail-section knowledge">
          <h4>📚 知识点</h4>
          <p>{{ currentTopic.topic_knowledge || '暂无' }}</p>
        </div>

        <!-- 错误次数 -->
        <div class="detail-section error-info">
          <h4>📊 错误统计</h4>
          <p>错误次数: {{ currentTopic.error_times }} 次</p>
        </div>
      </div>
      <div v-else>
        <p class="no-data">加载中...</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../../api1/api.js'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

export default {
  name: 'WrongTopicsView',
  components: {
    Refresh
  },
  setup() {
    const wrongTopics = ref([])
    const loading = ref(false)
    const analysisResult = ref('')
    
    // 题目详情相关
    const detailDialogVisible = ref(false)
    const currentTopic = ref(null)
    const currentUserAnswer = ref('')

    const fetchWrongTopics = async () => {
      loading.value = true
      try {
        // 获取当前登录用户ID
        const userId = localStorage.getItem('userId') || 1
        console.log('当前用户ID:', userId)
        
        const response = await apiService.wrongTopics.getByUser(userId)
        console.log('API Response:', response)
        wrongTopics.value = response.data.data
      } catch (error) {
        console.error('获取错题失败:', error)
        ElMessage.error('获取错题数据失败')
      } finally {
        loading.value = false
      }
    }

    const markAsMastered = async (wrongTopicId) => {
      try {
        await apiService.wrongTopics.updateStatus(wrongTopicId)
        ElMessage.success('标记成功')
        fetchWrongTopics()
      } catch (error) {
        console.error('标记失败:', error)
        ElMessage.error('标记失败')
      }
    }

    const analyzeWrongTopics = async () => {
      try {
        // 获取当前登录用户ID
        const userId = localStorage.getItem('userId') || 1
        const response = await apiService.ai.analyzeWrongTopics(userId)
        analysisResult.value = response.data.analysis
      } catch (error) {
        console.error('AI分析失败:', error)
        ElMessage.error('AI分析失败')
      }
    }

    // 查看题目详情
    const viewTopicDetail = async (wrongTopic) => {
      try {
        loading.value = true
        // 获取token（使用正确的key名称：access_token）
        const token = localStorage.getItem('access_token')
        
        console.log('获取到的Token:', token ? '存在' : '不存在')
        
        if (!token) {
          ElMessage.warning('请先登录')
          loading.value = false
          return
        }
        
        // 获取题目详细信息
        const response = await fetch(`http://localhost:8000/topic/${wrongTopic.topic_number}/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          if (response.status === 401) {
            ElMessage.error('认证失败，请重新登录')
            throw new Error('认证失败')
          }
          throw new Error(`获取题目详情失败: ${response.status}`)
        }
        
        const data = await response.json()
        currentTopic.value = { ...data, error_times: wrongTopic.error_times }
        
        // 获取用户答案（从答题详情中获取）
        currentUserAnswer.value = wrongTopic.user_answer || '未找到答案记录'
        
        detailDialogVisible.value = true
      } catch (error) {
        console.error('获取题目详情失败:', error)
        if (error.message !== '认证失败') {
          ElMessage.error('获取题目详情失败: ' + error.message)
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchWrongTopics()
    })

    return {
      wrongTopics,
      loading,
      analysisResult,
      fetchWrongTopics,
      markAsMastered,
      analyzeWrongTopics,
      // 题目详情相关
      detailDialogVisible,
      currentTopic,
      currentUserAnswer,
      viewTopicDetail
    }
  }
}
</script>

<style scoped>
.wrong-topics-view {
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

.ai-card {
  background-color: #f0f9ff;
  border-radius: 8px;
}

.card-header h3 {
  margin: 0;
  color: #409eff;
}

.analysis-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

/* 题目详情样式 */
.topic-detail {
  padding: 10px;
}

.detail-section {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
  background-color: #f9fafb;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 16px;
  font-weight: 600;
}

.detail-section p {
  margin: 0;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
}

.question-content {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.standard-answer {
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.analysis {
  background-color: #fff3e0;
  border-left: 4px solid #ff9800;
}

.user-answer {
  background-color: #fce4ec;
  border-left: 4px solid #e91e63;
}

.knowledge {
  background-color: #f3e5f5;
  border-left: 4px solid #9c27b0;
}

.error-info {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 30px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
