<script setup>
import { ref, reactive, watch, onMounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/stores/gain';
import dayjs from 'dayjs';

// 控制弹窗显示
const dialogVisible = ref(false);
const modifyFormRef = ref(null);

// 表单数据
const formData = reactive({
  Question_number: '',
  name: '',
  grade1: null,
  subject: null,
  question_type: '',
  if_public: false,
  status: '',
  created_at: '',
  updated_at: ''
});

// 下拉列表数据
const grades = ref([]);
const subjects = ref([]);

// 表单验证规则
const formRules = reactive({
  name: [
    { required: true, message: '请输入题库名称', trigger: 'blur' },
  ],
  grade1: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请选择学科', trigger: 'change' }
  ],
  question_type: [
    { required: true, message: '请选择题型', trigger: 'change' }
  ]
});

const props = defineProps({
  topicId: {
    type: String,
    required: true
  }
});

// 初始化获取年级和学科数据
onMounted(() => {
  api.fetchData('http://localhost:8000/grades/', grades, '获取年级数据失败');
  api.fetchData('http://localhost:8000/subjects/', subjects, '获取学科数据失败');
});

// 从父组件接收数据并回显
const openDialog = async (rowData) => {
  await nextTick(); // 确保DOM已更新
  dialogVisible.value = true;

  // 重置表单
  if (modifyFormRef.value) {
    modifyFormRef.value.resetFields();
  }

  // 格式化时间显示
  const formatDate = (dateString) => {
    return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss');
  };

  // 回显数据
  formData.Question_number = rowData.Question_number;
  formData.name = rowData.name;
  formData.grade1 = rowData.grade1;
  formData.subject = rowData.subject;
  formData.question_type = rowData.question_type;
  formData.if_public = rowData.if_public;
  formData.status = rowData.status;
  formData.created_at = formatDate(rowData.created_at);
  formData.updated_at = formatDate(rowData.updated_at);
};

// 提交修改
const handleSubmit = async () => {
  // 表单验证
  const isValid = await modifyFormRef.value.validate();
  if (!isValid) return;

  // 构造提交数据
  const submitData = {
    name: formData.name,
    question_type: formData.question_type,
    grade1: formData.grade1,
    if_public: formData.if_public,
    subject: formData.subject
  };

  // 调用更新接口
  const updateResult = ref(null);
  const url = `http://localhost:8000/questions/${formData.Question_number}/`;

  api.updateQuestionBank(
    url,
    updateResult,
    submitData,
    '修改题库失败'
  );

  // 监听更新结果
  watch(updateResult, (newVal) => {
    if (newVal) {
      ElMessage.success('题库修改成功');
      dialogVisible.value = false;
      // 通知父组件刷新列表
      emits('refreshList');
    }
  });
};

// 关闭弹窗
const handleClose = () => {
  if (modifyFormRef.value) {
    modifyFormRef.value.resetFields();
  }
  dialogVisible.value = false;
};

// 定义事件和暴露方法
const emits = defineEmits(['refreshList']);
defineExpose({ openDialog });
onMounted(() => {
  console.log('当前题目ID:', props.topicId);

  if (props.topicId) {
    loadTopicData(props.topicId);
  }
});
</script>


<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改题库"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="modifyFormRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      size="default"
    >
      <!-- 题库编号（不可修改） -->
      <el-form-item label="题库编号">
        <el-input
          v-model="formData.Question_number"
          disabled
          placeholder="自动生成"
        />
      </el-form-item>

      <!-- 题库名称（可修改） -->
      <el-form-item label="题库名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入题库名称"
        />
      </el-form-item>

      <!-- 年级（可修改） -->
      <el-form-item label="年份" prop="grade1">
        <el-select
          v-model="formData.grade1"
          placeholder="请选择年份"
        >
          <el-option
            v-for="grade in grades"
            :key="grade.id"
            :label="grade.grade10"
            :value="grade.id"
          />
        </el-select>
      </el-form-item>

      <!-- 学科（可修改） -->
      <el-form-item label="学科" prop="subject">
        <el-select
          v-model="formData.subject"
          placeholder="请选择学科"
        >
          <el-option
            v-for="subject in subjects"
            :key="subject.id"
            :label="subject.subject_name"
            :value="subject.id"
          />
        </el-select>
      </el-form-item>

      <!-- 题型（可修改） -->
      <el-form-item label="题型" prop="question_type">
        <el-select
          v-model="formData.question_type"
          placeholder="请选择题型"
        >
          <el-option label="单项选择题" value="单项选择题" />
          <el-option label="多项选择题" value="多项选择题"/>
          <el-option label="判断题" value="判断题"/>
          <el-option label="案例分析题" value="案例分析题"/>
          <el-option label="计算分析题" value="计算分析题"/>
          <el-option label="综合题" value="综合题"/>
        </el-select>
      </el-form-item>

      <!-- 是否公开（可修改） -->
      <el-form-item label="是否公开" prop="if_public">
        <el-radio-group v-model="formData.if_public">
          <el-radio :label="true">是</el-radio>
          <el-radio :label="false">否</el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 状态（不可修改） -->
      <el-form-item label="状态">
        <el-input v-model="formData.status" disabled />
      </el-form-item>

      <!-- 创建时间（不可修改） -->
      <el-form-item label="创建时间">
        <el-input v-model="formData.created_at" disabled />
      </el-form-item>

      <!-- 更新时间（不可修改） -->
      <el-form-item label="更新时间">
        <el-input v-model="formData.updated_at" disabled />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确认修改</el-button>
    </template>
  </el-dialog>
</template>



<style scoped>
::v-deep .el-form-item__label {
  font-weight: 500;
}

::v-deep .el-input.is-disabled .el-input__inner {
  background-color: #f5f7fa;
  color: #606266;
}
</style>
