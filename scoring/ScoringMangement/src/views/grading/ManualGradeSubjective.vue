<template>
  <div class="manual-grade-container">
    <!-- 页面标题 -->


    <!-- 筛选条件卡片 -->
    <el-card class="filter-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-search"></i>
            <span>筛选条件</span>
          </div>
        </div>
      </template>
      <!-- 筛选表单 -->
      <el-form :inline="true" :model="filterForm" class="filter-form" label-width="80px">
        <el-row :gutter="20">
          <!-- 考试名称选择器 -->
          <el-col :span="10">
            <el-form-item label="考试名称">
              <el-select
                v-model="filterForm.examId"
                placeholder="请选择考试"
                @change="onExamChange"
                clearable
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="exam in exams"
                  :key="exam.id"
                  :label="exam.name"
                  :value="exam.id">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 查询按钮 -->
          <el-col :span="4">
            <el-form-item>
              <el-button type="primary" @click="loadExamPapers" class="gradient-button">查询</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 待批改试卷卡片 -->
    <el-card class="papers-card glass-card">
      <template #header>
        <div class="card-header">
          <div class="header-content">
            <i class="el-icon-document"></i>
            <span>待批改试卷</span>
          </div>
          <!-- 批量打分区域 -->
          <div class="batch-grading">
            <!-- 批量分数输入框 -->
            <el-input-number v-model="batchScore" :min="0" :max="100" size="small" style="margin-right: 10px;" class="score-input"></el-input-number>
            <!-- 批量打分按钮 -->
            <el-button type="success" @click="batchGrade" :disabled="selectedPapers.length === 0" class="gradient-button">批量打分</el-button>
          </div>
        </div>
      </template>

      <!-- 试卷表格 -->
      <el-table
        :data="examPapers"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        class="modern-table"
        stripe>
        <!-- 多选列 -->
        <el-table-column type="selection" width="55"></el-table-column>
        <!-- 学生姓名列 -->
        <el-table-column prop="studentName" label="学生姓名" min-width="120">
          <template #default="scope">
            <div class="student-info">
              <i class="el-icon-user"></i>
              <span>{{ scope.row.studentName }}</span>
            </div>
          </template>
        </el-table-column>
        <!-- 学号列 -->
        <el-table-column prop="studentId" label="学号" min-width="120"></el-table-column>
        <!-- 班级列 -->
        <el-table-column prop="className" label="班级" min-width="150"></el-table-column>
        <!-- 提交时间列 -->
        <el-table-column prop="submitTime" label="提交时间" min-width="200"></el-table-column>
        <!-- 主观题数量列 -->
        <el-table-column label="主观题数量" min-width="120">
          <template #default="scope">
            <span class="count-text">{{ scope.row.subjectiveCount }}</span>
          </template>
        </el-table-column>
        <!-- 状态列 -->
        <el-table-column label="状态" min-width="120">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'graded' ? 'success' : 'warning'" class="status-tag">
              {{ scope.row.status === 'graded' ? '已批改' : '未批改' }}
            </el-tag>
          </template>
        </el-table-column>
        <!-- 主观题得分列 -->
        <el-table-column label="主观题得分" min-width="120">
          <template #default="scope">
            <span v-if="scope.row.subjectiveScore !== undefined" class="score-text">
              {{ scope.row.subjectiveScore }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <!-- 操作列 -->
        <el-table-column label="操作" min-width="150">
          <template #default="scope">
            <el-button size="small" @click="gradePaper(scope.row)" class="action-button">批改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 试卷批改对话框 -->
    <el-dialog v-model="gradingDialogVisible" :title="'批改试卷 - ' + currentPaper.studentName" width="80%" top="5vh" class="grading-dialog">
      <div style="margin-bottom: 15px; text-align: right;">
        <el-button type="warning" @click="aiGradeAll" :loading="aiLoading" class="ai-grade-button">
          <i class="el-icon-magic-stick"></i> AI打分
        </el-button>
      </div>
      <div v-if="currentPaperQuestions.length > 0">
        <el-card v-for="(question, index) in currentPaperQuestions" :key="question.question_number" class="question-card glass-card" style="margin-bottom: 20px;">
          <template #header>
            <div class="question-header">
              <span>第{{ index + 1 }}题 (满分: {{ question.max_score }}分)</span>
              <span v-if="question.aiScore !== undefined" class="ai-score-tag">
                AI评分: {{ question.aiScore }}/{{ question.max_score }}
              </span>
            </div>
          </template>
          <div class="question-content">
            <div class="question-stem">
              <p><strong>题目内容:</strong></p>
              <p>{{ question.content }}</p>
            </div>
            <div class="student-answer">
              <p><strong>学生答案:</strong></p>
              <p>{{ question.student_answer }}</p>
            </div>
            <div class="standard-answer">
              <p><strong>标准答案:</strong></p>
              <p>{{ question.standard_answer }}</p>
            </div>
            <div class="question-score">
              <p><strong>评分:</strong></p>
              <el-input-number
                v-model="question.score"
                :min="0"
                :max="question.max_score"
                @change="onScoreChange"
                size="small"
                class="score-input">
              </el-input-number>
              <span style="margin-left: 10px;">/{{ question.max_score }}分</span>
              <el-button v-if="question.aiScore !== undefined" size="small" type="info" @click="applyAiScore(question)" class="apply-ai-btn">
                采用AI评分
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
      <div v-else>
        <p class="no-data">暂无题目信息</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="gradingDialogVisible = false" class="footer-button secondary">取消</el-button>
          <el-button type="primary" @click="submitGrades" class="footer-button primary">提交评分</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import examService from '@/services/examService';
import paperService from '@/services/paperService';
import classService from '@/services/classService';
import reportService from '@/services/reportService';

export default {
  setup() {
    const filterForm = ref({
      examId: '',
      classId: ''
    });
    const exams = ref([]);
    const classes = ref([]);
    const examPapers = ref([]);
    const selectedPapers = ref([]);
    const batchScore = ref(0);

    // 批改对话框相关
    const gradingDialogVisible = ref(false);
    const currentPaper = ref({});
    const currentPaperQuestions = ref([]);
    const aiLoading = ref(false);

    const loadExams = async () => {
      try {
        const response = await examService.getExams();
        exams.value = response.data.map(exam => {
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
        });
      } catch (error) {
        console.error('加载考试列表失败:', error);
        ElMessage.error('加载考试列表失败');
      }
    };

    const loadClasses = async () => {
      try {
        const response = await classService.getClasses();
        classes.value = response.data.map(classItem => {
          // 修复字符编码问题
          let name = classItem.class1?.class_name;
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
            id: classItem.id,
            name: name || '未知班级'
          }
        });
      } catch (error) {
        console.error('加载班级列表失败:', error);
        ElMessage.error('加载班级列表失败: ' + (error.response?.data?.message || error.message));
      }
    };

    // 根据考试ID获取参加该考试的班级列表
    const loadClassesByExam = async (examId) => {
      if (!examId) {
        // 如果没有选择考试，加载所有班级
        await loadClasses();
        return;
      }

      try {
        const response = await reportService.getClassesByExam(examId);
        classes.value = response.data;
      } catch (error) {
        console.error('获取考试相关班级列表失败:', error);
        ElMessage.error('获取考试相关班级列表失败: ' + (error.response?.data?.message || error.message));
        classes.value = [];
      }
    };

    const loadExamPapers = async () => {
      try {
        if (!filterForm.value.examId) {
          examPapers.value = [];
          return;
        }

        const response = await paperService.getPapersByExamId(filterForm.value.examId, filterForm.value.classId);
        const papers = response.data;
        examPapers.value = papers.map(paper => {
          // 获取主观题数量（采用与客观题相同的健壮处理方式）
          let subjectiveCount = 0;
          // 明确检查所有可能的来源
          if (typeof paper.subjective_count === 'number') {
            subjectiveCount = paper.subjective_count;
          } else if (paper.subjective_details && Array.isArray(paper.subjective_details)) {
            subjectiveCount = paper.subjective_details.length;
          } else if (paper.subjective_details && typeof paper.subjective_details === 'object') {
            subjectiveCount = Object.keys(paper.subjective_details).length;
          }

          // 获取主观题得分
          let subjectiveScore = 0;
          if (paper.subjective_details && Array.isArray(paper.subjective_details)) {
            subjectiveScore = paper.subjective_details.reduce((total, item) => {
              return total + (item.score || 0);
            }, 0);
          }

          return {
            id: paper.id || paper.number,
            studentName: (paper.user?.last_name || '') + (paper.user?.first_name || '') || '未知学生',
            studentId: paper.user?.id || '',
            className: paper.user?.class1?.class1?.class_name || '未知班级',
            submitTime: paper.end_time ? new Date(paper.end_time).toLocaleString() : '',
            subjectiveCount: subjectiveCount,
            status: paper.status ? 'graded' : 'pending',
            subjectiveScore: subjectiveScore
          };
        });
      } catch (error) {
        console.error('加载试卷列表失败:', error);
        ElMessage.error('加载试卷列表失败: ' + (error.response?.data?.message || error.message));
      }
    };

    const onExamChange = (examId) => {
      filterForm.value.examId = examId;
      filterForm.value.classId = ''; // 重置班级选择

      if (examId) {
        // 加载参加该考试的班级
        loadClassesByExam(examId);
      } else {
        // 如果没有选择考试，加载所有班级
        loadClasses();
      }

      // 清空试卷列表
      examPapers.value = [];
    };

    const handleSelectionChange = (val) => {
      selectedPapers.value = val;
    };

    const gradePaper = async (paper) => {
      try {
        // 获取试卷的主观题详情
        const paperDetailResponse = await paperService.getSubjectiveQuestions(paper.id);
        const questions = paperDetailResponse.data.questions;

        // 设置当前试卷和题目信息
        currentPaper.value = paper;
        currentPaperQuestions.value = questions.map(question => ({
          ...question,
          score: question.score !== null ? question.score : 0
        }));

        // 显示批改对话框
        gradingDialogVisible.value = true;
      } catch (error) {
        console.error('获取试卷详情失败:', error);
        ElMessage.error('获取试卷详情失败: ' + (error.response?.data?.message || error.message));
      }
    };

    const onScoreChange = () => {
      // 分数变化时的处理函数
    };

    const submitGrades = async () => {
      try {
        // 构造主观题得分数据
        const subjectiveScores = currentPaperQuestions.value.map(question => ({
          question_number: question.question_number,
          score: question.score
        }));

        // 提交主观题得分
        const response = await paperService.manualGradeSubjective(currentPaper.value.id, {
          subjective_scores: subjectiveScores
        });

        // 更新表格中的数据
        const index = examPapers.value.findIndex(p => p.id === currentPaper.value.id);
        if (index !== -1) {
          examPapers.value[index].subjectiveScore = response.data.subjective_score;
          examPapers.value[index].status = 'graded';
        }

        // 关闭对话框
        gradingDialogVisible.value = false;

        ElMessage.success('评分提交成功');
      } catch (error) {
        console.error('评分提交失败:', error);
        ElMessage.error('评分提交失败: ' + (error.response?.data?.message || error.message));
      }
    };

    const aiGradeAll = async () => {
      aiLoading.value = true;
      try {
        const response = await paperService.aiGradeSubjective(currentPaper.value.id);
        const aiScores = response.data.ai_scores;
        
        console.log('AI评分返回数据:', aiScores);
        console.log('当前题目列表:', currentPaperQuestions.value);
        
        currentPaperQuestions.value.forEach(question => {
          console.log(`匹配题目 ${question.question_number}:`, question);
          const aiScoreData = aiScores.find(item => item.question_number === question.question_number);
          console.log(`找到匹配的AI评分:`, aiScoreData);
          if (aiScoreData) {
            question.aiScore = aiScoreData.ai_score;
            console.log(`已更新题目 ${question.question_number} 的 AI 分数为:`, question.aiScore);
          }
        });
        
        console.log('更新后的题目列表:', currentPaperQuestions.value);
        
        ElMessage.success('AI打分完成');
      } catch (error) {
        console.error('AI打分失败:', error);
        ElMessage.error('AI打分失败: ' + (error.response?.data?.message || error.message));
      } finally {
        aiLoading.value = false;
      }
    };

    const applyAiScore = (question) => {
      question.score = question.aiScore;
      ElMessage.success(`已采用AI评分: ${question.aiScore}分`);
    };

    const batchGrade = async () => {
      if (selectedPapers.value.length === 0) {
        ElMessage.warning('请先选择需要批改的试卷');
        return;
      }

      try {
        // 批量给主观题打分
        for (let i = 0; i < selectedPapers.value.length; i++) {
          const paper = selectedPapers.value[i];
          // 这里需要获取试卷的主观题详情，然后给每道主观题打分
          // 由于这是一个演示，我们假设所有主观题都打相同的分数

          // 获取试卷的主观题详情
          const paperDetailResponse = await paperService.getSubjectiveQuestions(paper.id);
          const subjectiveQuestions = paperDetailResponse.data.questions;

          // 构造主观题得分数据
          const subjectiveScores = subjectiveQuestions.map(question => ({
            question_number: question.question_number,
            score: batchScore.value
          }));

          // 提交主观题得分
          const response = await paperService.manualGradeSubjective(paper.id, {
            subjective_scores: subjectiveScores
          });

          // 更新表格中的数据
          const index = examPapers.value.findIndex(p => p.id === paper.id);
          if (index !== -1) {
            examPapers.value[index].subjectiveScore = response.data.subjective_score;
            examPapers.value[index].status = 'graded';
          }
        }

        ElMessage.success('批量打分成功');
        // 清空选择
        selectedPapers.value = [];
      } catch (error) {
        console.error('批量打分失败:', error);
        ElMessage.error('批量打分失败: ' + (error.response?.data?.message || error.message));
      }
    };

    onMounted(() => {
      loadExams();
      loadClasses();
    });

    return {
      filterForm,
      exams,
      classes,
      examPapers,
      selectedPapers,
      batchScore,
      loadExams,
      loadClasses,
      loadExamPapers,
      onExamChange,
      handleSelectionChange,
      gradePaper,
      batchGrade,
      // 批改对话框相关
      gradingDialogVisible,
      currentPaper,
      currentPaperQuestions,
      onScoreChange,
      submitGrades,
      aiLoading,
      aiGradeAll,
      applyAiScore
    };
  }
};
</script>

<style scoped>
.manual-grade-container {
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

.filter-card, .papers-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
  animation: fadeInUp 0.8s ease;
}

.filter-card:hover, .papers-card:hover {
  box-shadow: 0 15px 40px rgba(26, 115, 232, 0.25);
  transform: translateY(-5px);
}

.glass-card {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
  flex-wrap: wrap;
  gap: 15px;
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

.batch-grading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-form {
  width: 100%;
  padding: 20px;
}

.question-card {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  border-radius: 12px;
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease;
}

.question-card:hover {
  box-shadow: 0 6px 20px rgba(26, 115, 232, 0.25);
  transform: translateY(-3px);
}

.question-card :deep(.el-card__header) {
  background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
  font-weight: 600;
  color: #1a73e8;
  border-bottom: 1px solid rgba(64, 158, 255, 0.2);
}

.question-header {
  font-weight: bold;
  font-size: 16px;
  color: #1a73e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-score-tag {
  background: linear-gradient(45deg, #ff9800, #ff5722);
  color: white;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
  animation: fadeIn 0.5s ease;
}

.ai-grade-button {
  background: linear-gradient(45deg, #ff9800, #ff5722);
  border: none;
  color: white;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
  transition: all 0.3s ease;
}

.ai-grade-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 152, 0, 0.4);
}

.apply-ai-btn {
  margin-left: 15px;
  background: linear-gradient(45deg, #4caf50, #45a049);
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.apply-ai-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.question-content > div {
  margin-bottom: 15px;
}

.question-stem, .student-answer, .standard-answer {
  padding: 15px;
  border-radius: 8px;
}

.question-stem {
  background-color: #e3f2fd;
  border: 1px solid #90caf9;
}

.student-answer {
  background-color: #fff8e1;
  border: 1px solid #ffe082;
}

.standard-answer {
  background-color: #e8f5e9;
  border: 1px solid #a5d6a7;
}

.question-score {
  padding: 15px;
  background-color: #fff3e0;
  border: 1px solid #ffcc80;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-input :deep(.el-input-number__decrease),
.score-input :deep(.el-input-number__increase) {
  background: #f0f2f5;
}

.gradient-button {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
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

.gradient-button:disabled {
  background: #c0c4cc;
  transform: none;
  box-shadow: none;
}

.modern-table :deep(.el-table__row:hover) {
  background-color: #f0f9ff;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  border-radius: 20px;
  padding: 5px 12px;
}

.count-text, .score-text {
  font-weight: 700;
  color: #1a73e8;
}

.action-button {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  border: none;
  color: white;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.4);
}

.no-data {
  text-align: center;
  color: #909399;
  font-size: 16px;
  padding: 30px;
}

.grading-dialog :deep(.el-dialog__header) {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  color: white;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.grading-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 500;
}

.footer-button {
  padding: 10px 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.footer-button.primary {
  background: linear-gradient(45deg, #1a73e8, #4285f4);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3);
}

.footer-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(26, 115, 232, 0.4);
}

.footer-button.secondary {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.footer-button.secondary:hover {
  background: #e4e7ed;
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

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .manual-grade-container {
    padding: 15px;
  }

  .page-title {
    font-size: 24px;
  }

  .filter-card, .papers-card {
    border-radius: 10px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
  }

  .batch-grading {
    width: 100%;
    justify-content: flex-end;
  }

  .filter-form {
    padding: 15px;
  }
}
</style>
