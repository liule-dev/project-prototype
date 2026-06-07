from  django.utils import timezone

from django.contrib.auth.models import AbstractUser

# Create your models here.

from django.db import models

from Notification.notification_constants import NotificationType


# 专业模型 - 用于存储不同专业信息
class Specialty(models.Model):
    # 专业ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 专业名称，最大长度20个字符
    specialty10 = models.CharField(max_length=20)
    
    class Meta:
        # 指定数据库表名
        db_table ='specialty'

# 班级名称模型 - 存储班级名称信息
class ClassName(models.Model):
    # 班级ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 班级名称，最大长度20个字符
    class_name = models.CharField(max_length=20)

    class Meta:
        # 指定数据库表名
        db_table = 'class_name'


# 科目模型 - 存储考试科目信息
class Subject(models.Model):
    # 科目ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 科目名称，最大长度20个字符
    subject_name = models.CharField(max_length=20)
    # 选择题数量
    choice_count = models.IntegerField(default=0)
    # 选择题分数
    choice_score = models.FloatField(default=0)
    # 多选题数量
    multiple_choice_count = models.IntegerField(default=0)
    # 多选题分数
    multiple_choice_score = models.FloatField(default=0)
    # 判断题数量
    judgment_count = models.IntegerField(default=0)
    # 判断题分数
    judgment_score = models.FloatField(default=0)
    # 计算分析题数量
    calculation_analysis_count = models.IntegerField(default=0)
    # 计算分析题分数
    calculation_analysis_score = models.FloatField(default=0)
    # 案例分析题数量
    case_analysis_count = models.IntegerField(default=0)
    # 案例分析题分数
    case_analysis_score = models.FloatField(default=0)
    # 综合题数量
    comprehensive_count = models.IntegerField(default=0)
    # 综合题分数
    comprehensive_score = models.FloatField(default=0)
    
    class Meta:
        # 指定数据库表名
        db_table ='subject'

    def __str__(self):
        return self.subject_name

# 年级模型 - 存储年级信息
class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    grade10 = models.CharField(max_length=20)

    class Meta:
        db_table = 'grade'

    def __str__(self):
        return self.grade10


# 班级模型
class Class(models.Model):
    id = models.AutoField(primary_key=True)
    specialty = models.CharField(max_length=20,null=True,blank=True)
    class1 = models.ForeignKey(ClassName, on_delete=models.CASCADE, related_name='classname',default=None,null=True)
    grade1 = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade',default=None,null=True)
    specialty1 = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='specialty',default=None,null=True)

    class Meta:
        db_table = 'class'


# 用户模型
class User(AbstractUser):
    role = models.CharField(max_length=20, default='student')
    phone = models.CharField(max_length=11,)
    class1 = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='user1',default=None,null=True)
    
    def is_teacher(self):
        return self.role == 'teacher'
        
    def is_student(self):
        return self.role == 'student'
        
    class Meta:
        db_table = 'user'


# 题库模型 - 存储题库基本信息
class QuestionDatabase(models.Model):
    # 题库编号，主键，自动递增
    Question_number = models.AutoField(primary_key=True)
    # 创建用户，外键关联User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    # 题目数量
    question_total = models.IntegerField(default=0)
    # 题库名称，最大长度20个字符
    name = models.CharField(max_length=20)
    # 题目类型，最大长度20个字符
    question_type = models.CharField(max_length=20)
    # 年级，外键关联Grade模型
    grade1 = models.ForeignKey(Grade, on_delete=models.CASCADE,related_name='grade1')
    # 题库状态，最大长度20个字符
    status = models.CharField(max_length=20)
    # 是否公开，布尔类型
    if_public = models.BooleanField()
    # 创建时间，自动设置为记录创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新时间，每次保存时自动更新
    updated_at = models.DateTimeField(auto_now=True)
    # 科目，外键关联Subject模型
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,related_name='subject1')

    def save(self, *args, **kwargs):
        # 保存时自动更新题目数量
        if self.pk:
            # 更新现有记录
            self.question_total = Topic.objects.filter(Q_data=self).count()
        else:
            # 新建记录
            self.question_total = 0
        super().save(*args, **kwargs)

    class Meta:
        # 指定数据库表名
        db_table = 'question_database'


# 题目题库中间表模型 - 多对多关系表，连接题目和题库
class QuestionTopic(models.Model):
    # 题库编号
    question_number = models.IntegerField()
    # 题目编号
    topic_number = models.IntegerField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'questiondatebase_topic'

# 题目模型 - 存储具体题目信息
class Topic(models.Model):
    # 题目编号，主键，自动递增
    topic_number = models.AutoField(primary_key=True)
    # 题目内容，文本类型
    topic_content = models.TextField()
    # 题目答案，文本类型
    topic_answer = models.TextField()
    A = models.CharField(max_length=200, blank=True, null=True)
    B = models.CharField(max_length=200, blank=True, null=True)
    C = models.CharField(max_length=200, blank=True, null=True)
    D = models.CharField(max_length=200, blank=True, null=True)
    E = models.CharField(max_length=200, blank=True, null=True)
    # 题目难度，最大长度20个字符
    topic_difficulty = models.CharField(max_length=20)
    # 题目满分，默认为0
    score = models.FloatField(default=0)
    # 创建时间，自动设置为记录创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新时间，每次保存时自动更新
    updated_at = models.DateTimeField(auto_now=True)
    # 题目知识点，文本类型
    topic_knowledge = models.TextField(blank=True, null=True)
    # 题目解析，文本类型
    topic_type = models.CharField(max_length=110, blank=True, null=True, verbose_name="题目类型")
    topic_analysis = models.TextField(blank=True, null=True)
    # 所属题库，外键关联QuestionDatabase模型
    Q_data =models.ForeignKey(QuestionDatabase, on_delete=models.CASCADE,related_name='Q_data')

    class Meta:
        # 指定数据库表名
        db_table = 'topic'


# 试题与试卷中间表模型 - 多对多关系表，连接题目和试卷
class TopicExam(models.Model):
    # 题目编号
    topic_number = models.IntegerField()
    # 试卷编号
    examPaper_number = models.IntegerField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'topic_exam'


# 试卷模型 - 存储试卷信息
class ExamPaper(models.Model):
    # 试卷编号，主键，自动递增
    number = models.AutoField(primary_key=True)
    # 试卷名称，最大长度20个字符
    name = models.CharField(max_length=20)
    # 科目，外键关联Subject模型
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,related_name='subject_exam')
    # 试卷难度，最大长度20个字符
    difficulty = models.CharField(max_length=20)
    # 试卷创建人，外键关联User模型
    created_person = models.ForeignKey(User, on_delete=models.CASCADE,related_name='created_person')
    # 创建时间，自动设置为记录创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新时间，每次保存时自动更新
    updated_at = models.DateTimeField(auto_now=True)
    # 试卷总分
    all_score = models.IntegerField()
    # 试卷状态，布尔类型
    status = models.BooleanField()
    # 考试开始时间
    begin_time = models.DateTimeField()
    # 考试结束时间
    end_time = models.DateTimeField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'exam_paper'

# 考试记录与试卷中间表模型 - 多对多关系表，连接考试记录和试卷
class ExamRecordEx(models.Model):
    # 考试记录ID
    record_id = models.IntegerField()
    # 试卷编号
    exam_paper_number = models.IntegerField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'exam_record'

# 考试记录模型 - 存储学生考试记录信息
class ExamRecord(models.Model):
    # 考试记录编号，主键，自动递增
    number = models.AutoField(primary_key=True)
    # 考生，外键关联User模型
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_record')
    # 考试开始时间（分钟）
    begin_time = models.DecimalField(max_digits=5, decimal_places=2)
    # 考试结束时间
    end_time = models.DateTimeField()
    # 考试状态，布尔类型（是否已完成）
    status = models.BooleanField()
    # 考试得分
    end_score = models.FloatField()
    # 所属试卷，外键关联ExamPaper模型，允许为空
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='exam_records', null=True, blank=True)
    
    class Meta:
        # 指定数据库表名
        db_table = 'exam_record_ex'





# 答题详情模型 - 存储每道题的答题详情
class AnswerDetail(models.Model):
    # 答题详情ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 考试记录ID
    record_id = models.IntegerField()
    # 题目编号
    question_number = models.IntegerField()
    # 学生答案，文本类型
    answer = models.TextField()
    # 该题得分
    score = models.FloatField()
    # 题目类型，True表示客观题，False表示主观题
    true_false = models.BooleanField()
    type1=models.CharField(max_length=110, verbose_name="题目类型")
    
    class Meta:
        # 指定数据库表名
        db_table = 'answer_detail'

# 错题本模型 - 存储学生的错题信息
class WrongTopic(models.Model):
    # 错题ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 学生，外键关联User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_wrong')
    # 题目编号
    topic_number = models.IntegerField()
    # 错误次数
    error_times = models.DecimalField(max_digits=5, decimal_places=2)
    # 是否激活（是否仍需练习）
    active = models.BooleanField()
    # 题目知识点，文本类型
    topic_knowledge = models.TextField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'wrong_topic'


# 练习记录表模型 - 存储学生练习记录
class ContactRecord(models.Model):
    # 练习记录ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 练习时间
    record_time = models.DateTimeField()
    # 学生，外键关联User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_contact')
    # 题目编号
    topic_number = models.IntegerField()
    # 题目知识点，文本类型
    topic_knowledge = models.TextField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'contact_record'

# 复习记录模型 - 存储学生复习记录
class ReviewRecord(models.Model):
    # 复习记录ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 创建记录时间
    create_record_time = models.DateTimeField()
    # 学生，外键关联User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_review_record')
    # 题目编号，文本类型
    topic_number = models.TextField()
    # 复习时间
    review_time = models.DateTimeField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'review'

# 操作记录表模型 - 存储用户操作记录
class OperationRecord(models.Model):
    # 操作记录ID，主键，自动递增
    id = models.AutoField(primary_key=True)
    # 用户，外键关联User模型
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user_operation_record')
    # 操作类型，最大长度20个字符
    operation_type = models.CharField(max_length=20)
    # 操作内容，文本类型
    content = models.TextField()
    # 操作时间
    operation_time = models.DateTimeField()
    
    class Meta:
        # 指定数据库表名
        db_table = 'operation_record'


# 通知表模型
class Notification(models.Model):
    # 通知类型选项
    TYPE_CHOICES = [
        (NotificationType.EXAM_NOTIFICATION, NotificationType.EXAM_NOTIFICATION),
        (NotificationType.GRADE_NOTIFICATION, NotificationType.GRADE_NOTIFICATION),
        (NotificationType.QUESTION_REVIEW_NOTIFICATION, NotificationType.QUESTION_REVIEW_NOTIFICATION),
        (NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION, NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION),
        (NotificationType.WRONG_BOOK_UPDATE_NOTIFICATION, NotificationType.WRONG_BOOK_UPDATE_NOTIFICATION),
        (NotificationType.LEARNING_PLAN_RECOMMENDATION_NOTIFICATION,
         NotificationType.LEARNING_PLAN_RECOMMENDATION_NOTIFICATION),
    ]

    id = models.AutoField(primary_key=True)
    # 修复外键引用，使用直接引用而非字符串引用
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='sent_notifications')
    title = models.CharField(max_length=100)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES,
                            default=NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION)
    notification_time = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'

    def __str__(self):
        return f"{self.title} - {self.type}"



class ExamSetting(models.Model):
    id = models.AutoField(primary_key=True)
    exam_paper = models.OneToOneField(ExamPaper, on_delete=models.CASCADE, related_name='settings')
    passing_score = models.FloatField(verbose_name="及格线")
    duration = models.IntegerField(verbose_name="考试时长(分钟)")
    begin_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    draw_rule = models.CharField(max_length=20, choices=[('manual', '手动选题'), ('random', '随机抽题')])
    difficulty_distribution = models.JSONField(blank=True, null=True, verbose_name="难度分布")
    knowledge_distribution = models.JSONField(blank=True, null=True, verbose_name="知识点分布")

    class Meta:
        db_table = 'exam_setting'



class ExamParticipation(models.Model):
    id = models.AutoField(primary_key=True)
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_participations')
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="实际开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="实际结束时间")
    status = models.CharField(max_length=20, default='not_started', choices=[
        ('not_started', '未开始'),
        ('in_progress', '进行中'),
        ('submitted', '已交卷'),
        ('graded', '已评分')
    ])
    all_score = models.FloatField(blank=True, null=True, verbose_name="总分")
    obtained_score = models.FloatField(blank=True, null=True, verbose_name="获得分数")

    class Meta:
        db_table = 'exam_participation'
        unique_together = ('exam_paper', 'user')


class AutoScoringRule(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='scoring_rule')
    score = models.FloatField(verbose_name="题目分数")
    answer = models.TextField(verbose_name="标准答案")
    grading_method = models.CharField(max_length=20, choices=[
        ('automatic', '自动评分'),
        ('manual', '人工评分')
    ], default='automatic')

    class Meta:
        db_table = 'auto_scoring_rule'

class ExamNotification(models.Model):
    id = models.AutoField(primary_key=True)
    exam_paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, related_name='notifications')
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='exam_detail')
    is_exam_notification = models.BooleanField(default=True)

    class Meta:
        db_table = 'exam_notification'


class ExamProgress(models.Model):
    id = models.AutoField(primary_key=True)
    participation = models.ForeignKey(ExamParticipation, on_delete=models.CASCADE, related_name='progress')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='exam_progress')
    answer = models.TextField(blank=True, null=True, verbose_name="考生答案")
    is_answered = models.BooleanField(default=False)
    is_marked = models.BooleanField(default=False, verbose_name="是否标记")
    saved_at = models.DateTimeField(auto_now=True, verbose_name="保存时间")

    class Meta:
        db_table = 'exam_progress'
        unique_together = ('participation', 'topic')


class ScoreReport(models.Model):
    id = models.AutoField(primary_key=True)
    participation = models.OneToOneField(ExamParticipation, on_delete=models.CASCADE, related_name='score_report')
    generated_at = models.DateTimeField(auto_now_add=True)
    statistics = models.JSONField(verbose_name="成绩统计信息")

    class Meta:
        db_table = 'score_report'

class TopicTag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称")
    description = models.TextField(blank=True, verbose_name="标签描述")

    class Meta:
        db_table = 'topic_tag'

class TopicTagRelation(models.Model):
    id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(TopicTag, on_delete=models.CASCADE, related_name='topics')

    class Meta:
        db_table = 'topic_tag_relation'
        unique_together = ('topic', 'tag')

