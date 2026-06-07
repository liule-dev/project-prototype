<template>
  <el-dialog
    v-model="dialogVisible"
    title="确认操作"
    width="300px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="dialog-content">
      {{ content }}
    </div>
    <template #footer>
      <el-button @click="dialogVisible = false">否</el-button>
      <el-button type="primary" @click="handleConfirm">是</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ElMessage } from 'element-plus';
import api from '@/stores/gain';
import {ref} from "vue"; // 引入封装的请求模块（需确保路径正确）

// 控制弹窗显示
const dialogVisible = ref(false);
// 弹窗内容
const content = ref('是否确认删除该题库？');
// 要删除的数据
const deleteData = ref(null);
// 父组件的刷新回调
const refreshCallback = ref(null);

// 打开删除弹窗，接收要删除的数据、提示文案、刷新回调
const openDeleteDialog = (rowData, text = '是否确认删除该题库？', callback) => {
  deleteData.value = rowData;
  refreshCallback.value = callback;
  content.value = text;
  dialogVisible.value = true;
};

// 确认删除操作
const handleConfirm = () => {
  if (deleteData.value && refreshCallback.value) {
    // 调用封装的删除接口
    api.deleteData(
      `http://localhost:8000/questions/${deleteData.value.Question_number}/`,
      '删除成功',
      () => {
        // 确保刷新回调在删除成功后执行
        if (typeof refreshCallback.value === 'function') {
          refreshCallback.value();
        }
      }
    );
  }
  dialogVisible.value = false;
};

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false;
};

// 暴露方法给父组件
defineExpose({ openDeleteDialog });
</script>

<style scoped>
.dialog-content {
  text-align: center;
  padding: 20px 0;
}
</style>