<template>
  <div class="audit-page-wrapper">
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <div class="main-content">
      <header class="page-header">
        <div class="header-left">
          <div class="title-icon"><i class="fas fa-history"></i></div>
          <div>
            <h1>审计日志</h1>
            <p>系统操作行为全记录，保障数据安全可追溯</p>
          </div>
        </div>
        <div class="header-right">
          <el-button type="danger" @click="deleteAllLogs" icon="Delete" class="glass-btn" style="margin-right: 10px;">
            清空全部
          </el-button>
          <el-button type="success" @click="exportLogs" icon="Download" class="glass-btn">
            导出报表
          </el-button>
        </div>
      </header>

      <section class="glass-card filter-card">
        <el-form :model="filterForm" inline class="modern-form">
          <el-form-item label="操作用户">
            <el-input v-model="filterForm.user" placeholder="用户名" clearable />
          </el-form-item>
          <el-form-item label="操作类型">
            <el-select v-model="filterForm.operationType" placeholder="请选择" clearable style="width: 140px">
              <el-option label="题库管理" value="题库管理" />
              <el-option label="考试创建" value="考试创建" />
              <el-option label="答题提交" value="答题提交" />
              <el-option label="评分" value="评分" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              value-format="YYYY-MM-DD"
              class="modern-date"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchLogs" icon="Search" class="action-btn">查询</el-button>
            <el-button @click="resetFilter" icon="Refresh" class="action-btn-sub">重置</el-button>
          </el-form-item>
        </el-form>
      </section>

      <section class="glass-card table-card">
        <div class="table-top-info">
          <span><i class="fas fa-list-ul"></i> 数据列表</span>
          <el-text class="total-text">当前筛选条件下共 <b>{{ pagination.total }}</b> 条记录</el-text>
        </div>

        <el-table
          :data="logData"
          v-loading="loading"
          class="modern-table"
          row-class-name="log-row"
          style="width: 100%"
        >
          <el-table-column prop="id" label="ID" width="80" align="center" />

          <el-table-column prop="username" label="操作者" width="140">
            <template #default="{row}">
              <div class="user-cell">
                <el-avatar :size="24" icon="UserFilled" class="user-avatar" />
                <span>{{ row.username }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="operation_type" label="类型" width="130" align="center">
            <template #default="{row}">
              <span :class="['status-dot', getTypeClass(row.operation_type)]">
                {{ row.operation_type }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="content" label="操作详情" min-width="300" show-overflow-tooltip />

          <el-table-column prop="operation_time" label="操作时间" width="200" align="center">
            <template #default="{row}">
              <span class="time-text"><i class="far fa-clock"></i> {{ row.operation_time }}</span>
            </template>
          </el-table-column>

          <el-table-column label="管理" width="150" align="center" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" link @click="viewDetail(scope.row)">
                查看详情
              </el-button>
              <el-button size="small" type="danger" link @click="deleteSingleLog(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            background
          />
        </div>
      </section>
    </div>

    <el-dialog v-model="detailDialogVisible" title="操作日志明细" width="550px" destroy-on-close class="custom-dialog">
      <div class="detail-content">
        <div class="detail-item">
          <span class="label">操作用户：</span>
          <span class="val">{{ currentLog.username }}</span>
        </div>
        <div class="detail-item">
          <span class="label">操作类型：</span>
          <span :class="['status-dot', getTypeClass(currentLog.operation_type)]">{{ currentLog.operation_type }}</span>
        </div>
        <div class="detail-item">
          <span class="label">执行时间：</span>
          <span class="val">{{ currentLog.operation_time }}</span>
        </div>
        <div class="detail-item vertical">
          <span class="label">具体内容：</span>
          <div class="content-box">{{ currentLog.content }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from "@/services/api11.ts";

const filterForm = ref({ user: '', operationType: '', dateRange: [] as string[] })
const pagination = ref({ currentPage: 1, pageSize: 10, total: 0 })
const logData = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const currentLog = ref<any>({})

const getTypeClass = (type: string) => {
  const map: any = {
    '题库管理': 'type-primary',
    '考试创建': 'type-success',
    '答题提交': 'type-warning',
    '评分': 'type-danger'
  }
  return map[type] || 'type-info'
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.currentPage,
      page_size: pagination.value.pageSize,
      search: filterForm.value.user || undefined,
      operation_type: filterForm.value.operationType || undefined
    }
    if (filterForm.value.dateRange?.length === 2) {
      params.start_date = filterForm.value.dateRange[0]
      params.end_date = filterForm.value.dateRange[1]
    }
    const response = await api.get('/operation-records/', { params })

    // 兼容后端本地分页和接口分页逻辑
    if (Array.isArray(response)) {
      pagination.value.total = response.length
      const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
      logData.value = response.slice(start, start + pagination.value.pageSize)
    } else {
      logData.value = response.results || []
      pagination.value.total = response.count || 0
    }
  } catch (error: any) {
    ElMessage.error('加载失败');
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.value = { user: '', operationType: '', dateRange: [] }
  fetchLogs()
}

const viewDetail = (row: any) => {
  currentLog.value = row
  detailDialogVisible.value = true
}

// 删除单条日志
const deleteSingleLog = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定删除该条日志吗？此操作不可恢复', '警告', { type: 'warning' })
    await api.delete(`/operation-records/${row.id}/`)
    ElMessage.success('删除成功')
    fetchLogs()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 清空全部日志
const deleteAllLogs = async () => {
  try {
    await ElMessageBox.confirm('确定清空全部日志吗？此操作不可恢复，请谨慎操作！', '严重警告', {
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    })
    
    loading.value = true
    // 循环删除所有日志
    for (const log of logData.value) {
      await api.delete(`/operation-records/${log.id}/`)
    }
    
    ElMessage.success('清空成功')
    fetchLogs()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pagination.value.pageSize = val
  fetchLogs()
}

const handleCurrentChange = (val: number) => {
  pagination.value.currentPage = val
  fetchLogs()
}

const exportLogs = () => {
  ElMessageBox.confirm('确定导出日志报表吗？', '系统提示', { type: 'info' }).then(async () => {
    ElMessage.info('导出功能已触发...');
    // 导出逻辑保持原样...
  })
}

onMounted(fetchLogs)
</script>

<style scoped>
/* 全局容器及渐变背景 */
.audit-page-wrapper {
  min-height: 100vh;
  background-color: #f0f7ff;
  position: relative;
  overflow-x: hidden;
  padding: 24px;
}

.bg-decoration {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  z-index: 0;
  pointer-events: none;
}

.blob {
  position: absolute;
  filter: blur(80px);
  opacity: 0.4;
  border-radius: 50%;
}
.blob-1 {
  width: 500px; height: 500px;
  background: #1890ff;
  top: -200px; right: -100px;
}
.blob-2 {
  width: 400px; height: 400px;
  background: #69c0ff;
  bottom: -100px; left: -100px;
}

/* 玻璃卡片样式 */
.main-content {
  position: relative;
  z-index: 1;
  max-width: 1300px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.08);
  margin-bottom: 20px;
  padding: 24px;
}

/* 头部样式 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.page-header h1 {
  font-size: 22px;
  margin: 0;
  color: #1a1a1a;
}

.page-header p {
  font-size: 14px;
  color: #64748b;
  margin: 4px 0 0;
}

/* 筛选表单 */
.modern-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: #475569;
}

.action-btn {
  background: #1890ff;
  border-radius: 8px;
  padding: 0 20px;
}

.action-btn-sub {
  border-radius: 8px;
  color: #64748b;
}

/* 表格定制 */
.table-top-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-weight: 600;
  color: #334155;
}

.total-text b { color: #1890ff; }

.modern-table {
  background: transparent !important;
  --el-table-border-color: rgba(226, 232, 240, 0.6);
}

.modern-table :deep(tr) {
  background: transparent !important;
}

.modern-table :deep(th) {
  background: rgba(241, 245, 249, 0.6) !important;
  font-weight: 700;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1e293b;
  font-weight: 500;
}

.user-avatar { background: #e0f2fe; color: #0ea5e9; }

/* 状态圆点标签 */
.status-dot {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  position: relative;
  display: inline-block;
}

.type-primary { background: #e0f2fe; color: #0369a1; }
.type-success { background: #dcfce7; color: #15803d; }
.type-warning { background: #fef3c7; color: #b45309; }
.type-danger  { background: #fee2e2; color: #b91c1c; }
.type-info    { background: #f1f5f9; color: #475569; }

.time-text { color: #64748b; font-size: 13px; }

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 详情弹窗定制 */
.custom-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  border-bottom: 1px dashed #e2e8f0;
  padding-bottom: 12px;
}

.detail-item.vertical {
  flex-direction: column;
  align-items: flex-start;
  border-bottom: none;
}

.detail-item .label {
  width: 80px;
  color: #64748b;
  font-weight: 600;
}

.content-box {
  width: 100%;
  margin-top: 10px;
  background: #f8fafc;
  padding: 15px;
  border-radius: 8px;
  color: #334155;
  line-height: 1.6;
}
</style>
