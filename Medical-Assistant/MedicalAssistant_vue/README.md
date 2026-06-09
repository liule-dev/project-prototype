# 医疗 AI 助手 - Vue3 前端

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen)
![Vite](https://img.shields.io/badge/Vite-7.2-646CFF)
![Element Plus](https://img.shields.io/badge/Element_Plus-2.13-409EFF)
![Node](https://img.shields.io/badge/Node-20+-339933)
![License](https://img.shields.io/badge/License-MIT-yellow)

**基于 Vue 3 + Vite + Element Plus 的现代化医疗 AI 问答界面**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [项目结构](#-项目结构) • [组件说明](#-组件说明) • [部署指南](#-部署指南)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能特性](#-功能特性)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
  - [环境要求](#环境要求)
  - [本地开发](#本地开发)
  - [生产构建](#生产构建)
- [组件说明](#-组件说明)
- [API 集成](#-api-集成)
- [Docker 部署](#-docker-部署)
- [性能优化](#-性能优化)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目简介

医疗 AI 助手前端是一个基于 **Vue 3 Composition API** 构建的现代化单页应用（SPA），提供流畅的医疗咨询交互体验，支持文本问答、图像上传、文档解析、视频处理等多模态功能。

### 核心优势

- ⚡ **极速加载**: Vite 构建工具，秒级启动
- 🎨 **美观界面**: Element Plus 组件库，专业医疗风格
- 💬 **实时交互**: WebSocket 流式响应，打字机效果
- 📱 **响应式设计**: 完美适配桌面端和移动端
- 🚀 **性能优化**: 代码分割、懒加载、缓存策略

---

## ✨ 功能特性

### 💬 智能问答
- ✅ 实时流式对话（WebSocket）
- ✅ 多轮会话记忆
- ✅ Markdown 渲染
- ✅ 打字机效果输出
- ✅ 会话历史管理

### 🖼️ 多模态输入
- ✅ 图片上传与分析（支持 JPG/PNG）
- ✅ 文档上传（PDF/Word）
- ✅ 视频上传（MP4）
- ✅ 拖拽上传支持
- ✅ 预览与编辑

### 🎯 专科分诊
- ✅ 智能问题分类
- ✅ 推荐问题引导
- ✅ 专科图标展示
- ✅ 置信度提示

### 👤 用户系统
- ✅ 用户登录/注册
- ✅ 会话持久化
- ✅ 历史记录查询
- ✅ 本地存储管理

---

## 🛠️ 技术栈

### 核心框架
- **前端框架**: [Vue 3](https://vuejs.org/) 3.5.25 (Composition API)
- **构建工具**: [Vite](https://vite.dev/) 7.2.4
- **路由管理**: [Vue Router](https://router.vuejs.org/) 4.6.4

### UI 组件
- **组件库**: [Element Plus](https://element-plus.org/) 2.13.0
- **图标**: Element Plus Icons
- **样式**: CSS3 + Scoped Styles

### 网络请求
- **HTTP 客户端**: [Axios](https://axios-http.com/) 1.13.2
- **WebSocket**: 原生 WebSocket API

### 工具库
- **Markdown 渲染**: [Marked](https://marked.js.org/) 17.0.1
- **开发工具**: [Vite Plugin Vue DevTools](https://devtools.vuejs.org/) 8.0.5

### 开发环境
- **Node.js**: 20.19+ / 22.12+
- **包管理器**: npm

---

## 📁 项目结构

```
MedicalAssistant_vue/
├── public/                 # 静态资源
│   └── favicon.ico        # 网站图标
│
├── src/                    # 源代码
│   ├── api/               # API 接口
│   │   └── api.js         # Axios 封装与接口定义
│   │
│   ├── components/        # 组件
│   │   ├── HeaderSection.vue      # 顶部导航栏
│   │   ├── FunctionSection.vue    # 功能区（文件上传入口）
│   │   ├── RecommendSection.vue   # 推荐问题区
│   │   ├── ai.vue                 # AI 对话主界面 ⭐
│   │   ├── main.vue               # 主页面容器
│   │   ├── UploadModal.vue        # 文档上传弹窗
│   │   ├── ImageUploadModal.vue   # 图片上传弹窗
│   │   └── VideoUploadModal.vue   # 视频上传弹窗
│   │
│   ├── router/            # 路由配置
│   │   └── router.js      # Vue Router 配置
│   │
│   ├── views/             # 页面视图
│   │   └── Login.vue      # 登录页面
│   │
│   ├── App.vue            # 根组件
│   └── main.js            # 应用入口
│
├── .vscode/               # VSCode 配置
├── node_modules/          # 依赖包（不提交）
├── index.html             # HTML 模板
├── package.json           # 项目配置与依赖
├── vite.config.js         # Vite 配置
├── jsconfig.json          # JavaScript 配置
├── Dockerfile             # Docker 镜像配置
└── README.md              # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- **Node.js**: 20.19+ 或 22.12+
- **npm**: 10.0+
- **后端服务**: FastAPI 运行在 http://localhost:8000

### 本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/your-repo/Medical-Assistant.git
cd Medical-Assistant/MedicalAssistant_vue
```

#### 2. 安装依赖

```bash
npm install
```

#### 3. 配置后端地址

编辑 `src/api/api.js`，修改 `baseURL`：

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000',  // 修改为你的后端地址
  timeout: 10000,
});
```

#### 4. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173 查看应用。

**开发服务器特性**：
- ⚡ 热模块替换（HMR）
- 🔍 Vue DevTools 集成
- 📦 按需编译
- 🌐 自动打开浏览器

---

### 生产构建

#### 1. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

#### 2. 预览生产构建

```bash
npm run preview
```

访问 http://localhost:4173 预览生产版本。

#### 3. 部署到 Web 服务器

**Nginx 配置示例**：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # SPA 路由回退
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理（可选）
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket 代理
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
    }
}
```

---

## 🧩 组件说明

### 核心组件

#### 1. **ai.vue** - AI 对话主界面 ⭐

**功能**：
- WebSocket 连接管理
- 消息列表渲染
- 流式响应处理
- Markdown 渲染
- 会话历史加载

**关键代码**：
```vue
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'

const messages = ref([])
const ws = ref(null)

// 建立 WebSocket 连接
const connectWebSocket = () => {
  ws.value = new WebSocket(`ws://localhost:8000/api/query/stream/async?session_id=${sessionId}`)
  
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.event === 'delta') {
      // 流式追加文本
      messages.value[messages.value.length - 1].content += data.text
    }
  }
}

// 发送消息
const sendMessage = (question) => {
  messages.value.push({ role: 'user', content: question })
  ws.value.send(JSON.stringify({ question }))
}
</script>
```

---

#### 2. **HeaderSection.vue** - 顶部导航栏

**功能**：
- Logo 展示
- 用户信息显示
- 登出功能
- 新建会话按钮

**Props**：
```javascript
{
  username: String,     // 用户名
  onLogout: Function,   // 登出回调
  onNewChat: Function   // 新建会话回调
}
```

---

#### 3. **FunctionSection.vue** - 功能区

**功能**：
- 文件上传入口
- 图片/文档/视频上传按钮
- 触发对应上传弹窗

**Events**：
```javascript
emit('upload-image')   // 上传图片
emit('upload-document') // 上传文档
emit('upload-video')    // 上传视频
```

---

#### 4. **UploadModal.vue** - 文档上传弹窗

**功能**：
- PDF/Word 文件选择
- 拖拽上传支持
- 文件预览
- 上传进度显示
- 调用后端 API 上传

**支持的格式**：
- `.pdf` - PDF 文档
- `.doc` - Word 97-2003
- `.docx` - Word 2007+

---

#### 5. **ImageUploadModal.vue** - 图片上传弹窗

**功能**：
- 图片选择与预览
- 摄像头拍照（移动端）
- 图片压缩
- Base64 编码传输

**支持的格式**：
- `.jpg` / `.jpeg`
- `.png`
- `.webp`

---

#### 6. **VideoUploadModal.vue** - 视频上传弹窗

**功能**：
- 视频文件选择
- 视频预览播放
- 上传进度条
- MinIO 直传

**支持的格式**：
- `.mp4`
- `.avi`
- `.mov`

---

#### 7. **RecommendSection.vue** - 推荐问题

**功能**：
- 展示常见医疗问题
- 点击快速提问
- 专科分类图标

**数据结构**：
```javascript
const recommendations = [
  { 
    icon: '🫀', 
    text: '心血管疾病有哪些症状？',
    category: '心血管'
  },
  { 
    icon: '🧠', 
    text: '头痛应该挂什么科？',
    category: '神经内科'
  }
]
```

---

## 🔌 API 集成

### Axios 配置

```javascript
// src/api/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response.status === 401) {
      // 未授权，跳转登录
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 主要接口

#### 1. 用户认证

```javascript
// 登录
export function login(username, password) {
  return api.post('/auth/login', { username, password })
}

// 注册
export function register(username, password, email) {
  return api.post('/auth/register', { username, password, email })
}
```

#### 2. 文件上传

```javascript
// 上传医疗文档
export function upload_medical(url, data) {
  return api.post(url, data)
}
```

#### 3. 会话管理

```javascript
// 检查登录状态
export function isLoggedIn() {
  return localStorage.getItem('isLoggedIn') === 'true'
}

// 获取当前用户
export function getCurrentUser() {
  return {
    user_id: localStorage.getItem('user_id'),
    username: localStorage.getItem('username')
  }
}

// 登出
export function logout() {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  localStorage.removeItem('isLoggedIn')
}
```

---

## 🐳 Docker 部署

### 1. 构建 Docker 镜像

```bash
docker build -t medical-assistant-frontend .
```

### 2. 运行容器

```bash
docker run -d \
  --name medical-frontend \
  -p 80:80 \
  medical-assistant-frontend
```

### 3. Docker Compose（推荐）

在项目根目录使用 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  frontend:
    build: ./MedicalAssistant_vue
    container_name: medical-frontend
    ports:
      - "80:80"
    depends_on:
      - fastapi
    networks:
      - medical-network

networks:
  medical-network:
    driver: bridge
```

启动所有服务：

```bash
docker compose up -d
```

---

## 📊 性能优化

### 已实施的优化

| 优化项 | 说明 | 效果 |
|--------|------|------|
| **代码分割** | Vite 自动按路由分割 | 首屏加载 < 1s |
| **懒加载** | 组件按需加载 | 减少初始包体积 |
| **Tree Shaking** | 移除未使用代码 | 包体积减少 30% |
| **Gzip 压缩** | Nginx 启用 Gzip | 传输体积减少 70% |
| **缓存策略** | 静态资源长期缓存 | 二次访问秒开 |
| **WebSocket 复用** | 单连接多路复用 | 减少连接开销 |

### 性能指标

- **首屏加载时间**: < 1s
- **FCP (First Contentful Paint)**: < 0.8s
- **LCP (Largest Contentful Paint)**: < 1.5s
- **TTI (Time to Interactive)**: < 2s
- **Bundle Size**: ~150KB (Gzip)

### 优化建议

#### 1. 图片优化

```javascript
// 图片上传前压缩
const compressImage = (file, quality = 0.8) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        canvas.width = img.width * 0.8  // 缩小 20%
        canvas.height = img.height * 0.8
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        canvas.toBlob(resolve, file.type, quality)
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}
```

#### 2. 虚拟滚动（大量消息时）

```vue
<template>
  <RecycleScroller
    :items="messages"
    :item-size="50"
    key-field="id"
  >
    <template #default="{ item }">
      <MessageItem :message="item" />
    </template>
  </RecycleScroller>
</template>

<script setup>
import { RecycleScroller } from 'vue-virtual-scroller'
</script>
```

#### 3. Service Worker 缓存

```javascript
// 注册 Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(() => {
    console.log('Service Worker 注册成功')
  })
}
```

---

## ❓ 常见问题

### 1. WebSocket 连接失败

**错误**: `WebSocket connection to 'ws://localhost:8000' failed`

**解决**:
- 确认后端服务已启动
- 检查防火墙设置
- 确认 CORS 配置允许 WebSocket

### 2. 跨域问题

**错误**: `Access to XMLHttpRequest has been blocked by CORS policy`

**解决**:
```python
# FastAPI 后端配置
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 生产环境白屏

**原因**: 路由 history 模式需要服务端配置

**解决**:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 4. 图片上传失败

**错误**: `Request entity too large`

**解决**:
```nginx
# Nginx 配置
client_max_body_size 100M;
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 [Vue Style Guide](https://vuejs.org/style-guide/)
- 使用 `<script setup>` 语法
- 组件名使用 PascalCase
- Props 命名使用 camelCase

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

## 📞 联系方式

- 项目维护者: Your Name
- Email: your-email@example.com
- 问题反馈: [GitHub Issues](https://github.com/your-repo/Medical-Assistant/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

Made with ❤️ by Medical AI Team

</div>
