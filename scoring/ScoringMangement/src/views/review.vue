
<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-menu mode="horizontal" :default-active="activeMenuItem">
          <el-menu-item
            v-for="item in filteredMenuItems"
            :key="item.index"
            :index="item.index"
            @click="handleMenuClick(item)"
          >
            {{ item.title }}
          </el-menu-item>
        </el-menu>
      </el-header>
      <el-main class="main-content">
        <!-- 根据激活的菜单项显示对应组件 -->
        <div v-if="activeComponent" class="component-container">
          <component :is="activeComponent" />
        </div>
        <!-- 默认欢迎内容 -->
        <div v-else class="welcome-content">
          <h3>欢迎使用评审管理系统</h3>
          <p>请选择上方菜单中的功能进行操作</p>
        </div>
      </el-main>
    </el-container>
  </div>

  <!-- 欢迎弹窗 -->
  <el-dialog
    v-model="showWelcomeDialog"
    title="欢迎使用"
    width="30%"
    center
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <div class="welcome-dialog-content">
      <h3>欢迎使用评审管理系统</h3>
      <p>请选择上方菜单中的功能进行操作</p>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="showWelcomeDialog = false">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { RouterView } from "vue-router";
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { House } from '@element-plus/icons-vue';
import { ref, onMounted, watch, shallowRef } from 'vue';

// 导入所有可能需要显示的组件
import AutoGrade from '@/views/grading/AutoGradeObjective.vue';
import ManualGrade from '@/views/grading/ManualGradeSubjective.vue';
import GradeSummary from '@/views/grading/GradeSummary.vue';
import ExportReport from '@/views/reports/ExportGradeReport.vue';

const store = useStore();
const router = useRouter();

// 定义子菜单项及其对应组件
const menuItems = ref([
  { index: '/review/auto-grade', title: '客观题自动批改', role: 'teacher', component: AutoGrade },
  { index: '/review/manual-grade', title: '主观题人工批改', role: 'teacher', component: ManualGrade },
  { index: '/review/grade-summary', title: '成绩整合', role: 'teacher', component: GradeSummary },
  { index: '/review/export-report', title: '导出报表', role: 'teacher', component: ExportReport }
]);

// 根据用户角色过滤菜单项
const filteredMenuItems = menuItems.value.filter(item => {
  if (item.role === 'teacher') {
    const userRole = store.state.user?.role || localStorage.getItem('role');
    return userRole === 'teacher' || userRole === 'admin';
  }
  return true;
});

// 控制欢迎弹窗显示
const showWelcomeDialog = ref(false);

// 当前激活的菜单项和组件
const activeMenuItem = ref('/review/auto-grade'); // 默认激活第一个菜单项
const activeComponent = shallowRef(AutoGrade); // 默认显示AutoGrade组件

// 处理菜单点击事件
const handleMenuClick = (item) => {
  activeMenuItem.value = item.index;
  activeComponent.value = item.component;
};

// 监听路由变化，当进入Review页面时显示欢迎弹窗
watch(() => router.currentRoute.value.name, (newVal) => {
  if (newVal === 'Review') {
    showWelcomeDialog.value = true;
    // 设置默认激活状态为自动批改组件
    activeMenuItem.value = '/review/auto-grade';
    activeComponent.value = AutoGrade;
  }
}, { immediate: true });

// 返回主页功能
const goHome = () => {
  router.push('/main');
};

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });

    // 清除认证信息
    store.dispatch('logout');

    // 跳转到登录页
    router.push('/login');
  } catch (error) {
    // 用户取消操作
    console.log('用户取消登出操作');
  }
};
</script>

<style scoped>
.common-layout {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-header {
  padding: 0;
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  height: calc(100% - 60px); /* 减去header的高度 */
  position: relative;
}

.header-right {
  float: right;
  height: 100%;
  display: flex;
  align-items: center;
  padding-right: 20px;
  gap: 10px; /* 添加按钮和下拉菜单之间的间距 */
}

.home-button {
  margin-right: 10px; /* 按钮与下拉菜单之间的间距 */
}

.welcome-dialog-content,
.welcome-content {
  text-align: center;
  padding: 20px 0;
}

.welcome-dialog-content h3,
.welcome-content h3 {
  color: #409eff;
  margin-bottom: 15px;
}

.welcome-dialog-content p,
.welcome-content p {
  color: #606266;
  font-size: 16px;
}

.component-container {
  background-color: white;
  border-radius: 4px;
  padding: 20px;
  min-height: 100%;
}
</style>
