<script setup>
import {marked} from 'marked';
import {onMounted, reactive, ref} from "vue";

const chat_url = "ws://localhost:8080/ws/chat";
const ws = ref(null);
const wsStatus = ref("closed");
const question = ref("");
const sending = ref(false);
const preview = ref(null); // 图片预览数据
const preview1 = ref(null);// 文件预览数据
const imageBase64 = ref(null);
const datafilebase64 = ref(null);
const imageSrc = ref(null);
const messages = reactive([]);
const image = ref(null);
function connectWebSocket() {
  // 实例化websocket对象
  ws.value = new WebSocket(chat_url);//这个 WebSocket 实例化是在前端进行的。
                                    //实例化语句是：ws.value = new WebSocket(chat_url);
                                    //其中 chat_url 是定义好的 WebSocket 服务地址 "ws://localhost:8080/ws/chat"。
                                    //通过 new WebSocket(chat_url) 创建了一个连接到指定 URL 的 WebSocket 对象，并赋值给响应式变量 ws.value。
  ws.value.onopen = () => {
    wsStatus.value = "open";
    console.log("WebSocket连接已打开");
  };
  ws.value.onerror = () => {
    wsStatus.value = "error";
    console.log("WebSocket连接出错");
  };
  ws.value.onclose = () => {//关闭连接的操作：是 websocket.close() 方法（主动关闭），或网络中断、后端主动断开等被动情况。onclose 事件：是连接已经关闭后触发的回调，用来响应 “连接关闭” 这个结果。
    wsStatus.value = "closed";
    console.log("WebSocket连接已关闭");
  };
  ws.value.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.event === "start") {
    sending.value = true;
    // 添加一个带有标识的消息
    messages.push({ role: "assistant", text: "正在生成回答...", isGenerating: true });
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
    if (data.image) {
      imageSrc.value = `data:image/png;base64,${data.image}`;
    }
    sending.value = false;
    if (data.error) {
      messages.push({ role: "system", text: "错误：" + data.message });
    }
  }
};

}

// WebSocket消息处理


// 图片选择之后的处理
function previewImage(event) {
  const file = event.target.files[0];// 获取选择的图片对象
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.value = e.target.result;
      imageBase64.value = e.target.result.split(",")[1]; //提取 base64 数据部分
    };
    reader.readAsDataURL(file);
  }
}
const selectedFileInfo = ref(null);
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



function handleKeydown(event) {
  // 检查是否按下 Enter 键且没有按下 Shift 键
  if (event.key === 'Enter' && !event.shiftKey) {
    // 阻止默认行为（避免在 textarea 中插入换行符）
    event.preventDefault();
    // 调用发送消息函数
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
    alert("WebSocket未连接，无法发送消息");
    return;
  }
  // 将用户消息添加到消息列表
  messages.push({ role: "user", text: question.value.trim(),image: preview.value,datafile: preview1.value});
  // 构造发送的数据对象
  const messageData = {
    question: question.value.trim(),
    imageBase64: imageBase64.value,
    datafileBase64: datafilebase64.value,
  };
  // 通过WebSocket发送消息
  ws.value.send(JSON.stringify(messageData));
  // 清空输入框和预览
  question.value = "";
  preview.value = null;
  imageBase64.value = null;
  image.value = null;
  preview1.value = null;
  datafilebase64.value = null;
}

// 在组件挂载的时候 就去执行这个方法
onMounted(() => connectWebSocket());
</script>

<template>
  <div class="app-container">
    <div class="header">
      <h1>Qwen-VL 多模态对话</h1>
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
          <img v-if="msg.image" style="width: 200px; height: 200px" :src="msg.image" alt="图片" />
          <img v-if="imageSrc && msg.role === 'assistant'" :src="imageSrc" class="img">
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

<style scoped>


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
  margin-right: 1000px;
  max-width: 1400px; /* 大幅增加最大宽度 */
  padding: 20px 2vw; /* 使用视口宽度单位适配边距 */
  min-height: 100vh;
  background-color: #f5f7fa;
}


.img{
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
  background: linear-gradient(120deg, #6366f1, #8b5cf6);
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
  height: calc(100vh - 140px); /* 自适应高度 */
  width: 100%;
}

/* 聊天内容区域 */
.chat-box {
  flex: 1;
  padding: 32px clamp(16px, 3vw, 40px); /* 响应式内边距 */
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
  width: clamp(40px, 5vw, 48px); /* 响应式头像大小 */
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
  max-width: clamp(60%, 70%, 80%); /* 响应式气泡宽度 */
  line-height: 1.6;
  font-size: clamp(15px, 1.8vw, 16px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-item.user .message-bubble {
  background-color: #6366f1;
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
  border-color: #6366f1;
  color: #6366f1;
  background-color: #f8fafc;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
}

.preview-container {
  position: relative;
}

.image-preview {
  width: clamp(80px, 10vw, 100px); /* 响应式图片预览 */
  height: clamp(80px, 10vw, 100px);
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  background-color: #6366f1;
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
  background-color: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3);
}

.send-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
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

/* 超宽屏幕适配 */
@media (min-width: 1600px) {
  .app-container {
    max-width: 1600px;
  }

  .message-bubble {
    max-width: 70%;
  }
}
</style>
