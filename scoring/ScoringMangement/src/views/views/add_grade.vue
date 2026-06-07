<template>
  <div class="grade-manage-container">
    <el-card class="grade-list-card">
      <template #header>
        <div class="card-header">
          <span>年份管理</span>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button type="primary" @click="openAddDialog" style="margin-left: 10px;">新增年份</el-button>
          </div>
        </div>
      </template>

      <!-- 年级列表 -->
      <el-table :data="grades" style="width: 100%">
        <el-table-column prop="grade10" label="年份名称" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteGrade(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

    </el-card>

    <!-- 新增年级弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增年份" width="500px" @close="handleDialogClose">
      <el-form :model="newGrade" ref="formRef" label-width="80px">
        <el-form-item label="年级名称" prop="grade10" :rules="[{ required: true, message: '请输入年级名称', trigger: 'blur' }]">
          <el-input v-model="newGrade.grade10" placeholder="请输入年级名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="addGrade">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/stores/gain.ts'

// 路由实例
const router = useRouter()

// 年级列表数据
const grades = ref<any[]>([])

// 弹窗控制
const addDialogVisible = ref(false)

// 新年级表单数据
const newGrade = reactive({
  grade: ''
})

// 表单引用
const formRef = ref()

// 返回上一页
const goBack = () => {
  router.push('/main')
}

// 获取年级列表
const fetchGrades = async () => {
  try {
    console.log('开始获取年级数据...')
    const res = await api.fetchData('/grades/', grades, '获取年级失败')
    console.log('获取到的数据:', grades.value)
  } catch (error) {
    console.error('获取年级失败:', error)
    ElMessage.error('获取年级失败')
  }
}

// 页面加载时获取数据
fetchGrades()
// 删除年级
const deleteGrade = async (id: number) => {
  await ElMessageBox.confirm('确定要删除该年级吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
  try {
    await api.deleteData(`/grades/${id}/`, '删除年级失败')
    ElMessage.success('删除成功')
    fetchGrades() // 刷新列表
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 打开新增弹窗
const openAddDialog = () => {
  addDialogVisible.value = true
}

// 关闭弹窗并重置表单
const handleDialogClose = () => {
  addDialogVisible.value = false
  newGrade.grade = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 新增年级
const addGrade = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        api.addQuestionBank(
          '/grades/create/',
          newGrade,
          '添加年级失败',
          () => {
            ElMessage.success('年级添加成功')
            handleDialogClose()
            fetchGrades()
          },
        )
      } catch (error) {
        console.error('新增失败:', error)
        ElMessage.error('新增失败')
      }
    }
  })
}

// 页面加载时获取数据
fetchGrades()
</script>

<style scoped>
.grade-manage-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.grade-list-card {
  max-width: 800px;
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
