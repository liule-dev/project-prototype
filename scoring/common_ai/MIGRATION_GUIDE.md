# AI 服务统一重构说明

## ✅ 已完成的优化

### 1. 删除根目录杂乱文件
- ✅ 删除 `error_response.html` (209.9KB)
- ✅ 删除 `response.txt` (206.3KB)
- ✅ 删除 `teacher_topic.zip` (24.0KB)
- ✅ 删除 `test.xlsx` (5.5KB)
- ✅ 删除 `test_api.py`

### 2. 创建统一 AI 服务模块
创建了 `common_ai/` 目录，包含：
- `__init__.py` - 模块入口
- `apps.py` - Django app 配置
- `base.py` - AI 服务基类（通用 API 调用）
- `grading.py` - AI 批改服务
- `study_assistant.py` - 学习辅助服务（对话、学习计划、错题分析）

---

## 🔄 需要更新的代码

### **步骤1：更新 management/views.py**

**原代码**：
```python
from .ai_service import AIService

ai_service = AIService()
score = ai_service.grade_subjective_question(...)
```

**改为**：
```python
from common_ai.grading import GradingService

grading_service = GradingService()
score = grading_service.grade_subjective_question(...)
```

---

### **步骤2：更新 notebook/views.py**

**原代码**：
```python
from .ai_service import generate_study_plan, analyze_wrong_topics

plan = generate_study_plan(subjects, time_frame, goals)
analysis = analyze_wrong_topics(wrong_topics_data)
```

**改为**：
```python
from common_ai.study_assistant import StudyAssistantService

assistant = StudyAssistantService()
plan = assistant.generate_study_plan(subjects, time_frame, goals)
analysis = assistant.analyze_wrong_topics(wrong_topics_data)
reply = assistant.chat_with_ai(user_message)
```

---

### **步骤3：更新 exam/views.py（如果有 AI 相关功能）**

**原代码**：
```python
from .ai_service import generate_exam_questions

questions = generate_exam_questions(...)
```

**改为**：
```python
from common_ai.base import QwenAIService

ai_service = QwenAIService()
# 根据需要添加试题生成方法
```

---

### **步骤4：删除旧的 ai_service.py 文件**

确认所有引用都已更新后，可以删除：
- ❌ `management/ai_service.py`
- ❌ `notebook/ai_service.py`
- ❌ `exam/ai_service.py`

---

## 🎯 优势

### **之前的问题**
- ❌ 3 个独立的 ai_service.py，代码重复
- ❌ API Key 配置分散在多处
- ❌ 超时设置、错误处理不一致
- ❌ 修改 API 需要改 3 个地方

### **现在的优势**
- ✅ 统一的 AI 服务入口
- ✅ 只需在一个地方配置 API Key（settings.py）
- ✅ 统一的超时策略（30秒）、错误处理
- ✅ 易于维护和扩展
- ✅ 方便添加新功能（如缓存、限流、日志）

---

## 📝 使用示例

### **AI 批改主观题**
```python
from common_ai.grading import GradingService

service = GradingService()
score = service.grade_subjective_question(
    question_content="简述货币政策的作用",
    student_answer="货币政策可以调节...",
    standard_answer="货币政策通过调节货币供应量...",
    max_score=10
)
print(f"AI 评分: {score}")
```

### **生成学习计划**
```python
from common_ai.study_assistant import StudyAssistantService

assistant = StudyAssistantService()
plan = assistant.generate_study_plan(
    subjects=['金融学', '经济学'],
    time_frame='30天',
    goals='通过CFA一级考试'
)
print(plan)
```

### **AI 对话**
```python
from common_ai.study_assistant import StudyAssistantService

assistant = StudyAssistantService()
reply = assistant.chat_with_ai("什么是通货膨胀？")
print(reply)
```

---

## ⚠️ 注意事项

1. **测试后再删除旧文件**：先更新引用，测试功能正常后再删除旧的 ai_service.py
2. **保持向后兼容**：如果某些模块暂时无法更新，可以保留旧的 ai_service.py
3. **API Key 安全**：生产环境建议使用环境变量，不要硬编码在 settings.py

---

## 🚀 下一步优化建议

1. **拆分 views.py**：将 management/views.py (71.8KB) 拆分为多个小文件
2. **添加缓存层**：为 AI 响应添加 Redis 缓存，避免重复调用
3. **添加日志记录**：记录 AI 调用的耗时、成功率等指标
4. **添加限流机制**：防止 API 调用频率过高
