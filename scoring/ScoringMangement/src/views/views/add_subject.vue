<template>
  <div class="subject-manage-container">
    <el-card class="subject-list-card">
      <template #header>
        <div class="card-header">
          <span>学科管理</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="openAddDialog" style="margin-left: 10px;">新增学科</el-button>
          </div>
        </div>
      </template>

      <!-- 学科列表 -->
      <el-table :data="subjects" style="width: 100%">
        <el-table-column prop="subject_name" label="学科名称" />
        <el-table-column prop="choice_count" label="选择题数量" />
        <el-table-column prop="choice_score" label="选择题分数" />
        <el-table-column prop="multiple_choice_count" label="多选题数量" />
        <el-table-column prop="multiple_choice_score" label="多选题分数" />
        <el-table-column prop="judgment_count" label="判断题数量" />
        <el-table-column prop="judgment_score" label="判断题分数" />
        <el-table-column prop="calculation_analysis_count" label="计算分析题数量" />
        <el-table-column prop="calculation_analysis_score" label="计算分析题分数" />
        <el-table-column prop="case_analysis_count" label="案例分析题数量" />
        <el-table-column prop="case_analysis_score" label="案例分析题分数" />
        <el-table-column prop="comprehensive_count" label="综合题数量" />
        <el-table-column prop="comprehensive_score" label="综合题分数" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editSubject(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSubject(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑学科弹窗 -->
    <el-dialog v-model="addDialogVisible" :title="isEditing ? '编辑学科' : '新增学科'" width="600px" @close="handleDialogClose">
      <el-form :model="currentSubject" ref="formRef" label-width="120px">
        <el-form-item label="学科名称" prop="subject_name" :rules="[{ required: true, message: '请输入学科名称', trigger: 'blur' }]">
          <el-input v-model="currentSubject.subject_name" placeholder="请输入学科名称" />
        </el-form-item>

        <!-- 选择题数量和分数 -->
        <el-form-item label="选择题数量" prop="choice_count">
          <el-input-number v-model="currentSubject.choice_count" :min="0" placeholder="选择题数量" />
        </el-form-item>
        <el-form-item label="选择题分数" prop="choice_score">
          <el-input-number v-model="currentSubject.choice_score" :min="0" placeholder="选择题分数" />
        </el-form-item>

        <!-- 多选题数量和分数 -->
        <el-form-item label="多选题数量" prop="multiple_choice_count">
          <el-input-number v-model="currentSubject.multiple_choice_count" :min="0" placeholder="多选题数量" />
        </el-form-item>
        <el-form-item label="多选题分数" prop="multiple_choice_score">
          <el-input-number v-model="currentSubject.multiple_choice_score" :min="0" placeholder="多选题分数" />
        </el-form-item>

        <!-- 判断题数量和分数 -->
        <el-form-item label="判断题数量" prop="judgment_count">
          <el-input-number v-model="currentSubject.judgment_count" :min="0" placeholder="判断题数量" />
        </el-form-item>
        <el-form-item label="判断题分数" prop="judgment_score">
          <el-input-number v-model="currentSubject.judgment_score" :min="0" placeholder="判断题分数" />
        </el-form-item>

        <!-- 计算分析题数量和分数 -->
        <el-form-item label="计算分析题数量" prop="calculation_analysis_count">
          <el-input-number v-model="currentSubject.calculation_analysis_count" :min="0" placeholder="计算分析题数量" />
        </el-form-item>
        <el-form-item label="计算分析题分数" prop="calculation_analysis_score">
          <el-input-number v-model="currentSubject.calculation_analysis_score" :min="0" placeholder="计算分析题分数" />
        </el-form-item>

        <!-- 案例分析题数量和分数 -->
        <el-form-item label="案例分析题数量" prop="case_analysis_count">
          <el-input-number v-model="currentSubject.case_analysis_count" :min="0" placeholder="案例分析题数量" />
        </el-form-item>
        <el-form-item label="案例分析题分数" prop="case_analysis_score">
          <el-input-number v-model="currentSubject.case_analysis_score" :min="0" placeholder="案例分析题分数" />
        </el-form-item>

        <!-- 综合题数量和分数 -->
        <el-form-item label="综合题数量" prop="comprehensive_count">
          <el-input-number v-model="currentSubject.comprehensive_count" :min="0" placeholder="综合题数量" />
        </el-form-item>
        <el-form-item label="综合题分数" prop="comprehensive_score">
          <el-input-number v-model="currentSubject.comprehensive_score" :min="0" placeholder="综合题分数" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="saveSubject">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/stores/gain'

// 路由实例
const router = useRouter()

// 学科列表数据
const subjects = ref<any[]>([])

// 弹窗控制
const addDialogVisible = ref(false)
const isEditing = ref(false)

// 当前学科表单数据（包含数量和分数字段）
const currentSubject = reactive({
  id: null,
  subject_name: '',
  choice_count: 0,
  choice_score: 0,
  multiple_choice_count: 0,
  multiple_choice_score: 0,
  judgment_count: 0,
  judgment_score: 0,
  calculation_analysis_count: 0,
  calculation_analysis_score: 0,
  case_analysis_count: 0,
  case_analysis_score: 0,
  comprehensive_count: 0,
  comprehensive_score: 0
})

// 表单引用
const formRef = ref()

// 返回上一页
const goBack = () => {
  router.back()
}

// 获取学科列表
const fetchSubjects = async () => {
  try {
    const res = await api.fetchData('/subjects/', subjects, '获取学科失败')
  } catch (error) {
    console.error('获取学科失败:', error)
    ElMessage.error('获取学科失败')
  }
}

// 删除学科
const deleteSubject = async (id: number) => {
  await ElMessageBox.confirm('确定要删除该学科吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
  try {
    await api.deleteData(`/subjects/${id}/`, '删除学科失败')
    ElMessage.success('删除成功')
    fetchSubjects() // 刷新列表
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 编辑学科
const editSubject = (subject: any) => {
  Object.assign(currentSubject, subject)
  isEditing.value = true
  addDialogVisible.value = true
}

// 打开新增弹窗
const openAddDialog = () => {
  resetForm()
  isEditing.value = false
  addDialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  currentSubject.id = null
  currentSubject.subject_name = ''
  currentSubject.choice_count = 0
  currentSubject.choice_score = 0
  currentSubject.multiple_choice_count = 0
  currentSubject.multiple_choice_score = 0
  currentSubject.judgment_count = 0
  currentSubject.judgment_score = 0
  currentSubject.calculation_analysis_count = 0
  currentSubject.calculation_analysis_score = 0
  currentSubject.case_analysis_count = 0
  currentSubject.case_analysis_score = 0
  currentSubject.comprehensive_count = 0
  currentSubject.comprehensive_score = 0
}

// 关闭弹窗并重置表单
const handleDialogClose = () => {
  addDialogVisible.value = false
  isEditing.value = false
  resetForm()
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 保存学科（新增或编辑）
const saveSubject = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (isEditing.value) {
          // 编辑学科
          await api.updateData(`/subjects/${currentSubject.id}/`, currentSubject, '编辑学科失败')
          ElMessage.success('学科编辑成功')
        } else {
          // 新增学科
          await api.addQuestionBank(
            '/subjects/create/',
            currentSubject,
            '添加学科失败',
            () => {
              ElMessage.success('学科添加成功')
            }
          )
        }
        handleDialogClose()
        fetchSubjects()
      } catch (error) {
        console.error('保存失败:', error)
        ElMessage.error('保存失败')
      }
    }
  })
}

// 页面加载时获取数据
fetchSubjects()
</script>

<style scoped>
.subject-manage-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.subject-list-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  text-align: right;
}
</style>
