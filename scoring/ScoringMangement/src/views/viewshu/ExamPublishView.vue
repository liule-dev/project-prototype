这个<!-- src/viewshu/ExamPublishView.vue -->
<template>
  <div class="exam-publish-container">
    <el-card class="exam-card">
      <template #header>
        <div class="card-header">
          <span>发布考试</span>
        </div>
      </template>

      <el-form
        :model="publishForm"
        :rules="publishRules"
        ref="publishFormRef"
        label-width="120px"
        class="publish-form"
      >
        <el-form-item label="考试ID" prop="exam_paper_id">
          <el-input v-model.number="publishForm.exam_paper_id" type="number" placeholder="请输入要发布的考试ID" />
        </el-form-item>

        <el-form-item label="筛选条件">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-select v-model="filterType" placeholder="请选择筛选类型">
                <el-option label="按班级" value="class" />
                <el-option label="按专业" value="specialty" />
                <el-option label="按年级" value="grade" />
              </el-select>
            </el-col>
            <el-col :span="16">
              <el-input v-model="filterValue" placeholder="请输入筛选值" />
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="publishExam">发布考试</el-button>
          <el-button @click="viewExamDetail" v-if="publishForm.exam_paper_id">查看考试详情</el-button>
        </el-form-item>
      </el-form>

      <!-- 考试详情展示 -->
      <div v-if="examDetail" class="exam-detail">
        <el-divider>考试详情</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考试名称">{{ examDetail.name }}</el-descriptions-item>
          <el-descriptions-item label="科目">{{ examDetail.subject }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ examDetail.begin_time }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ examDetail.end_time }}</el-descriptions-item>
          <el-descriptions-item label="及格线">{{ examDetail.settings.passing_score }}</el-descriptions-item>
          <el-descriptions-item label="考试时长">{{ examDetail.settings.duration }}分钟</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="examDetail.status ? 'success' : 'warning'">
              {{ examDetail.status ? '已发布' : '未发布' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { examAPI } from '@/api1/exam.js'
import { ElMessage } from 'element-plus'

// 表单引用
const publishFormRef = ref()

// 表单数据
const publishForm = reactive({
  exam_paper_id: ''
})

// 筛选条件
const filterType = ref('class')
const filterValue = ref('')

// 考试详情
const examDetail = ref(null)

// 表单验证规则
const publishRules = {
  exam_paper_id: [
    { required: true, message: '请输入考试ID', trigger: 'blur' }
  ]
}

// 查看考试详情
const viewExamDetail = async () => {
  if (!publishForm.exam_paper_id) {
    ElMessage.warning('请输入考试ID')
    return
  }

  try {
    const response = await examAPI.getExamDetail(publishForm.exam_paper_id)
    if (response.status === 'success') {
      examDetail.value = response.exam
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    ElMessage.error('获取考试详情失败: ' + error.message)
  }
}

// 发布考试
const publishExam = async (exam) => {
  // 检查是否有权限发布该考试
  if (!canManageExam(exam)) {
    ElMessage.error('无权限发布该考试')
    return
  }

  try {
    const response = await examAPI.publishExam({ exam_paper_id: exam.id })
    if (response.status === 'success') {
      ElMessage.success('发布成功')
      await fetchExams() // 确保刷新考试列表

      // 更新本地数据状态
      const index = exams.value.findIndex(item => item.id === exam.id)
      if (index !== -1) {
        exams.value[index].status = true
      }
    } else {
      ElMessage.error(response.message)
    }
  } catch (error) {
    ElMessage.error('发布失败: ' + error.message)
  }
}

</script>

<style scoped>
.exam-publish-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.exam-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.publish-form {
  margin-top: 20px;
}

.exam-detail {
  margin-top: 30px;
}
</style>
