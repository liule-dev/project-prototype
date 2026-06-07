<template>
  <div class="ai-assistant-container">
    <el-row :gutter="20" class="main-layout">
      <el-col :xs="24" :md="9" :lg="8">
        <el-card class="box-card tool-panel" shadow="always">
          <template #header>
            <div class="card-header">
              <span class="header-title">🛠️ 智能辅助工具</span>
            </div>
          </template>

          <el-tabs v-model="activeTab" type="border-card" class="custom-tabs">
            <el-tab-pane name="plan">
              <template #label>
                <i class="el-icon-date"></i> 制定计划
              </template>
              <el-form :model="studyPlanForm" label-position="top" class="plan-form">
                <el-form-item label="学习科目">
                  <el-input v-model="studyPlanForm.subjects" placeholder="如：数学, 英语, 物理" clearable />
                </el-form-item>
                <el-form-item label="时间跨度">
                  <el-select v-model="studyPlanForm.timeFrame" style="width: 100%">
                    <el-option label="📅 一周" value="weekly" />
                    <el-option label="📆 一个月" value="monthly" />
                    <el-option label="🗓️ 三个月" value="quarterly" />
                  </el-select>
                </el-form-item>
                <el-form-item label="核心目标">
                  <el-input
                    v-model="studyPlanForm.goals"
                    type="textarea"
                    :rows="4"
                    placeholder="例如：准备期末考试，掌握函数基础"
                  />
                </el-form-item>
                <el-button
                  type="primary"
                  class="action-btn"
                  @click="generateStudyPlan"
                  :loading="studyPlanLoading"
                  round
                >
                  🚀 生成学习计划
                </el-button>
              </el-form>

              <div v-if="studyPlanResult" class="result-display plan-res">
                <h5>📋 计划预览：</h5>
                <div class="markdown-body" v-html="studyPlanResult"></div>
              </div>
            </el-tab-pane>

            <el-tab-pane name="analysis">
              <template #label>
                <i class="el-icon-pie-chart"></i> 错题分析
              </template>
              <div class="analysis-center">
                <el-empty v-if="!analysisResult" description="分析错题本以获得针对性建议">
                  <el-button
                    type="success"
                    @click="analyzeWrongTopics"
                    :loading="analysisLoading"
                    round
                  >
                    🔍 开始深度分析
                  </el-button>
                </el-empty>

                <div v-else class="result-display analysis-res">
                  <h5>📈 分析报告：</h5>
                  <div v-html="analysisResult"></div>
                  <el-button size="small" style="margin-top: 15px" @click="analysisResult = ''">重置分析</el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="15" :lg="16">
        <el-card class="box-card chat-panel" shadow="always">
          <template #header>
            <div class="chat-header">
              <div class="status-info">
                <span class="header-title">💬 AI 学习助手</span>
                <el-tag size="small" type="success" effect="dark" class="status-tag">在线</el-tag>
              </div>
              <el-button type="text" @click="chatMessages = []">清空对话记录</el-button>
            </div>
          </template>

          <div class="chat-container">
            <div class="chat-history" ref="chatHistory">
              <div v-if="chatMessages.length === 0" class="welcome-message">
                <p>你好！我是你的 AI 学习伙伴。你可以问我：</p>
                <el-tag @click="userInput = '如何高效背单词？'">如何高效背单词？</el-tag>
                <el-tag @click="userInput = '帮我解释一下勾股定理'">解释勾股定理</el-tag>
              </div>

              <div
                v-for="(msg, index) in chatMessages"
                :key="index"
                :class="['message-wrapper', msg.type]"
              >
                <div class="avatar">{{ msg.type === 'user' ? '👤' : '🤖' }}</div>
                <div class="message-content-box">
                  <div class="message-bubble">{{ msg.content }}</div>
                  <div class="message-time">{{ msg.time }}</div>
                </div>
              </div>

              <div v-if="chatLoading" class="message-wrapper ai">
                <div class="avatar">🤖</div>
                <div class="message-bubble loading-dots">正在思考中...</div>
              </div>
            </div>

            <div class="chat-input-wrapper">
              <el-input
                v-model="userInput"
                placeholder="在此输入您的问题 (按回车发送)..."
                @keyup.enter="sendMessage"
                :disabled="chatLoading"
                size="large"
              >
                <template #append>
                  <el-button @click="sendMessage" :loading="chatLoading" type="primary">
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'
import apiService from '../../api1/api.js'
import { ElMessage } from 'element-plus'

export default {
  name: 'AIAssistantView',
  setup() {
    // 基础状态
    const activeTab = ref('plan')
    const studyPlanForm = ref({ subjects: '', timeFrame: 'weekly', goals: '' })
    const studyPlanLoading = ref(false)
    const analysisLoading = ref(false)
    const studyPlanResult = ref('')
    const analysisResult = ref('')

    // 聊天状态
    const chatMessages = ref([])
    const userInput = ref('')
    const chatLoading = ref(false)
    const chatHistory = ref(null)

    // 生成计划逻辑
    const generateStudyPlan = async () => {
      if (!studyPlanForm.value.subjects || !studyPlanForm.value.goals) {
        ElMessage.warning('请填写完整的表单信息')
        return
      }
      studyPlanLoading.value = true
      try {
        const response = await apiService.ai.generateStudyPlan({
          subjects: studyPlanForm.value.subjects.split(',').map(s => s.trim()),
          time_frame: studyPlanForm.value.timeFrame,
          goals: studyPlanForm.value.goals
        })
        studyPlanResult.value = response.data.data.study_plan
        ElMessage.success('学习计划生成成功')
      } catch (error) {
        ElMessage.error(`生成失败: ${error.message}`)
      } finally {
        studyPlanLoading.value = false
      }
    }

    // 错题分析逻辑
    const analyzeWrongTopics = async () => {
      analysisLoading.value = true
      try {
        const response = await apiService.ai.analyzeWrongTopics(1)
        const obj = response.data.data.analysis;
        analysisResult.value = `
          <div class="analysis-card">
            <p>📌 <strong>错题总数：</strong> ${obj.total_wrong_topics} 道</p>
            <p>🔥 <strong>薄弱知识点：</strong> ${obj.most_error_knowledge}</p>
            <p>💡 <strong>提分建议：</strong> ${obj.suggestion}</p>
          </div>
        `;
        ElMessage.success('分析成功')
      } catch (error) {
        ElMessage.error('分析失败')
      } finally {
        analysisLoading.value = false
      }
    }

    // 聊天逻辑
    const sendMessage = async () => {
      if (!userInput.value?.trim() || chatLoading.value) return

      const msg = userInput.value
      chatMessages.value.push({
        type: 'user',
        content: msg,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })

      userInput.value = ''
      chatLoading.value = true
      scrollToBottom()

      try {
        const response = await apiService.ai.chatWithAI({ message: msg, user_id: 1 })
        chatMessages.value.push({
          type: 'ai',
          content: response.data.data.reply,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        })
      } catch (error) {
        chatMessages.value.push({ type: 'error', content: '服务响应异常，请稍后再试。', time: 'Error' })
      } finally {
        chatLoading.value = false
        scrollToBottom()
      }
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (chatHistory.value) {
          chatHistory.value.scrollTop = chatHistory.value.scrollHeight
        }
      })
    }

    return {
      activeTab, studyPlanForm, studyPlanLoading, analysisLoading,
      studyPlanResult, analysisResult, chatMessages, userInput,
      chatLoading, chatHistory, generateStudyPlan, analyzeWrongTopics, sendMessage
    }
  }
}
</script>

<style scoped>
/* 容器布局 */
.ai-assistant-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.main-layout {
  height: 100%;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/* 通用卡片样式 */
.box-card {
  border-radius: 12px;
  border: none;
  height: 750px; /* 统一高度 */
  display: flex;
  flex-direction: column;
}

/* 左侧工具栏微调 */
.tool-panel :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.custom-tabs {
  height: 100%;
  border: none;
}

.plan-form {
  padding: 10px 5px;
}

.action-btn {
  width: 100%;
  margin-top: 10px;
}

.result-display {
  margin-top: 20px;
  padding: 15px;
  background: #fdfdfd;
  border-radius: 8px;
  border: 1px solid #eef1f6;
  font-size: 14px;
  line-height: 1.6;
}

/* 聊天面板样式 */
.chat-panel :deep(.el-card__body) {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-tag {
  margin-left: 10px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f9fbff;
}

.chat-history {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 聊天气泡设计 */
.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  margin: 0 12px;
  font-size: 20px;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-all;
  position: relative;
}

.user .message-bubble {
  background-color: #409eff;
  color: #fff;
  border-top-right-radius: 2px;
}

.ai .message-bubble {
  background-color: #fff;
  color: #333;
  border-top-left-radius: 2px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  text-align: inherit;
}

.user .message-time { text-align: right; }

/* 输入框区域 */
.chat-input-wrapper {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.welcome-message .el-tag {
  margin: 5px;
  cursor: pointer;
}

/* 滚动条优化 */
.chat-history::-webkit-scrollbar { width: 6px; }
.chat-history::-webkit-scrollbar-thumb { background: #e0e3e9; border-radius: 3px; }

.loading-dots {
  color: #909399;
  font-style: italic;
}
</style>
