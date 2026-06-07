// 路由配置文件：src/router/index.js
import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import AiComponent from '@/components/ai.vue' // 你的/ai对应组件
import LoginView from '@/views/Login.vue' // 登录页面
import CustomMain from '@/components/main.vue' // 主页面

// 路由规则配置（确认已定义/ai路由，解决之前的匹配失败问题）
const routes = [
  {
    path: '/', // 根路径，重定向到登录页
    redirect: '/login'
  },
  {
    path: '/login', // 登录页面
    name: 'Login',
    component: LoginView
  },
  {
    path: '/main', // 主页面
    name: 'Main',
    component: CustomMain
  },
  {
    path: '/ai', // 实际路由路径（无#）
    name: 'Ai',
    component: AiComponent
  },

  // 其他你的路由规则...
]

const router = createRouter({
  // 关键配置：使用createWebHistory() 取消hash模式（去除#）
  history: createWebHistory(), // 不传参数默认使用当前域名根路径
  // 若你的项目部署在子路径（如https://xxx.com/my-app/），需传参：createWebHistory('/my-app/')
  routes
})

export default router