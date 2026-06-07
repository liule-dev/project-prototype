<template>
  <el-dialog v-model="dialogVisible" title="添加题库" width="50%">
    <el-form :model="questionBankForm" label-width="120px">
      <el-form-item label="题库名称">
        <el-input v-model="questionBankForm.name" placeholder="请输入题库名称"/>
      </el-form-item>
      <el-form-item label="年分">
        <el-select v-model="questionBankForm.grade_id" placeholder="请选择年分">
          <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.grade10"
              :value="grade.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="学科">
        <el-select v-model="questionBankForm.subject_id" placeholder="请选择学科">
          <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.subject_name"
              :value="subject.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="题型">
        <el-select v-model="questionBankForm.question_type" placeholder="请选择题型">
          <el-option label="单项选择题" value="单项选择题"/>
          <el-option label="多项选择题" value="多项选择题"/>
          <el-option label="判断题" value="判断题"/>
          <el-option label="计算分析题" value="计算分析题"/>
          <el-option label="案例分析题" value="案例分析题"/>
          <el-option label="综合题" value="综合题"/>
        </el-select>
      </el-form-item>
      <el-form-item label="是否公开">
        <el-radio-group v-model="questionBankForm.if_public">
          <el-radio :label="true">是</el-radio>
          <el-radio :label="false">否</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确认添加</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, defineEmits } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/stores/gain';

// 定义自定义事件
const emit = defineEmits(['refreshList']);

// 控制弹窗显示
const dialogVisible = ref(false);

// 表单数据
const questionBankForm = reactive({
  name: '',
  grade_id: '',
  subject_id: '',
  question_type: '',
  if_public: false
});

// 下拉列表数据
const grades = ref([]);
const subjects = ref([]);

// 存储父组件传递的刷新回调
const refreshCallback = ref(null);

// 打开弹窗的方法
const addDialog = (callback) => {
  // 重置表单
  Object.assign(questionBankForm, {
    name: '',
    grade_id: '',
    subject_id: '',
    question_type: '',
    if_public: false
  });
  refreshCallback.value = callback;
  dialogVisible.value = true;
};

// 页面加载时获取下拉数据
onMounted(() => {
  api.fetchData('http://localhost:8000/subjects/', subjects, '获取学科失败');
  api.fetchData('http://localhost:8000/grades/', grades, '获取年级失败');
});

// 提交表单
const handleSubmit = () => {
  // 基础验证
  if (!questionBankForm.name) {
    ElMessage.error('请输入题库名称');
    return;
  }
  if (!questionBankForm.subject_id) {
    ElMessage.error('请选择所属学科');
    return;
  }
  if (!questionBankForm.grade_id) {
    ElMessage.error('请选择所属年级');
    return;
  }

  // 构造提交数据
  const submitData = {
    name: questionBankForm.name,
    question_type: questionBankForm.question_type,
    subject: questionBankForm.subject_id,
    grade1: questionBankForm.grade_id,
    if_public: questionBankForm.if_public,
  };

  // 调用添加接口
  api.addQuestionBank(
      'http://localhost:8000/questions/',
      submitData,
      '添加失败',
      () => {
        // 触发刷新
        if (refreshCallback.value) {
          refreshCallback.value();
        }
        emit('refreshList');
        dialogVisible.value = false;
      }
  );
};

// 暴露方法给父组件
defineExpose({addDialog});
</script>
