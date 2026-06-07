<template>
  <div class="export-report-container">
    <!-- 页面标题 -->


    <!-- 导出设置卡片 -->
    <el-card class="filter-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-setting"></i>
            <span>导出设置</span>
          </div>
        </div>
      </template>
      <!-- 导出设置表单 -->
      <el-form :model="exportForm" label-width="120px" class="export-form">
        <el-row :gutter="20">
          <!-- 考试名称选择 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="考试名称">
              <el-select v-model="exportForm.examId" @change="onExamChange" style="width: 100%">
                <el-option
                  v-for="exam in exams"
                  :key="exam.id"
                  :label="exam.name"
                  :value="exam.id.toString()">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <!-- 班级选择（支持多选） -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="班级">
              <el-select v-model="exportForm.classId" clearable multiple style="width: 100%">
                <el-option
                  v-for="classItem in classes"
                  :key="classItem.id"
                  :label="classItem.name"
                  :value="classItem.id.toString()">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <!-- 报表类型选择 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="报表类型">
              <el-select v-model="exportForm.reportType" style="width: 100%">
                <el-option label="成绩单" value="grade"></el-option>
                <el-option label="成绩分析报告" value="analysis"></el-option>
                <el-option label="排名表" value="ranking"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <!-- 导出格式选择 -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="导出格式">
              <el-select v-model="exportForm.exportFormat" style="width: 100%">
                <el-option label="Excel (.xlsx)" value="xlsx"></el-option>
                <el-option label="CSV (.csv)" value="csv"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <!-- 包含内容选择（复选框） -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="包含内容">
              <el-checkbox-group v-model="exportForm.includeContent">
                <div class="checkbox-group">
                  <el-checkbox label="客观题得分">客观题得分</el-checkbox>
                  <el-checkbox label="主观题得分">主观题得分</el-checkbox>
                  <el-checkbox label="总分">总分</el-checkbox>
                  <el-checkbox label="全校排名">考试排名</el-checkbox>
                </div>
              </el-checkbox-group>
            </el-form-item>
          </el-col>
          <!-- 排序方式选择（单选框） -->
          <el-col :xs="24" :sm="24" :md="12" :lg="12">
            <el-form-item label="排序方式">
              <el-radio-group v-model="exportForm.sortBy">
                <div class="radio-group">
                  <el-radio label="score">按分数</el-radio>
                  <el-radio label="studentId">按考号</el-radio>
                </div>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-form-item class="button-group">
          <el-button type="primary" @click="previewReport" class="gradient-button preview-button">预览</el-button>
          <el-button type="success" @click="exportReport" :loading="exportLoading" class="gradient-button export-button">导出报表</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报表预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="报表预览" :width="isMobile ? '95%' : '80%'" top="5vh" class="preview-dialog">
      <div class="dialog-content">
        <div v-if="previewData && previewData.length > 0">
          <!-- 预览表格 -->
          <el-table :data="previewData" :height="isMobile ? 300 : 400" style="width: 100%" class="preview-table" stripe>
            <el-table-column
              v-for="column in previewColumns"
              :key="column.prop"
              :prop="column.prop"
              :label="column.label"
              :width="column.width">
            </el-table-column>
          </el-table>
        </div>
        <div v-else>
          <!-- 无数据提示 -->
          <el-alert title="暂无数据" type="info" description="没有找到符合条件的成绩数据，请检查筛选条件或确认是否有相关考试记录。" show-icon class="no-data-alert"></el-alert>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false" class="footer-button secondary">关闭</el-button>
          <el-button type="success" @click="exportReport" :loading="exportLoading" class="footer-button primary">导出报表</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 提示信息弹窗 -->
    <el-dialog v-model="infoDialogVisible" title="提示" width="30%" center class="info-dialog">
      <div class="dialog-content">
        <i class="el-icon-warning-outline" style="font-size: 48px; color: #e6a23c; display: block; text-align: center; margin-bottom: 15px;"></i>
        <span style="display: block; text-align: center; font-size: 16px;">{{ infoMessage }}</span>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="infoDialogVisible = false" class="footer-button">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import examService from '@/services/examService'
import classService from '@/services/classService'
import reportService from '@/services/reportService'

export default {
  name: 'ExportGradeReport',
  data() {
    return {
      // 导出表单数据
      exportForm: {
        examId: '',                     // 考试ID
        classId: [],                    // 班级ID数组（支持多选）
        reportType: 'grade',            // 报表类型：grade-成绩单, analysis-成绩分析报告, ranking-排名表
        exportFormat: 'xlsx',           // 导出格式：xlsx-Excel, csv-CSV
        includeContent: ['客观题得分', '主观题得分', '总分', '考试排名'],  // 包含内容
        sortBy: 'class'                 // 排序方式：class-按班级, score-按分数, studentId-按学号
      },
      exams: [],                        // 考试列表
      classes: [],                      // 班级列表
      exportLoading: false,             // 导出加载状态
      previewDialogVisible: false,      // 预览对话框显示状态
      previewData: [],                  // 预览数据
      previewColumns: [                 // 预览表格列定义
        { prop: '学号', label: '学号', width: 120 },
        { prop: '姓名', label: '姓名', width: 120 },
        { prop: '班级', label: '班级', width: 120 },
        { prop: '客观题得分', label: '客观题得分', width: 120 },
        { prop: '主观题得分', label: '主观题得分', width: 120 },
        { prop: '总分', label: '总分', width: 100 },
        { prop: '班级排名', label: '班级排名', width: 100 }
      ],
      infoDialogVisible: false,         // 提示信息弹窗显示状态
      infoMessage: ''                   // 提示信息内容
    }
  },
  computed: {
    // 检测是否为移动设备
    isMobile() {
      return window.innerWidth < 768
    }
  },
  async mounted() {
    // 组件挂载时加载考试和班级数据
    await this.loadExams()
    await this.loadClasses()
  },
  methods: {
    // 获取考试列表
    async loadExams() {
      try {
        const response = await examService.getExams()
        this.exams = response.data.map(exam => {
          // 修复字符编码问题
          let name = exam.name;
          try {
            // 尝试修复可能的编码问题
            name = decodeURIComponent(escape(name));
          } catch (e) {
            // 检查是否是编码问题导致的异常
            if (e instanceof URIError) {
              // URIError表示编码不正确，使用原始名称
              console.warn('字符编码修复失败，使用原始名称:', name);
            } else {
              // 其他错误重新抛出
              throw e;
            }
          }

          return {
            id: exam.number || exam.id,
            name: name || '未知考试'
          }
        })
      } catch (error) {
        // 移除弹窗提示，仅在控制台输出错误信息
        console.error('获取考试列表失败:', error)
        ElMessage.error('获取考试列表失败: ' + (error.response?.data?.message || error.message))
      }
    },

    // 获取班级列表
    async loadClasses() {
      try {
        const response = await classService.getClasses()
        this.classes = response.data.map(cls => {
          // 正确处理班级名称：class1是一个对象，包含class_name属性
          let className = '';
          if (cls.class1 && typeof cls.class1 === 'object' && cls.class1.class_name) {
            className = cls.class1.class_name;
          } else {
            className = '未知班级';
          }

          // 确保className是字符串类型
          if (typeof className !== 'string') {
            className = String(className);
          }

          return {
            id: cls.id,
            name: className
          }
        })
      } catch (error) {
        // 移除弹窗提示，仅在控制台输出错误信息
        console.error('获取班级列表失败:', error)
        ElMessage.error('获取班级列表失败: ' + (error.response?.data?.message || error.message))
      }
    },

    // 根据考试ID获取参加该考试的班级列表
    async loadClassesByExam(examId) {
      if (!examId) {
        // 如果没有选择考试，加载所有班级
        await this.loadClasses();
        return;
      }

      try {
        const response = await reportService.getClassesByExam(examId);
        this.classes = response.data;
      } catch (error) {
        console.error('获取考试相关班级列表失败:', error);
        ElMessage.error('获取考试相关班级列表失败: ' + (error.response?.data?.message || error.message));
        this.classes = [];
      }
    },

    // 考试选择变化时的处理函数
    async onExamChange(examId) {
      this.exportForm.examId = examId;
      this.exportForm.classId = []; // 重置班级选择

      if (examId) {
        // 加载参加该考试的班级
        await this.loadClassesByExam(examId);
      } else {
        // 如果没有选择考试，加载所有班级
        await this.loadClasses();
      }
    },

    // 预览报表
    async previewReport() {
      // 检查是否选择了考试
      if (!this.exportForm.examId) {
        this.infoMessage = '请选择考试'
        this.infoDialogVisible = true
        return
      }

      try {
        // 构造请求参数
        const params = {
          exam_id: this.exportForm.examId,
          report_type: this.exportForm.reportType,
          sort_by: this.exportForm.sortBy
        }

        // 只有当选择了班级时才添加class_ids参数
        if (this.exportForm.classId && this.exportForm.classId.length > 0) {
          // 将数组转换为逗号分隔的字符串
          params.class_ids = this.exportForm.classId.join(',');
        }

        // 显示加载状态
        this.exportLoading = true

        // 调用服务预览报表
        const response = await reportService.previewReport(params)
        this.previewData = response.data

        // 确保在有数据时才显示预览对话框
        if (this.previewData && this.previewData.length > 0) {
          this.previewDialogVisible = true
        } else {
          // 如果没有数据，显示提示信息
          ElMessage.warning('没有找到符合条件的数据')
        }
      } catch (error) {
        // 显示错误信息
        console.error('预览报表失败:', error)
        ElMessage.error('预览报表失败: ' + (error.response?.data?.message || error.message || '未知错误'))
      } finally {
        this.exportLoading = false
      }
    },

    // 导出报表
    async exportReport() {
      // 检查是否选择了考试
      if (!this.exportForm.examId) {
        this.infoMessage = '请选择考试'
        this.infoDialogVisible = true
        return
      }

      try {
        // 构造导出参数
        let params = {
          exam_id: this.exportForm.examId,
          report_type: this.exportForm.reportType,
          sort_by: this.exportForm.sortBy,
          format_type: this.exportForm.exportFormat
        };

        // 只有当选择了班级时才添加class_ids参数
        if (this.exportForm.classId && this.exportForm.classId.length > 0) {
          // 将数组转换为逗号分隔的字符串
          params.class_ids = this.exportForm.classId.join(',');
        }

        // 显示加载状态
        this.exportLoading = true

        // 调用服务导出报表
        const response = await reportService.exportReport(params)

        // 创建下载链接并触发下载
        const blob = new Blob([response.data], { type: response.headers['content-type'] || 'application/octet-stream' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `成绩报表.${this.exportForm.exportFormat}`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

        ElMessage.success('导出成功')
        this.previewDialogVisible = false
      } catch (error) {
        console.error('导出报表失败:', error)
        ElMessage.error('导出报表失败: ' + (error.response?.data?.message || error.message || '未知错误'))
      } finally {
        this.exportLoading = false
      }
    }
  }
}
</script>

<style scoped>
/* 导出报表容器样式 */
.export-report-container {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
  background: linear-gradient(135deg, #e4f3ff 0%, #f0f9ff 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  animation: fadeInDown 0.8s ease;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1a73e8;
  text-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
}

.page-subtitle {
  font-size: 16px;
  color: #5f6368;
  font-weight: 400;
}

/* 筛选卡片样式 */
.filter-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease;
}

.filter-card:hover {
  box-shadow: 0 15px 40px rgba(26, 115, 232, 0.25);
  transform: translateY(-5px);
}

.glass-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
  flex-wrap: wrap;
  gap: 10px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1a73e8;
  font-size: 18px;
}

.header-content i {
  font-size: 20px;
  color: #1a73e8;
}

.export-form {
  width: 100%;
  padding: 20px;
}

/* 复选框组样式 */
.checkbox-group .el-checkbox {
  margin-right: 15px;
  margin-bottom: 10px;
  display: block;
}

/* 单选框组样式 */
.radio-group .el-radio {
  margin-bottom: 10px;
  display: block;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.gradient-button {
  border: none;
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
}

.gradient-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(26, 115, 232, 0.4);
}

.preview-button {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
}

.export-button {
  background: linear-gradient(45deg, #0f9d58, #34a853);
}

.preview-table :deep(.el-table__row:hover) {
  background-color: #f0f9ff;
}

.no-data-alert {
  border-radius: 10px;
}

.preview-dialog :deep(.el-dialog__header) {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  color: white;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.preview-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 500;
}

.info-dialog :deep(.el-dialog__header) {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  color: white;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.info-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 500;
}

.footer-button {
  padding: 10px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.footer-button.primary {
  background: linear-gradient(45deg, #0f9d58, #34a853);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(15, 157, 88, 0.3);
}

.footer-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(15, 157, 88, 0.4);
}

.footer-button.secondary {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.footer-button.secondary:hover {
  background: #e4e7ed;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .export-report-container {
    padding: 15px;
  }

  .page-title {
    font-size: 24px;
  }

  .filter-card {
    border-radius: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
  }

  .button-group {
    flex-direction: column;
    gap: 10px;
  }

  .gradient-button {
    width: 100%;
  }

  .export-form {
    padding: 15px;
  }

  .checkbox-group .el-checkbox {
    display: block;
    margin-bottom: 8px;
  }

  .radio-group .el-radio {
    display: block;
    margin-bottom: 8px;
  }
}

@media (max-width: 480px) {
  .el-dialog {
    margin: 10px;
  }

  .el-dialog__header {
    padding: 15px;
  }

  .el-dialog__body {
    padding: 15px;
  }

  .el-dialog__footer {
    padding: 15px;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
