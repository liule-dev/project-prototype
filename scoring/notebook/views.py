# 导入所需的Django模块和其他组件
from django.shortcuts import render, get_object_or_404  # 渲染模板和获取对象或返回404错误
from django.http import JsonResponse  # 返回JSON响应
from django.views.decorators.csrf import csrf_exempt  # 免除CSRF验证装饰器
from django.conf import settings
from management.models import WrongTopic, User, Topic, ContactRecord, ReviewRecord, AnswerDetail  # 导入相关模型
from datetime import datetime  # 处理日期时间
import json  # 解析JSON数据
import dashscope

# 错题相关视图函数
@csrf_exempt  # 装饰器：免除CSRF验证，允许跨站请求
def add_wrong_topic(request):  # 定义添加错题的视图函数
    """添加错题到错题本"""  # 函数文档字符串
    if request.method == 'POST':  # 检查请求方法是否为POST
        try:  # 异常处理开始
            data = json.loads(request.body)  # 解析请求体中的JSON数据
            user_id = data.get('user_id')  # 获取用户ID
            topic_number = data.get('topic_number')  # 获取题目编号
            topic_knowledge = data.get('topic_knowledge')  # 获取题目知识点

            if not all([user_id, topic_number]):  # 检查必要参数是否齐全
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})  # 返回错误响应

            user = get_object_or_404(User, id=user_id)  # 获取用户对象，不存在则返回404
            # 验证题目是否存在
            get_object_or_404(Topic, topic_number=topic_number)  # 验证题目是否存在

            # 检查是否已经存在该错题，不存在则创建新记录
            wrong_topic, created = WrongTopic.objects.get_or_create(
                user=user,  # 关联用户
                topic_number=topic_number,  # 题目编号
                defaults={  # 默认值字典，仅在创建时使用
                    'error_times': 1,  # 错误次数初始化为1
                    'active': True,  # 激活状态设为True
                    'topic_knowledge': topic_knowledge  # 题目知识点
                }
            )

            if not created:  # 如果记录已存在
                # 如果已存在，则增加错误次数
                wrong_topic.error_times += 1  # 增加错误次数
                wrong_topic.active = True  # 设置为激活状态
                wrong_topic.save()  # 保存更改

            return JsonResponse({'status': 'success', 'message': '错题添加成功'})  # 返回成功响应
        except Exception as e:  # 捕获所有异常
            return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})  # 非POST请求返回错误


def get_wrong_topics(request, user_id):  # 定义获取用户错题列表的视图函数
    """获取用户的错题列表"""  # 函数文档字符串
    try:  # 异常处理开始
        wrong_topics = WrongTopic.objects.filter(user_id=user_id)  # 查询指定用户的错题记录
        data = []  # 初始化结果列表
        for wt in wrong_topics:  # 遍历查询结果
            # 查询该用户在这道题上的答案
            user_answer = ''
            try:
                answer_detail = AnswerDetail.objects.filter(
                    record__user_id=user_id,
                    question_number=wt.topic_number
                ).first()
                if answer_detail:
                    user_answer = answer_detail.answer or ''
            except:
                pass
            
            data.append({  # 将每个错题信息添加到结果列表中
                'id': wt.id,  # 错题ID
                'topic_number': wt.topic_number,  # 题目编号
                'error_times': wt.error_times,  # 错误次数（修正：保持原数据类型）
                'active': wt.active,  # 激活状态
                'topic_knowledge': wt.topic_knowledge,  # 题目知识点
                'user_answer': user_answer  # 用户答案
            })
        return JsonResponse({'status': 'success', 'data': data})  # 返回成功响应及数据
    except Exception as e:  # 捕获所有异常
        return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息


@csrf_exempt  # 装饰器：免除CSRF验证
def update_wrong_topic_status(request, wrong_topic_id):  # 定义更新错题状态的视图函数
    """更新错题状态（标记为已掌握）"""  # 函数文档字符串
    if request.method == 'POST':  # 检查请求方法是否为POST
        try:  # 异常处理开始
            wrong_topic = get_object_or_404(WrongTopic, id=wrong_topic_id)  # 获取错题对象
            wrong_topic.active = False  # 将错题标记为非激活状态（已掌握）
            wrong_topic.save()  # 保存更改
            return JsonResponse({'status': 'success', 'message': '错题状态更新成功'})  # 返回成功响应
        except Exception as e:  # 捕获所有异常
            return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})  # 非POST请求返回错误


# 练习记录相关视图函数
@csrf_exempt  # 装饰器：免除CSRF验证
def add_contact_record(request):  # 定义添加练习记录的视图函数
    """添加练习记录"""  # 函数文档字符串
    if request.method == 'POST':  # 检查请求方法是否为POST
        try:  # 异常处理开始
            data = json.loads(request.body)  # 解析请求体中的JSON数据
            user_id = data.get('user_id')  # 获取用户ID
            topic_number = data.get('topic_number')  # 获取题目编号
            topic_knowledge = data.get('topic_knowledge')  # 获取题目知识点

            if not all([user_id, topic_number]):  # 检查必要参数是否齐全
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})  # 返回错误响应

            user = get_object_or_404(User, id=user_id)  # 获取用户对象

            contact_record = ContactRecord.objects.create(  # 创建新的练习记录
                record_time=datetime.now(),  # 记录时间设为当前时间
                user=user,  # 关联用户
                topic_number=topic_number,  # 题目编号
                topic_knowledge=topic_knowledge  # 题目知识点
            )

            return JsonResponse({  # 返回成功响应
                'status': 'success',  # 状态标识
                'message': '练习记录添加成功',  # 成功消息
                'record_id': contact_record.id  # 新创建记录的ID
            })
        except Exception as e:  # 捕获所有异常
            return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})  # 非POST请求返回错误


def get_contact_records(request, user_id):  # 定义获取用户练习记录的视图函数
    """获取用户的练习记录"""  # 函数文档字符串
    try:  # 异常处理开始
        contact_records = ContactRecord.objects.filter(user_id=user_id).order_by('-record_time')  # 查询并按时间倒序排列
        data = []  # 初始化结果列表
        for cr in contact_records:  # 遍历查询结果
            data.append({  # 将每个练习记录信息添加到结果列表中
                'id': cr.id,  # 记录ID
                'record_time': cr.record_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化记录时间
                'topic_number': cr.topic_number,  # 题目编号
                'topic_knowledge': cr.topic_knowledge  # 题目知识点
            })
        return JsonResponse({'status': 'success', 'data': data})  # 返回成功响应及数据
    except Exception as e:  # 捕获所有异常
        return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息


# 复习记录相关视图函数
@csrf_exempt  # 装饰器：免除CSRF验证
def add_review_record(request):  # 定义添加复习记录的视图函数
    """添加复习记录"""  # 函数文档字符串
    if request.method == 'POST':  # 检查请求方法是否为POST
        try:  # 异常处理开始
            data = json.loads(request.body)  # 解析请求体中的JSON数据
            user_id = data.get('user_id')  # 获取用户ID
            topic_number = data.get('topic_number')  # 获取题目编号
            review_time = data.get('review_time')  # 获取可选的复习时间

            if not all([user_id, topic_number]):  # 检查必要参数是否齐全
                return JsonResponse({'status': 'error', 'message': '缺少必要参数'})  # 返回错误响应

            user = get_object_or_404(User, id=user_id)  # 获取用户对象

            # 处理复习时间，如果提供则转换为datetime对象
            if review_time:  # 如果提供了复习时间
                try:  # 尝试解析时间格式
                    review_time = datetime.strptime(review_time, '%Y-%m-%d %H:%M:%S')  # 转换为datetime对象
                except ValueError:  # 时间格式不正确时捕获异常
                    return JsonResponse(
                        {'status': 'error', 'message': '复习时间格式不正确，应为YYYY-MM-DD HH:MM:SS'})  # 返回错误响应
            else:  # 如果未提供复习时间
                review_time = datetime.now()  # 设为当前时间

            review_record = ReviewRecord.objects.create(  # 创建新的复习记录
                create_record_time=datetime.now(),  # 创建记录时间设为当前时间
                user=user,  # 关联用户
                topic_number=topic_number,  # 题目编号
                review_time=review_time  # 复习时间
            )

            return JsonResponse({  # 返回成功响应
                'status': 'success',  # 状态标识
                'message': '复习记录添加成功',  # 成功消息
                'record_id': review_record.id  # 新创建记录的ID
            })
        except Exception as e:  # 捕获所有异常
            return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})  # 非POST请求返回错误


def get_review_records(request, user_id):  # 定义获取用户复习记录的视图函数
    """获取用户的复习记录"""  # 函数文档字符串
    try:  # 异常处理开始
        review_records = ReviewRecord.objects.filter(user_id=user_id).order_by('-create_record_time')  # 查询并按创建时间倒序排列
        data = []  # 初始化结果列表
        for rr in review_records:  # 遍历查询结果
            data.append({  # 将每个复习记录信息添加到结果列表中
                'id': rr.id,  # 记录ID
                'create_record_time': rr.create_record_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化创建记录时间
                'topic_number': rr.topic_number,  # 题目编号
                'review_time': rr.review_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化复习时间
            })
        return JsonResponse({'status': 'success', 'data': data})  # 返回成功响应及数据
    except Exception as e:  # 捕获所有异常
        return JsonResponse({'status': 'error', 'message': str(e)})  # 返回异常信息


@csrf_exempt
def generate_study_plan_api(request):
    """生成学习计划API"""
    if request.method == 'POST':
        try:
            # 直接从settings获取并设置API密钥
            dashscope.api_key = settings.TONGYI_API_KEY.strip()

            # 调试信息
            print(f"使用API密钥: {bool(dashscope.api_key)}")

            if not dashscope.api_key:
                return JsonResponse({
                    'status': 'error',
                    'message': 'AI服务密钥未正确配置'
                })

            data = json.loads(request.body)
            subjects = data.get('subjects')
            time_frame = data.get('time_frame')
            goals = data.get('goals')

            # 调用AI服务生成学习计划
            from .ai_service import generate_study_plan
            plan = generate_study_plan(subjects, time_frame, goals)

            # 检查返回结果
            if plan and isinstance(plan, str) and len(plan) > 0:
                return JsonResponse({
                    'status': 'success',
                    'data': {'study_plan': plan}
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'AI服务未返回有效内容'
                })
        except Exception as e:
            print(f"生成学习计划时发生错误: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})


def analyze_wrong_topics_api(request, user_id):
    """错题本分析API"""
    if request.method == 'GET':
        try:
            # 获取用户错题数据
            wrong_topics = WrongTopic.objects.filter(user_id=user_id)
            topics_data = []
            for wt in wrong_topics:
                topics_data.append({
                    'topic_number': wt.topic_number,
                    'error_times': wt.error_times,
                    'topic_knowledge': wt.topic_knowledge,
                    'active': wt.active
                })

            analysis = analyze_wrong_topics(topics_data)
            return JsonResponse({
                'status': 'success',
                'data': {'analysis': analysis}
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': '请求方法不正确'})

def generate_study_plan(subjects, time_frame, goals):
    """
    生成学习计划的示例函数（需根据实际业务逻辑完善）
    :param subjects: 科目列表
    :param time_frame: 时间范围，如 'weekly' 或 'monthly'
    :param goals: 学习目标描述
    :return: 学习计划文本或结构化数据
    """
    # 示例返回内容，可根据需求扩展
    return f"为以下科目生成{time_frame}学习计划：{', '.join(subjects)}，目标：{goals}"

def analyze_wrong_topics(topics_data):
    """
    分析错题数据，生成分析报告
    :param topics_data: 错题数据列表，每个元素是包含topic_number, error_times等字段的字典
    :return: 分析结果，例如高频错误知识点、建议复习策略等
    """
    if not topics_data:
        return "暂无错题数据"

    # 统计错误次数最多的知识点
    knowledge_count = {}
    for topic in topics_data:
        knowledge = topic.get('topic_knowledge')
        if knowledge:
            knowledge_count[knowledge] = knowledge_count.get(knowledge, 0) + topic['error_times']

    # 找出最高频的知识点
    most_common_knowledge = max(knowledge_count, key=knowledge_count.get) if knowledge_count else "未知"

    return {
        "total_wrong_topics": len(topics_data),
        "most_error_knowledge": most_common_knowledge,
        "suggestion": "建议重点复习高频错题知识点"
    }


# 与AI的对话
@csrf_exempt
def chat_with_ai(request):
    """
    与AI进行对话
    """
    if request.method == 'POST':
        try:
            # 设置API密钥
            dashscope.api_key = settings.TONGYI_API_KEY.strip()

            if not dashscope.api_key:
                return JsonResponse({
                    'status': 'error',
                    'message': 'AI服务密钥未正确配置'
                })

            data = json.loads(request.body)
            user_message = data.get('message')
            user_id = data.get('user_id')

            if not user_message:
                return JsonResponse({
                    'status': 'error',
                    'message': '缺少必要参数: message'
                })

            # 可以在这里添加历史对话记录逻辑
            # 这里简单地将用户消息发送给AI

            # 构造发送给AI的消息
            messages = [{
                'role': 'user',
                'content': user_message
            }]

            # 调用通义千问API
            response = dashscope.Generation.call(
                model='qwen-turbo',  # 通义千问模型名称
                messages=messages,
                result_format='message'
            )

            if response.status_code == 200:
                ai_reply = response.output.choices[0]['message']['content']
                return JsonResponse({
                    'status': 'success',
                    'data': {
                        'reply': ai_reply
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'AI服务调用失败: {response.message}'
                })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': '请求方法不正确'
    })
