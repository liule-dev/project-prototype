# exam/viewshu.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import timedelta, datetime
import random
from rest_framework.decorators import api_view
from django.http import JsonResponse
import redis
# 在第 5 行附近添加
import uuid

# 创建 Redis 连接（适配你的 8.6.1 版本）
r = redis.Redis(
    host="127.0.0.1",  # 本地 Redis 地址
    port=6379,         # 默认端口
    db=0,              # 使用第 0 个数据库
    password="",       # 本地无密码，留空
    decode_responses=True  # 关键：自动将 bytes 转字符串，解决中文乱码
)


from management.models import (
    ExamPaper, ExamSetting, Topic, TopicExam, User, Notification,
    ExamNotification, ExamParticipation, ExamProgress, AutoScoringRule,
    ScoreReport, WrongTopic, Subject, AnswerDetail, ExamRecordEx, ExamRecord, QuestionDatabase
)
from teacher_topic.utils import OperationLogger


# 创建考试视图
@api_view(['post'])
@csrf_exempt
def create_exam(request):

    """
    创建考试：基于题库创建考试，设置考试名称、时长、开始/结束时间、及格线
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 验证必要字段
            required_fields = ['exam_name', 'subject_id', 'all_score', 'passing_score', 'duration', 'begin_time', 'end_time']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'缺少必要字段：{field}'})

            # 获取当前用户信息
            try:
                current_user = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在，请先登录'})

            # 处理日期时间字段，确保有时区信息
            begin_time_str = data['begin_time']
            end_time_str = data['end_time']

            # 解析日期时间字符串并添加时区信息
            begin_time = datetime.fromisoformat(begin_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            # 如果日期时间没有时区信息，添加默认时区
            if begin_time.tzinfo is None:
                begin_time = timezone.make_aware(begin_time)
            if end_time.tzinfo is None:
                end_time = timezone.make_aware(end_time)

            # 创建试卷（使用当前登录用户的ID作为创建人）
            exam_paper = ExamPaper.objects.create(
                name=data['exam_name'],
                subject_id=data['subject_id'],
                difficulty=data.get('difficulty', 'medium'),
                created_person_id=current_user.id,  # 使用当前登录用户的ID
                all_score=data.get('all_score', 100),
                status=False,  # 初始状态为未发布
                begin_time=begin_time,
                end_time=end_time
            )

            # 创建考试设置
            exam_setting = ExamSetting.objects.create(
                exam_paper=exam_paper,
                passing_score=data['passing_score'],
                duration=data['duration'],
                begin_time=begin_time,
                end_time=end_time,
                draw_rule=data.get('draw_rule', 'random'),
                difficulty_distribution=data.get('difficulty_distribution'),
                knowledge_distribution=data.get('knowledge_distribution')
            )

            # 根据抽题规则处理题目关联
            draw_rule = data.get('draw_rule', 'random')
            if draw_rule == 'random':
                # 随机抽题 - 传递 exam_paper 对象而不是规则字典
                topics = _random_draw_topics({}, exam_paper=exam_paper)

                # 将题目关联到试卷
                for topic in topics:
                    TopicExam.objects.create(
                        topic_number=topic.topic_number,
                        examPaper_number=exam_paper.number
                    )
            elif draw_rule == 'manual':
                # 手动选题 - 从请求数据中获取题目列表并创建
                manual_topics = data.get('manual_topics', [])
                if not manual_topics:
                    return JsonResponse({'status': 'error', 'message': '手动选题模式下必须提供题目数据'})
                
                # 批量创建题目并关联到试卷
                from django.db import transaction
                
                with transaction.atomic():
                    for topic_data in manual_topics:
                        # 创建题目
                        topic = Topic.objects.create(
                            topic_content=topic_data.get('topic_content', ''),
                            topic_answer=topic_data.get('topic_answer', ''),
                            A=topic_data.get('A', ''),
                            B=topic_data.get('B', ''),
                            C=topic_data.get('C', ''),
                            D=topic_data.get('D', ''),
                            E=topic_data.get('E', ''),
                            topic_difficulty=topic_data.get('topic_difficulty', 'medium'),
                            score=topic_data.get('score', 0),
                            topic_knowledge=topic_data.get('topic_knowledge', ''),
                            topic_type=topic_data.get('topic_type', ''),
                            topic_analysis=topic_data.get('topic_analysis', ''),
                            Q_data_id=1  # 默认题库ID，可根据实际情况调整
                        )
                        
                        # 关联到试卷
                        TopicExam.objects.create(
                            topic_number=topic.topic_number,
                            examPaper_number=exam_paper.number
                        )
                    
                    # 记录操作日志
                    OperationLogger.log_exam_creation_operation(
                        user=current_user,
                        content=f"创建考试（手动选题），考试 ID:{exam_paper.number}，考试名称:{exam_paper.name}，题目数量:{len(manual_topics)}"
                    )
            
            # 清除可能存在的旧缓存（如果之前有缓存的话）
            cache_key = f"exam_detail:{exam_paper.number}"
            r.delete(cache_key)
            
            return JsonResponse({
                'status': 'success',
                'exam_paper_id': exam_paper.number,
                'message': '考试创建成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'创建考试失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})

# AI 智能组卷视图
@csrf_exempt
def ai_generate_exam(request):
    """
    AI 智能组卷：使用通义千问生成题目并组卷
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 验证必要字段
            required_fields = ['exam_name', 'subject_id', 'created_person_id',
                               'all_score', 'begin_time', 'end_time']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'status': 'error', 'message': f'缺少必要字段：{field}'})

            # 验证用户是否存在，如果不存在则使用默认用户 ID 1
            try:
                user_id = data['created_person_id']
                User.objects.get(id=user_id)
            except User.DoesNotExist:
                try:
                    User.objects.get(id=request.user.id)
                except User.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': '默认用户不存在，请先创建用户'})

            # 获取科目信息
            try:
                subject = Subject.objects.get(id=data['subject_id'])
            except Subject.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '指定的科目不存在'})

            # 处理日期时间字段，确保有时区信息
            begin_time_str = data['begin_time']
            end_time_str = data['end_time']

            # 解析日期时间字符串并添加时区信息
            begin_time = datetime.fromisoformat(begin_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            # 如果日期时间没有时区信息，添加默认时区
            if begin_time.tzinfo is None:
                begin_time = timezone.make_aware(begin_time)
            if end_time.tzinfo is None:
                end_time = timezone.make_aware(end_time)

            # 创建试卷
            exam_paper = ExamPaper.objects.create(
                name=data['exam_name'],
                subject_id=data['subject_id'],
                difficulty=data.get('difficulty', 'medium'),
                created_person_id=request.user.id,
                all_score=data.get('all_score', 100),
                status=False,
                begin_time=begin_time,
                end_time=end_time
            )

            # 创建考试设置
            exam_setting = ExamSetting.objects.create(
                exam_paper=exam_paper,
                passing_score=data.get('passing_score', 60),
                duration=data.get('duration', 120),
                begin_time=begin_time,
                end_time=end_time,
                draw_rule='ai',  # 使用 AI 组卷规则
                difficulty_distribution=data.get('difficulty_distribution'),
                knowledge_distribution=data.get('knowledge_distribution')
            )

            # 使用简化版 AI 组卷（按知识点随机抽取）
            try:
                topics = _ai_draw_topics_by_knowledge({
                    'knowledge_points': data.get('knowledge_points', []),
                    'difficulty_distribution': exam_setting.difficulty_distribution or {}
                })

                # 将题目关联到试卷
                for topic in topics:
                    TopicExam.objects.create(
                        topic_number=topic.topic_number,
                        examPaper_number=exam_paper.number
                    )



            except Exception as ai_error:
                # AI 生成失败，回退到随机抽题
                topics = _random_draw_topics({
                    'difficulty_distribution': exam_setting.difficulty_distribution or {}
                })

                # 将题目关联到试卷
                for topic in topics:
                    TopicExam.objects.create(
                        topic_number=topic.topic_number,
                        examPaper_number=exam_paper.number
                    )
            
            # 清除可能存在的旧缓存
            cache_key = f"exam_detail:{exam_paper.number}"
            r.delete(cache_key)

            return JsonResponse({
                'status': 'success',
                'exam_paper_id': exam_paper.number,
                'message': 'AI 组卷成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'AI 组卷失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


def _random_draw_topics(rules, exam_paper=None):
    """
    随机抽题实现
    根据试卷的科目类型查询各题型数量，然后按题型抽取相应数量的题目
    """
    topics = []

    # 如果提供了试卷对象，则根据试卷科目查询各题型数量
    subject = exam_paper.subject  # 正确：获取 Subject 对象


    # 定义题型映射字典，将题型名称映射到 Subject 模型中的字段名
    type_field_mapping = {
        '单项选择题': 'choice_count',
        '多项选择题': 'multiple_choice_count',
        '判断题': 'judgment_count',
        '案例分析题': 'case_analysis_count',
        '计算分析题': 'calculation_analysis_count',
        '综合题': 'comprehensive_count'
    }

    # 遍历每种题型，查询该科目下配置的数量并抽取题目
    for qtype, field_name in type_field_mapping.items():
        # 获取该题型的数量
        count = getattr(subject, field_name, 0)

        if count > 0:  # 只有当数量大于 0 时才抽取题目
            # 先找到该科目对应的未提交题库

            related_databases = QuestionDatabase.objects.filter(
                subject=subject,  # 根据科目过滤题库
                status='未提交',
                question_type=qtype  # 添加状态过滤条件，具体字段名根据实际模型调整
            )

            # 从这些题库中查找指定题型的题目并随机抽取
            # 从这些特定题型的题库中获取所有题目
            all_topics_from_filtered_db = Topic.objects.filter(
                Q_data__in=related_databases # 从该科目的特定题型题库中查找
            )

            # 随机抽取指定数量的题目，然后按 topic_number 排序
            type_topics = list(all_topics_from_filtered_db.order_by('?')[:count])
            # 按题号排序，确保题目顺序一致
            type_topics.sort(key=lambda x: x.topic_number)

            topics.extend(type_topics)
    print(topics)
    return topics



def _ai_draw_topics_by_knowledge(rules):
    """
    简化版 AI 抽题实现：按知识点随机抽取
    """
    topics = []
    knowledge_points = rules.get('knowledge_points', [])
    difficulty_dist = rules.get('difficulty_distribution', {})

    # 如果有指定知识点，优先从这些知识点中抽取
    if knowledge_points:
        for difficulty, count in difficulty_dist.items():
            # 将难度映射到数据库中的值
            difficulty_mapping = {
                '简单': 'easy',
                '中等': 'medium',
                '困难': 'hard',
                'easy': 'easy',
                'medium': 'medium',
                'hard': 'hard'
            }
            db_difficulty = difficulty_mapping.get(difficulty, difficulty)

            # 从指定知识点中抽取题目
            knowledge_topics = list(Topic.objects.filter(
                topic_knowledge__in=knowledge_points,
                topic_difficulty=db_difficulty
            ).order_by('?')[:count])

            # 如果指定知识点中题目不足，从所有题目中补充
            if len(knowledge_topics) < count:
                additional_count = count - len(knowledge_topics)
                additional_topics = list(Topic.objects.filter(
                    topic_difficulty=db_difficulty
                ).exclude(
                    topic_number__in=[t.topic_number for t in knowledge_topics]
                ).order_by('?')[:additional_count])
                knowledge_topics.extend(additional_topics)

            topics.extend(knowledge_topics)
    else:
        # 没有指定知识点时，使用随机抽题
        topics = _random_draw_topics(rules)

    return topics
@api_view(['post'])
@csrf_exempt
def publish_exam(request):
    """
    发布考试并通知所有学生
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 更新试卷状态为已发布
            exam_paper = ExamPaper.objects.get(number=data['exam_paper_id'])
            exam_paper.status = True
            exam_paper.save()
            
            # 清除缓存，因为状态改变了
            cache_key = f"exam_detail:{exam_paper.number}"
            r.delete(cache_key)

            # 获取考试创建者（教师）
            exam_creator = exam_paper.created_person

            # 向所有学生发布考试
            users = User.objects.filter(role='student')
            notification_content = f"新考试发布：{exam_paper.name}，请按时参加"

            # 为每个学生创建通知和考试参与记录
            for user in users:
                notification = Notification.objects.create(
                    receiver_id=user.id,
                    content=notification_content,
                    notification_time=timezone.now(),
                    is_read=False
                )

                ExamNotification.objects.create(
                    exam_paper=exam_paper,
                    notification=notification,
                    is_exam_notification=True
                )

                # 创建考试参与记录
                ExamParticipation.objects.create(
                    exam_paper=exam_paper,
                    user=user,
                    status='not_started',
                    all_score=exam_paper.all_score  # 使用试卷的总分
                )
            OperationLogger.log_exam_creation_operation(
                user=exam_creator,
                content=f"发布考试，考试 ID:{exam_paper.number}，考试名称:{exam_paper.name}，发布时间:{timezone.now().isoformat()}"
            )
            return JsonResponse({
                'status': 'success',
                'message': f'考试已发布，通知了{len(users)}名学生'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'发布考试失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


# 开始答题视图
@csrf_exempt
def start_exam(request):
    """
    开始答题视图
    处理学生开始考试的请求，初始化考试状态并返回试卷题目
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 获取或创建考试参与记录
            participation, created = ExamParticipation.objects.get_or_create(
                exam_paper_id=data['exam_paper_id'],
                user_id=data['user_id'],
                defaults={
                    'status': 'not_started',
                    'all_score': ExamPaper.objects.get(number=data['exam_paper_id']).all_score
                }
            )

            # 更新状态和开始时间
            participation.status = 'in_progress'
            participation.start_time = timezone.now()
            participation.save()

            # 获取用户信息用于记录日志
            current_user = User.objects.get(id=data['user_id'])
            exam_paper = ExamPaper.objects.get(number=data['exam_paper_id'])

            # 获取试卷题目
            topic_exams = TopicExam.objects.filter(examPaper_number=data['exam_paper_id'])
            topic_ids = [te.topic_number for te in topic_exams]
            topics = Topic.objects.filter(topic_number__in=topic_ids)

            # 记录操作日志
            OperationLogger.log_answer_submission_operation(
                user=current_user,
                content=f"开始考试，考试 ID:{exam_paper.number}，考试名称:{exam_paper.name}"
            )

            return JsonResponse({
                'status': 'success',
                'participation_id': participation.id,
                'topics': [{
                    'topic_number': topic.topic_number,
                    'content': topic.topic_content,
                    'options': {
                        'A': topic.A,
                        'B': topic.B,
                        'C': topic.C,
                        'D': topic.D,
                        'E': topic.E
                    },
                    'difficulty': topic.topic_difficulty,
                    'topic_type': topic.topic_type  # 添加题目类型字段
                } for topic in topics],
                'end_time': (participation.start_time + timedelta(
                    minutes=participation.exam_paper.settings.duration)).isoformat()
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'开始考试失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


# 保存答题进度视图

# ... existing code ...

# 交卷视图
@csrf_exempt
def submit_exam(request):
    """
    交卷视图
    处理学生提交考试的请求，更新考试状态并计算成绩
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 获取考试参与记录
            participation = ExamParticipation.objects.get(id=data['participation_id'])

            # 更新状态和结束时间
            participation.status = 'completed'
            participation.end_time = timezone.now()

            # 直接从 AnswerDetail 表获取答题记录（save_progress 时已创建）
            answer_details = AnswerDetail.objects.filter(record_id=participation.id)

            # 计算客观题得分
            total_score = 0
            passing_score = participation.exam_paper.settings.passing_score

            for answer_detail in answer_details:
                # 只处理客观题（主观题需要教师批改）
                if answer_detail.true_false is not None:  # 客观题
                    topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                    if topic:
                        correct_answer = topic.topic_answer
                        user_answer = answer_detail.answer
                        
                        # 判断是否正确
                        is_correct = str(user_answer).strip().upper() == str(correct_answer).strip().upper()
                        answer_detail.true_false = is_correct
                        
                        # 如果正确，累加分数
                        if is_correct:
                            total_score += topic.score or 0
                        
                        answer_detail.save()

            # 更新用户得分
            participation.obtained_score = total_score
            participation.save()
            
            print(f"\n=== 开始创建 ExamRecord ===")
            print(f"Participation ID: {participation.id}")
            print(f"用户：{participation.user.username}")
            print(f"考试：{participation.exam_paper.name}")
            print(f"开始时间：{participation.start_time}")
            print(f"结束时间：{participation.end_time}")
            
            # 创建 ExamRecord 记录（用于教师批改和个人报告）
            from management.models import ExamRecord
            from decimal import Decimal
            
            try:
                # 计算考试时长（分钟）
                begin_time_decimal = Decimal('0.00')
                if participation.start_time:
                    time_diff = participation.end_time - participation.start_time
                    begin_time_decimal = Decimal(str(time_diff.total_seconds() / 60)).quantize(Decimal('0.01'))
                    print(f"考试时长：{begin_time_decimal} 分钟")
                else:
                    print("警告：participation.start_time 为 None，使用 0.00")
                
                exam_record = ExamRecord.objects.create(
                    user=participation.user,
                    begin_time=begin_time_decimal,
                    end_time=participation.end_time,
                    status=False,  # 初始状态为未批改，等待教师批改
                    end_score=total_score,  # 临时分数，批改后会更新
                    exam_paper=participation.exam_paper
                )
                
                print(f"✓ ExamRecord 创建成功：ID={exam_record.number}")
                
                # 更新 AnswerDetail 的 record_id 为新的 exam_record.number
                answer_details.update(record_id=exam_record.number)
                
                print(f"✓ 更新 {answer_details.count()} 条 AnswerDetail 记录的 record_id")
                print(f"已创建 ExamRecord: ID={exam_record.number}, 用户={participation.user.username}, 考试={participation.exam_paper.name}")
                
                # 将客观题错题添加到错题本（包括：单项选择题、多项选择题、判断题）
                # 筛选出答错的客观题：type1为客观题类型 且 true_false=False（答错）
                incorrect_objective = answer_details.filter(
                    type1__in=['单项选择题', '多项选择题', '判断题'],
                    true_false=False
                )
                print(f"找到 {incorrect_objective.count()} 道答错的客观题")
                for answer_detail in incorrect_objective:
                    topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                    if topic:
                        wrong_topic, created = WrongTopic.objects.get_or_create(
                            user=participation.user,
                            topic_number=topic.topic_number,
                            defaults={
                                'error_times': 1,
                                'active': True,
                                'topic_knowledge': topic.topic_knowledge or ''
                            }
                        )
                        if not created:
                            wrong_topic.error_times += 1
                            wrong_topic.active = True
                            wrong_topic.save()
                        print(f"✓ 添加客观题错题: 题目编号={topic.topic_number}, 题型={topic.topic_type}")
                
            except Exception as e:
                print(f"✗ 创建 ExamRecord 失败：{str(e)}")
                import traceback
                traceback.print_exc()
                # 即使创建失败也不影响交卷，继续执行

            # 获取用户信息用于记录日志
            current_user = participation.user
            exam_paper = participation.exam_paper

            # 记录操作日志
            OperationLogger.log_answer_submission_operation(
                user=current_user,
                content=f"交卷，考试 ID:{exam_paper.number}，考试名称:{exam_paper.name}，得分:{total_score}"
            )

            # 清除缓存
            cache_key = f"exam_participation:{participation.id}"
            r.delete(cache_key)

            return JsonResponse({
                'status': 'success',
                'message': '交卷成功',
                'obtained_score': total_score,
                'passing_score': passing_score,
                'passed': total_score >= passing_score
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'交卷失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


# 生成成绩报告视图
# ... existing code ...


# 在 save_progress 函数中添加 answer_detail 记录
@csrf_exempt
def save_progress(request):
    """
    保存答题进度 - 直接写入 AnswerDetail 表
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            participation = ExamParticipation.objects.get(id=data['participation_id'])
            topic = Topic.objects.get(topic_number=data['topic_id'])
            
            # 直接更新或创建 AnswerDetail 记录
            AnswerDetail.objects.update_or_create(
                record_id=data['participation_id'],  # 使用 participation_id 作为临时 record_id
                question_number=data['topic_id'],
                defaults={
                    'answer': data['answer'],
                    'score': 0,  # 初始分数为 0，批改时更新
                    'true_false': False,  # 初始为 False，交卷时更新
                    'type1': data.get('type1', topic.topic_type or '')
                }
            )

            current_user = participation.user
            exam_paper = participation.exam_paper

            # 记录操作日志
            OperationLogger.log_answer_submission_operation(
                user=current_user,
                content=f"提交答案，考试 ID:{exam_paper.number}，考试名称:{exam_paper.name}，题目 ID:{topic.topic_number}"
            )

            return JsonResponse({
                'status': 'success',
                'message': '进度保存成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'保存进度失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


# 交卷视图

#
# 在 submit_exam 函数中删除自动评分功能



# 生成成绩报告视图
@api_view(['post'])
@csrf_exempt
def generate_score_report(request):
    """
    生成成绩报告
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            participation = ExamParticipation.objects.get(id=data['participation_id'])

            # 从 AnswerDetail 表获取答题记录
            answer_details = AnswerDetail.objects.filter(record_id=participation.id)
            
            # 统计信息
            statistics = {
                'total_questions': answer_details.count(),
                'correct_answers': answer_details.filter(true_false=True).count(),
                'incorrect_answers': answer_details.filter(true_false=False).count(),
                'unanswered_questions': 0,  # AnswerDetail 中不区分是否未答
                'all_score': participation.all_score,
                'obtained_score': participation.obtained_score,
                'passing_score': participation.exam_paper.settings.passing_score,
                'passed': participation.obtained_score >= participation.exam_paper.settings.passing_score
            }

            # 创建成绩报告
            score_report = ScoreReport.objects.create(
                participation=participation,
                statistics=statistics
            )

            # 更新错题本
            incorrect_answers = answer_details.filter(true_false=False)

            for answer_detail in incorrect_answers:
                topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                if topic:
                    wrong_topic, created = WrongTopic.objects.get_or_create(
                        user=participation.user,
                        topic_number=topic.topic_number,
                        defaults={
                            'error_times': 1,
                            'active': True,
                            'topic_knowledge': topic.topic_knowledge
                        }
                    )
                    if not created:
                        wrong_topic.error_times += 1
                        wrong_topic.save()

            return JsonResponse({
                'status': 'success',
                'report_id': score_report.id,
                'statistics': statistics,
                'message': '成绩报告生成成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'生成成绩报告失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 POST 请求'})


# 获取考试详情视图 (已优化：增加 Redis 缓存)
def get_exam_detail(request, exam_paper_id):
    """
    获取考试详情
    优先从 Redis 缓存读取，若缓存不存在则查询数据库并写入缓存
    """
    cache_key = f"exam_detail:{exam_paper_id}"
    
    # 尝试从 Redis 获取缓存数据
    cached_data = r.get(cache_key)
    if cached_data:
        # 如果缓存存在，直接返回
        return JsonResponse(json.loads(cached_data))
    
    # 缓存不存在，查询数据库
    try:
        exam_paper = ExamPaper.objects.get(number=exam_paper_id)
        setting = ExamSetting.objects.get(exam_paper=exam_paper)

        response_data = {
            'status': 'success',
            'exam': {
                'id': exam_paper.number,
                'name': exam_paper.name,
                'subject': exam_paper.subject.subject_name,
                'difficulty': exam_paper.difficulty,
                'all_score': exam_paper.all_score,
                'status': exam_paper.status,
                'begin_time': exam_paper.begin_time.isoformat(),
                'end_time': exam_paper.end_time.isoformat(),
                'settings': {
                    'passing_score': setting.passing_score,
                    'duration': setting.duration,
                    'draw_rule': setting.draw_rule,
                    'difficulty_distribution': setting.difficulty_distribution,
                    'knowledge_distribution': setting.knowledge_distribution
                }
            }
        }
        
        # 将结果存入 Redis，设置过期时间为 1 小时 (3600 秒)
        r.setex(cache_key, 3600, json.dumps(response_data, ensure_ascii=False))
        
        return JsonResponse(response_data)
    except ExamPaper.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '考试不存在'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取考试详情失败：{str(e)}'})


# 获取用户考试参与情况视图
def get_user_exam_participation(request, user_id, exam_paper_id):
    """
    获取用户考试参与情况
    """
    try:
        participation = ExamParticipation.objects.get(
            user_id=user_id,
            exam_paper_id=exam_paper_id
        )

        return JsonResponse({
            'status': 'success',
            'participation': {
                'id': participation.id,
                'status': participation.status,
                'start_time': participation.start_time.isoformat() if participation.start_time else None,
                'end_time': participation.end_time.isoformat() if participation.end_time else None,
                'total_score': participation.all_score,
                'obtained_score': participation.obtained_score
            }
        })
    except ExamParticipation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '考试参与记录不存在'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取参与情况失败：{str(e)}'})


# 获取用户可参加的考试列表
def get_user_available_exams(request, user_id):
    """
    获取用户可参加的考试列表
    """
    try:
        now = timezone.now()
        # 获取学生用户信息
        user = User.objects.get(id=user_id)

        # 获取所有已发布且在有效时间内的考试（面向所有学生）
        available_exams = ExamPaper.objects.filter(
            status=True,  # 已发布
            begin_time__lte=now,  # 已开始
            end_time__gte=now  # 未结束
        ).select_related('subject', 'settings')

        # 获取用户已参加的考试（排除未开始状态）
        user_participations = ExamParticipation.objects.filter(
            user_id=user_id
        ).exclude(status='not_started').values_list('exam_paper_id', flat=True)

        exams_data = []
        for exam in available_exams:
            # 如果用户尚未参加该考试，则添加到列表中
            if exam.number not in user_participations:
                exams_data.append({
                    'id': exam.number,
                    'name': exam.name,
                    'subject': exam.subject.subject_name,
                    'begin_time': exam.begin_time.isoformat(),
                    'end_time': exam.end_time.isoformat(),
                    'duration': exam.settings.duration if hasattr(exam, 'settings') else 0,
                    'passing_score': exam.settings.passing_score if hasattr(exam, 'settings') else 0,
                    'all_score': exam.all_score
                })

        return JsonResponse({
            'status': 'success',
            'exams': exams_data,
            'message': '获取考试列表成功'
        })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取考试列表失败：{str(e)}'})


# 获取所有考试列表
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

# 用装饰器指定认证方式为 Token 认证
@api_view(['GET'])
def get_published_exams(request):
    """
    获取所有考试列表（包括已发布和未发布的）
    教师和管理员只能看到自己创建的考试
    学生可以看到所有考试
    """
    try:
        # 获取当前用户
        current_user = request.user
        
        if not current_user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': '用户未登录'})
        
        # 调试信息：打印当前用户ID和角色
        print(f"[DEBUG] 当前用户ID: {current_user.id}, 用户名: {current_user.username}, 角色: {current_user.role}")

        # 根据用户角色返回不同的考试列表
        if current_user.role == 'admin':
            # 管理员可以看到所有考试
            print(f"[DEBUG] 管理员模式，查询所有考试")
            all_exams = ExamPaper.objects.all()
        elif current_user.role == 'teacher':
            # 教师只能看到自己创建的考试
            print(f"[DEBUG] 教师模式，只查询用户 {current_user.id} 创建的考试")
            all_exams = ExamPaper.objects.filter(
                created_person_id=current_user.id
            )
        else:
            # 学生可以看到所有已发布的考试
            print(f"[DEBUG] 学生模式，角色={current_user.role}，只查询已发布考试")
            all_exams = ExamPaper.objects.filter(
                status=True
            )
        
        print(f"[DEBUG] 查询到 {all_exams.count()} 条考试记录")

        exams_data = []
        for exam in all_exams:
            exams_data.append({
                'id': exam.number,
                'name': exam.name,
                'subject': exam.subject.subject_name,
                'subject_id': exam.subject.id,
                'begin_time': exam.begin_time.isoformat(),
                'end_time': exam.end_time.isoformat(),
                'all_score': exam.all_score,
                'status': exam.status,
                'created_person_id': exam.created_person_id,
                'settings': {
                    'passing_score': exam.settings.passing_score if hasattr(exam, 'settings') else 0,
                    'duration': exam.settings.duration if hasattr(exam, 'settings') else 0,
                    'draw_rule': exam.settings.draw_rule if hasattr(exam, 'settings') else 'random'
                }
            })
        
        return JsonResponse({
            'status': 'success',
            'exams': exams_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取考试列表失败：{str(e)}'})


# 获取科目列表
def get_subjects(request):
    """
    获取所有科目列表
    """
    try:
        subjects = Subject.objects.all()
        subjects_data = [
            {
                'id': subject.id,
                'subject_name': subject.subject_name
            }
            for subject in subjects
        ]

        return JsonResponse({
            'status': 'success',
            'subjects': subjects_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取科目列表失败：{str(e)}'})


# 获取科目详情（包含题型配置）
def get_subject_detail(request, subject_id):
    """
    获取科目详情，包括各题型的数量和分数配置
    """
    try:
        subject = Subject.objects.get(id=subject_id)
        
        subject_data = {
            'id': subject.id,
            'subject_name': subject.subject_name,
            'choice_count': subject.choice_count,
            'choice_score': subject.choice_score,
            'multiple_choice_count': subject.multiple_choice_count,
            'multiple_choice_score': subject.multiple_choice_score,
            'case_analysis_count': subject.case_analysis_count,
            'case_analysis_score': subject.case_analysis_score,
            'calculation_analysis_count': subject.calculation_analysis_count,
            'calculation_analysis_score': subject.calculation_analysis_score,
            'comprehensive_count': subject.comprehensive_count,
            'comprehensive_score': subject.comprehensive_score
        }
        
        return JsonResponse({
            'status': 'success',
            'data': subject_data
        })
    except Subject.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '科目不存在'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取科目详情失败：{str(e)}'})


# 获取试卷题目
def get_exam_topics(request, exam_paper_id):
    """
    获取试卷题目
    按照题型顺序排列：单项选择题 -> 多项选择题 -> 判断题 -> 案例分析题 -> 计算分析题 -> 综合题
    """
    try:
        # 获取试卷题目
        topic_exams = TopicExam.objects.filter(examPaper_number=exam_paper_id)
        topic_ids = [te.topic_number for te in topic_exams]
        topics = Topic.objects.filter(topic_number__in=topic_ids)
        
        # 定义题型顺序
        type_order = {
            '单项选择题': 1,
            '多项选择题': 2,
            '判断题': 3,
            '案例分析题': 4,
            '计算分析题': 5,
            '综合题': 6
        }
        
        # 按题型顺序和题号排序
        sorted_topics = sorted(topics, key=lambda t: (type_order.get(t.topic_type, 99), t.topic_number))

        topics_data = [{
            'topic_number': topic.topic_number,
            'topic_content': topic.topic_content,
            'A': topic.A,
            'B': topic.B,
            'C': topic.C,
            'D': topic.D,
            'E': topic.E,
            'topic_difficulty': topic.topic_difficulty,
            'topic_type': topic.topic_type,  # 添加题目类型字段
            'display_order': idx + 1  # 添加显示顺序（从1开始连续编号）
        } for idx, topic in enumerate(sorted_topics)]

        return JsonResponse({
            'status': 'success',
            'topics': topics_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取试卷题目失败：{str(e)}'})


# 更新考试视图
@csrf_exempt
def update_exam(request, exam_paper_id):
    """
    更新考试信息
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)

            # 更新试卷
            try:
                exam_paper = ExamPaper.objects.get(number=exam_paper_id)
            except ExamPaper.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '考试不存在'})

            # 更新字段
            exam_paper.name = data.get('exam_name', exam_paper.name)
            exam_paper.subject_id = data.get('subject_id', exam_paper.subject_id)
            exam_paper.all_score = data.get('all_score', exam_paper.all_score)

            # 处理日期时间字段
            if 'begin_time' in data:
                begin_time_str = data['begin_time']
                begin_time = datetime.fromisoformat(begin_time_str.replace('Z', '+00:00'))
                if begin_time.tzinfo is None:
                    begin_time = timezone.make_aware(begin_time)
                exam_paper.begin_time = begin_time

            if 'end_time' in data:
                end_time_str = data['end_time']
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                if end_time.tzinfo is None:
                    end_time = timezone.make_aware(end_time)
                exam_paper.end_time = end_time

            # 如果提供了 created_person_id 且用户存在，则更新
            if 'created_person_id' in data:
                try:
                    user_id = data['created_person_id']
                    User.objects.get(id=user_id)
                    exam_paper.created_person_id = user_id
                except User.DoesNotExist:
                    # 如果用户不存在，使用默认用户 ID 1
                    try:
                        User.objects.get(id=request.user.id)
                        exam_paper.created_person_id = request.user.id
                    except User.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': '默认用户不存在'})

            exam_paper.save()

            # 更新考试设置
            try:
                setting = ExamSetting.objects.get(exam_paper=exam_paper)
                setting.passing_score = data.get('passing_score', setting.passing_score)
                setting.duration = data.get('duration', setting.duration)

                # 处理日期时间字段
                if 'begin_time' in data:
                    begin_time_str = data['begin_time']
                    begin_time = datetime.fromisoformat(begin_time_str.replace('Z', '+00:00'))
                    if begin_time.tzinfo is None:
                        begin_time = timezone.make_aware(begin_time)
                    setting.begin_time = begin_time

                if 'end_time' in data:
                    end_time_str = data['end_time']
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    if end_time.tzinfo is None:
                        end_time = timezone.make_aware(end_time)
                    setting.end_time = end_time

                setting.draw_rule = data.get('draw_rule', setting.draw_rule)

                # 更新难度分布和知识点分布
                if 'difficulty_distribution' in data:
                    setting.difficulty_distribution = data['difficulty_distribution']
                if 'knowledge_distribution' in data:
                    setting.knowledge_distribution = data['knowledge_distribution']

                setting.save()
            except ExamSetting.DoesNotExist:
                # 如果没有考试设置，创建一个新的
                begin_time = exam_paper.begin_time
                end_time = exam_paper.end_time
                if 'begin_time' in data:
                    begin_time_str = data['begin_time']
                    begin_time = datetime.fromisoformat(begin_time_str.replace('Z', '+00:00'))
                    if begin_time.tzinfo is None:
                        begin_time = timezone.make_aware(begin_time)
                if 'end_time' in data:
                    end_time_str = data['end_time']
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    if end_time.tzinfo is None:
                        end_time = timezone.make_aware(end_time)

                ExamSetting.objects.create(
                    exam_paper=exam_paper,
                    passing_score=data.get('passing_score', 60),
                    duration=data.get('duration', 120),
                    begin_time=begin_time,
                    end_time=end_time,
                    draw_rule=data.get('draw_rule', 'random')
                )
            
            # 更新后清除缓存
            cache_key = f"exam_detail:{exam_paper_id}"
            r.delete(cache_key)

            return JsonResponse({
                'status': 'success',
                'message': '考试更新成功'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'更新考试失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 PUT 请求'})


# 删除考试视图
@csrf_exempt
def delete_exam(request, exam_paper_id):
    """
    删除考试
    """
    if request.method == 'DELETE':
        try:
            exam_paper = ExamPaper.objects.get(number=exam_paper_id)

            # 获取考试创建者（用于记录日志）
            exam_creator = exam_paper.created_person

            # 删除相关数据
            ExamSetting.objects.filter(exam_paper=exam_paper).delete()
            TopicExam.objects.filter(examPaper_number=exam_paper_id).delete()
            
            # 先获取参与该考试的所有用户记录
            exam_participations = ExamParticipation.objects.filter(exam_paper=exam_paper)
            participation_ids = [p.id for p in exam_participations]
            
            # 删除相关的 AnswerDetail 记录
            AnswerDetail.objects.filter(record_id__in=participation_ids).delete()
            
            # 删除相关的 ExamRecord 记录
            ExamRecord.objects.filter(number__in=participation_ids).delete()
            
            # 删除考试参与记录
            exam_participations.delete()
            
            # 删除试卷
            exam_paper.delete()
            
            # 删除对应的缓存
            cache_key = f"exam_detail:{exam_paper_id}"
            r.delete(cache_key)

            # 记录操作日志
            OperationLogger.log_exam_creation_operation(
                user=exam_creator,
                content=f"删除考试，考试 ID:{exam_paper_id}，考试名称:{exam_paper.name}"
            )

            return JsonResponse({
                'status': 'success',
                'message': '考试删除成功'
            })
        except ExamPaper.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '考试不存在'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'删除考试失败：{str(e)}'})

    return JsonResponse({'status': 'error', 'message': '仅支持 DELETE 请求'})


# 统一考试详情视图
@csrf_exempt
def exam_detail_view(request, exam_paper_id):
    if request.method == 'GET':
        # 获取考试详情
        return get_exam_detail(request, exam_paper_id)
    elif request.method == 'PUT':
        # 更新考试
        return update_exam(request, exam_paper_id)
    elif request.method == 'DELETE':
        # 删除考试
        return delete_exam(request, exam_paper_id)
    else:
        return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})


# 在 exam/viewshu.py 中添加

def get_user_info(request, ):
    """
    获取用户详细信息，包括班级、专业、年级等
    """
    try:
        user = User.objects.get(id=request.user.id)

        # 获取班级信息
        class_info = None
        if user.class1:
            class_obj = user.class1
            class_info = {
                'class_id': class_obj.id,
                'class_name': class_obj.class1.class_name if class_obj.class1 else '',
                'grade': class_obj.grade1.grade10 if class_obj.grade1 else '',
                'specialty': class_obj.specialty1.specialty10 if class_obj.specialty1 else ''
            }

        return JsonResponse({
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email,
                'phone': user.phone,
                'class_info': class_info
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取用户信息失败：{str(e)}'})


def get_user_scores(request, user_id):
    """
    获取指定用户的考试成绩（只能查看自己的成绩，教师可以查看班级学生成绩）
    只返回已经参加过的考试（有start_time的记录）
    """
    try:
        # 验证请求用户 ID 与路径参数是否一致（防止越权访问）
        request_user_id = user_id

        # 获取当前用户
        try:
            current_user = User.objects.get(id=request_user_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})

        # 权限检查：用户只能查看自己的成绩，教师可以查看班级学生成绩
        if current_user.role == 'student' and str(current_user.id) != str(user_id):
            return JsonResponse({'status': 'error', 'message': '无权限查看他人成绩'})

        # 如果是教师，检查要查询的用户是否在自己的班级中
        if current_user.role in ['teacher', 'admin'] and str(current_user.id) != str(user_id):
            try:
                target_user = User.objects.get(id=user_id)
                # 检查目标用户是否在当前教师的班级中
                if target_user.class1 != current_user.class1 and current_user.role != 'admin':
                    return JsonResponse({'status': 'error', 'message': '无权限查看该学生成绩'})
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '目标用户不存在'})

        # 获取用户的考试参与记录（只返回已经参加过的，即有start_time的记录）
        participations = ExamParticipation.objects.filter(
            user_id=user_id
        ).exclude(
            start_time__isnull=True  # 排除未开始参加的考试
        ).select_related('exam_paper', 'exam_paper__subject')

        scores_data = []
        for participation in participations:
            # 安全处理时间格式化
            created_at = None
            if participation.end_time:
                try:
                    created_at = participation.end_time.isoformat()
                except:
                    created_at = None
            elif participation.start_time:
                try:
                    created_at = participation.start_time.isoformat()
                except:
                    created_at = None

            # 计算实际得分：从 AnswerDetail 表累加所有题目的分数
            actual_score = 0
            try:
                # 尝试从 ExamRecord 获取答题记录
                from management.models import ExamRecord
                exam_record = ExamRecord.objects.filter(
                    user_id=user_id,
                    exam_paper_id=participation.exam_paper.number
                ).first()
                
                if exam_record:
                    # 使用 ExamRecord.number 查询 AnswerDetail
                    answer_details = AnswerDetail.objects.filter(record_id=exam_record.number)
                    actual_score = sum(answer_detail.score or 0 for answer_detail in answer_details)
                else:
                    # 使用 participation.id 查询 AnswerDetail
                    answer_details = AnswerDetail.objects.filter(record_id=participation.id)
                    actual_score = sum(answer_detail.score or 0 for answer_detail in answer_details)
            except Exception as e:
                print(f"计算分数失败: {str(e)}")
                # 如果计算失败，使用 participation.obtained_score
                actual_score = participation.obtained_score or 0

            # 添加所有参加过的考试，不仅仅是已评分的
            scores_data.append({
                'id': participation.id,
                'exam_paper_number': participation.exam_paper.number,
                'exam_name': participation.exam_paper.name,
                'subject': participation.exam_paper.subject.subject_name,
                'all_score': participation.all_score,
                'obtained_score': actual_score,
                'status': participation.status,
                'created_at': created_at
            })

        return JsonResponse({
            'status': 'success',
            'scores': scores_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取成绩失败：{str(e)}'})


def get_class_scores(request, user_id):
    """
    获取当前用户所在班级的学生成绩
    教师可以看到自己班级学生的成绩，学生只能看到自己的成绩
    """
    try:
        # 获取当前用户
        try:
            current_user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'})

        # 如果是学生，只能查看自己的成绩
        if current_user.role == 'student':
            participations = ExamParticipation.objects.filter(
                user_id=user_id
            ).select_related('exam_paper', 'exam_paper__subject', 'user')
        else:
            # 如果是教师，可以查看自己班级学生的成绩
            # 获取教师所在班级的学生
            class_students = User.objects.filter(class1=current_user.class1)
            student_ids = [student.id for student in class_students]

            participations = ExamParticipation.objects.filter(
                user_id__in=student_ids
            ).select_related('exam_paper', 'exam_paper__subject', 'user')

        scores_data = []
        for participation in participations:
            # 安全处理时间格式化
            created_at = None
            if participation.end_time:
                try:
                    created_at = participation.end_time.isoformat()
                except:
                    created_at = None
            elif participation.start_time:
                try:
                    created_at = participation.start_time.isoformat()
                except:
                    created_at = None

            # 添加所有参加过的考试，不仅仅是已评分的
            scores_data.append({
                'id': participation.id,
                'exam_paper_number': participation.exam_paper.number,
                'exam_name': participation.exam_paper.name,
                'user_name': participation.user.username,
                'subject': participation.exam_paper.subject.subject_name,
                'all_score': participation.all_score,
                'obtained_score': participation.obtained_score,
                'status': participation.status,
                'created_at': created_at
            })

        return JsonResponse({
            'status': 'success',
            'scores': scores_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'获取成绩失败：{str(e)}'})


# 获取用户考试答题详情
def get_user_exam_answers(request, user_id, exam_paper_id):
    """
    获取用户在某次考试中的答题详情
    """
    try:
        from management.models import ExamRecord
        
        # 获取用户的考试参与记录
        participation = ExamParticipation.objects.get(
            user_id=user_id,
            exam_paper_id=exam_paper_id
        )
        
        print(f"\n=== 查询答题详情 ===")
        print(f"Participation ID: {participation.id}")
        print(f"用户：{participation.user.username}")
        print(f"考试：{participation.exam_paper.name}")

        # 尝试查找对应的 ExamRecord
        exam_record = ExamRecord.objects.filter(
            user_id=user_id,
            exam_paper_id=exam_paper_id
        ).first()
        
        # 如果考试已交卷，record_id 是 ExamRecord.number；否则是 participation.id
        if exam_record:
            print(f"找到 ExamRecord，number: {exam_record.number}")
            answer_details = AnswerDetail.objects.filter(
                record_id=exam_record.number
            )
        else:
            print(f"未找到 ExamRecord，使用 participation.id: {participation.id}")
            answer_details = AnswerDetail.objects.filter(
                record_id=participation.id
            )
        
        print(f"查询到 {answer_details.count()} 条答题记录")

        # 构造答题详情数据
        answers_data = []
        for answer_detail in answer_details:
            answers_data.append({
                'topic_number': answer_detail.question_number,
                'user_answer': answer_detail.answer,
                'is_correct': answer_detail.true_false,
                'score': answer_detail.score
            })

        return JsonResponse({
            'status': 'success',
            'answers': answers_data
        })
    except ExamParticipation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '考试参与记录不存在'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f'获取答题详情失败：{str(e)}'})
