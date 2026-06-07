<template>
  <div class="app-container">
    <div class="header">
      <h1>医疗知识助手</h1>
      <div class="status-indicator">
        <span class="status-dot" :class="wsStatus"></span>
        <span class="status-text">
          {{ wsStatus === "open" ? "已连接" : wsStatus === "error" ? "连接错误" : "未连接" }}
        </span>
      </div>
    </div>

    <div class="chat-card">
      <!-- 聊天内容区域 -->
      <div class="chat-box">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role]"
        >
          <div class="avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else-if="msg.role === 'assistant'">🤖</span>
            <span v-else>⚠️</span>
          </div>

          <div class="message-bubble" v-html="marked(msg.text)"></div>

          <!-- 显示用户或助手消息中的图片（旧版兼容） -->
          <img
            v-if="msg.image"
            style="width: 200px; height: 200px; margin-top: 10px; border-radius: 8px;"
            :src="msg.image"
            alt="图片"
          />

          <!-- ✅ 新增：显示检索到的图片列表（MinIO URLs） -->
          <div v-if="msg.imageUrls && msg.imageUrls.length > 0" class="image-grid">
            <div
              v-for="(img, idx) in msg.imageUrls"
              :key="idx"
              class="image-card"
            >
              <div class="image-wrapper">
                <img
                  :src="img.url"
                  :alt="img.filename || '医疗影像'"
                  class="result-image"
                  @error="handleImageError($event, img.url)"
                  @load="onImageLoad($event)"
                />
                <!-- 加载中的提示 -->
                <div v-if="!img.loaded && !img.error" class="loading-overlay">
                  <span>加载中...</span>
                </div>
              </div>

              <div class="image-info">
                <span class="similarity-tag">相似度：{{ (img.similarity * 100).toFixed(2) }}%</span>
                <span v-if="img.filename" class="filename">{{ img.filename }}</span>
              </div>
            </div>
          </div>
        </div>
        <!-- 空状态提示 -->
        <div class="empty-tip" v-if="messages.length === 0">
          开始对话吧！可以输入文字或上传图片提问~
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <!-- 图片上传区域 -->
        <div class="image-upload">
          <label class="upload-btn">
            📷 上传图片
            <input
              type="file"
              accept="image/*"
              @change="previewImage"
              hidden
            />
          </label>
          <div class="preview-container" v-if="preview">
            <img :src="preview" class="image-preview" />
            <button class="clear-preview" @click="preview = null; imageBase64 = null">✕</button>
          </div>
        </div>

        <!-- 文件上传区域 -->
        <div class="image-upload">
          <label class="upload-btn">
            📄 上传文件
            <input
              type="file"
              accept=""
              @change="previewfile"
              hidden
            />
          </label>
          <div class="preview-container" v-if="preview1">
            <div class="file-preview">
              <div class="file-icon">📄</div>
              <div class="file-info" v-if="selectedFileInfo">
                <div class="file-name">{{ selectedFileInfo.name }}</div>
                <div class="file-size">{{ formatFileSize(selectedFileInfo.size) }}</div>
              </div>
            </div>
            <button class="clear-preview" @click="preview1 = null; datafilebase64 = null; selectedFileInfo = null">✕</button>
          </div>
        </div>

        <!-- 文字输入框 -->
        <textarea
          v-model="question"
          placeholder="请输入您的问题...（支持图文结合提问）"
          :disabled="sending"
          class="question-input"
          @keydown="handleKeydown"
        ></textarea>

        <!-- 发送按钮 -->
        <button
          class="send-btn"
          @click="sendMessage"
          :disabled="sending || wsStatus !== 'open' || (!question.trim() && !imageBase64)"
        >
          {{ sending ? "发送中..." : "发送" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { marked } from 'marked';
import { onMounted, reactive, ref } from 'vue';

// WebSocket 配置 - 使用医疗助手的后端地址（异步版本）
const chat_url = "ws://localhost:8000/query/stream/async"; // 后端异步 WebSocket 地址
const ws = ref(null);
const wsStatus = ref("closed");
const question = ref("");
const sending = ref(false);
const preview = ref(null); // 图片预览数据
const preview1 = ref(null); // 文件预览数据
const datafilebase64 = ref(null);
const imageSrc = ref(null);
const messages = reactive([]);
const imageBase64 = ref(null);
const selectedFileInfo = ref(null);

// 获取当前用户ID作为session_id
const getUserId = () => {
  return localStorage.getItem('user_id') || 'guest_' + Date.now();
};

// ✅ 新增：图片加载成功处理函数
function onImageLoad(event) {
  const img = event.target;
  img.style.opacity = '1';

  // 移除加载提示
  const overlay = img.parentElement?.querySelector('.loading-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

// ✅ 新增：图片加载失败处理函数
function handleImageError(event, url) {
  console.error('🖼️ 图片加载失败:', url);

  const img = event.target;
  img.style.display = 'none';
  img.error = true; // 标记为错误状态

  // 查找父容器并添加错误提示
  const parent = img.closest('.image-card');
  if (parent && !parent.querySelector('.error-message')) {
    parent.innerHTML += `
      <div class="error-message">
        ⚠️ 图片加载失败
        <small style="display: block; margin-top: 4px; color: #94a3b8;">
          ${url.length > 50 ? url.substring(0, 50) + '...' : url}
        </small>
      </div>
    `;
  }
}

// WebSocket 连接函数
function connectWebSocket() {
  const userId = getUserId();
  // 在 WebSocket URL 中添加用户ID和会话ID作为查询参数
  const wsUrl = `${chat_url}?user_id=${userId}&session_id=${userId}`;
  
  ws.value = new WebSocket(wsUrl);

  ws.value.onopen = () => {
   wsStatus.value = "open";
    console.log("WebSocket 连接已打开", { userId });
    
    // 请求加载历史消息
    ws.value.send(JSON.stringify({ event: "load_history" }));
  };

  ws.value.onerror = () => {
   wsStatus.value = "error";
    console.log("WebSocket 连接出错");
  };

  ws.value.onclose = () => {
   wsStatus.value = "closed";
    console.log("WebSocket 连接已关闭");
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // 处理历史消息加载
    if (data.event === "history") {
      messages.length = 0; // 清空当前
      data.messages.forEach(msg => {
        messages.push({
          role: msg.role,
          text: msg.content,
          imageUrls: msg.imageUrls || []
        });
      });
      return;
    }

    if (data.event === "start") {
      sending.value = true;
      // 添加一个带有标识的消息，初始化 imageUrls 字段
      messages.push({ role: "assistant", text: "正在生成回答...", isGenerating: true, imageUrls: [] });
    }
    if (data.event === "delta") {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.isGenerating) {
        // 第一次接收内容时替换整个文本
        lastMessage.text = data.text;
        lastMessage.isGenerating = false;
      } else {
        // 后续内容追加到现有文本
        lastMessage.text += data.text;
      }
    }
    if (data.event === "end") {
      const lastMessage = messages[messages.length - 1];

      // ✅ 核心修改：处理后端返回的 images 数组（MinIO URLs）
      if (data.images && Array.isArray(data.images) && data.images.length > 0) {
        // 将图片 URLs 添加到消息中
        lastMessage.imageUrls = data.images.map(img => ({
          url: img.url,
          similarity: img.similarity,
          filename: img.filename || '',
          upload_time: img.upload_time || '',
          loaded: false,  // ✅ 新增：加载状态
          error: false    // ✅ 新增：错误状态
        }));
        console.log("收到后端返回的图片 URLs:", lastMessage.imageUrls);
      }

      // 兼容旧的 image 字段（如果有单个 Base64 图片）
      if (data.image && !data.images) {
        if (data.image.startsWith('data:image')) {
          lastMessage.imageUrls = [{ url: data.image, loaded: false, error: false }];
        } else {
          lastMessage.imageUrls = [{ url: `data:image/png;base64,${data.image}`, loaded: false, error: false }];
        }
      }

      sending.value = false;
      if (data.error) {
        messages.push({ role: "system", text: "错误：" + data.message });
      }
    }
    // ✅ 新增：处理后端报错事件
    if (data.event === "error") {
      sending.value = false;
      messages.push({ role: "system", text: "系统处理出错：" + data.message });
    }
  };
}

// 图片选择之后的处理
function previewImage(event) {
  const file = event.target.files[0]; // 获取选择的图片对象
  if (file) {
    const reader= new FileReader();
    reader.onload = (e) => {
      preview.value = e.target.result;
      imageBase64.value = e.target.result.split(",")[1]; // 提取 base64 数据部分
    };
    reader.readAsDataURL(file);
  }
}

function previewfile(event) {
  const file = event.target.files && event.target.files[0];
  if (file) {
    // 保存文件信息
    selectedFileInfo.value = {
      name: file.name,
      size: file.size,
      type: file.type
    };

    const reader = new FileReader();
    reader.onload = (e) => {
      preview1.value = e.target.result;
      datafilebase64.value = e.target.result.split(",")[1];
    };
    reader.readAsDataURL(file);
  }
}

// 处理键盘事件
function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 发送消息函数
function sendMessage() {
  if (wsStatus.value !== "open") {
    alert("WebSocket 未连接，无法发送消息");
    return;
  }

  const userQuestion = question.value.trim();

  // ✅ 新增：强校验，防止空内容发送（兼容键盘回车触发）
  if (!userQuestion && !imageBase64.value) {
    return;
  }

  // 消息列表追加用户内容
  messages.push({
    role: "user",
    text: userQuestion,
    image: preview.value
  });

  // 构造 JSON 数据发送 base64
  const dataToSend = {
    question: userQuestion,
    image: imageBase64.value,      // 图片 base64 字符串
   file: datafilebase64.value    // 文件 base64 字符串
  };

  ws.value.send(JSON.stringify(dataToSend));

  // 清空输入
  question.value = "";
  preview.value = null;
  preview1.value = null;
  imageBase64.value = null;
  datafilebase64.value = null;
  selectedFileInfo.value = null;
}


// 在组件挂载的时候执行连接
onMounted(() => connectWebSocket());
</script>
<style scoped>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Inter", "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 主容器 - 更宽且自适应 */
.app-container {
  width: 1200px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 2vw;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.img {
  width: 200px;
  height: 200px;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 8px;
}

.header h1 {
  font-size: clamp(24px, 3vw, 32px); /* 响应式字体大小 */
  font-weight: 700;
  background: linear-gradient(120deg, #74abda, #a289db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 0.5px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(14px, 1.5vw, 16px);
}

.status-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.open {
  background-color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
}

.status-dot.closed {
  background-color: #ef4444;
}

.status-dot.error {
  background-color: #f59e0b;
}

.status-text {
  color: #4b5563;
}

/* 聊天卡片 - 自适应高度和宽度 */
.chat-card {
  background-color: #ffffff;
  border-radius: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  width: 100%;
}

/* 聊天内容区域 */
.chat-box {
  flex: 1;
  padding: 32px clamp(16px, 3vw, 40px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 滚动条美化 */
.chat-box::-webkit-scrollbar {
  width: 8px;
}

.chat-box::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.chat-box::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.chat-box::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  animation: fadeIn 0.3s ease-out;
  width: 100%;
}

.message-item.user {
  flex-direction: row-reverse;
}

.avatar {
  width: clamp(40px, 5vw, 48px);
  height: clamp(40px, 5vw, 48px);
  border-radius: 50%;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(16px, 2vw, 20px);
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-item.user .avatar {
  background-color: #6366f1;
  color: white;
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 20px;
  max-width: clamp(60%, 70%, 80%);
  line-height: 1.6;
  font-size: clamp(15px, 1.8vw, 16px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-item.user .message-bubble {
  background-color: #69a5e8;
  color: white;
  border-bottom-right-radius: 6px;
}

.message-item.assistant .message-bubble {
  background-color: #f1f5f9;
  color: #1e293b;
  border-bottom-left-radius: 6px;
}

.message-item.system .message-bubble {
  background-color: #fef2f2;
  color: #dc2626;
  max-width: 80%;
  margin: 0 auto;
  border-radius: 16px;
}

.empty-tip {
  text-align: center;
  color: #94a3b8;
  font-size: clamp(15px, 1.8vw, 16px);
  margin-top: 80px;
}

/* 输入区域 */
.input-area {
  padding: 24px clamp(16px, 3vw, 40px);
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #fafbfc;
}

.image-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-btn {
  padding: 10px 20px;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-size: clamp(14px, 1.6vw, 15px);
  background-color: white;
}

.upload-btn:hover {
  border-color: #6076e4;
  color: #888aed;
  background-color: #f8fafc;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
}

.preview-container {
  position: relative;
}

.image-preview {
  width: clamp(80px, 10vw, 100px);
  height: clamp(80px, 10vw, 100px);
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f1f5f9;
  border-radius: 8px;
  min-width: 150px;
}

.file-icon {
  font-size: 24px;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #64748b;
}

.clear-preview {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #ef4444;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
}

.question-input {
  width: 100%;
  min-height: 100px;
  padding: 16px 20px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  resize: none;
  font-size: clamp(15px, 1.8vw, 16px);
  color: #1e293b;
  transition: all 0.2s;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.question-input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.question-input:disabled {
  background-color: #f8fafc;
  color: #94a3b8;
}

.send-btn {
  align-self: flex-end;
  padding: 12px 32px;
  background-color: #787ae8;
  color: white;
  border: none;
  border-radius: 16px;
  font-size: clamp(15px, 1.8vw, 16px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

.send-btn:hover:not(:disabled) {
  background-color: #7c76e6;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3);
}

.send-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* ✅ 新增：图片网格布局样式 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 16px;
  width: 100%;
}

.image-card {
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative; /* ✅ 新增：为错误提示提供定位上下文 */
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  background: #e2e8f0;
}

.result-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
  background: #e2e8f0;
  transition: opacity 0.3s;
  opacity: 0.8; /* 加载时半透明 */
}

/* ✅ 新增：加载中覆盖层 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  color: #64748b;
  font-size: 14px;
  z-index: 5;
}

.image-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.similarity-tag {
  font-size: 13px;
  font-weight: 600;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
  align-self: flex-start;
}

.filename {
  font-size: 12px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ✅ 新增：图片加载失败样式 */
.result-image[src*="placeholder"] {
  opacity: 0.6;
  filter: grayscale(100%);
}

/* ✅ 新增：错误提示框样式 */
.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #ef4444;
  font-size: 14px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  border: 2px dashed #ef4444;
  width: 90%;
  z-index: 10;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式适配 - 移动端优化 */
@media (max-width: 768px) {
  .app-container {
    padding: 12px 4vw;
  }

  .chat-card {
    height: calc(100vh - 100px);
    border-radius: 16px;
  }

  .chat-box {
    padding: 20px 16px;
    gap: 16px;
  }

  .message-item {
    gap: 12px;
  }

  .message-bubble {
    max-width: 85%;
    padding: 12px 16px;
  }

  .input-area {
    padding: 20px 16px;
  }
}
</style>
