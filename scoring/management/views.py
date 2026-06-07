import sys
# 从Django中导入相关模块
# PermissionDenied异常用于权限拒绝情况
# authenticate函数用于验证用户凭据
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate
# 从Django REST framework中导入Token认证相关模块
# Token模型用于创建和管理用户认证令牌
# api_view装饰器用于将普通函数转换为API视图
# permission_classes装饰器用于设置视图的权限类
# AllowAny权限类允许任何用户访问
# IsAuthenticated权限类只允许已认证用户访问
# HTTP_400_BAD_REQUEST状态码表示客户端请求错误
# Response类用于返回API响应
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
# 从Django REST framework中导入视图集和状态码相关模块
# viewsets模块提供ModelViewSet等通用视图集
# status模块包含HTTP状态码常量
# action装饰器用于创建自定义视图操作
from rest_framework import viewsets, status
from rest_framework.decorators import action
# 从当前应用中导入模型、序列化器和辅助类
# Class模型表示班级信息
# User模型表示用户信息
# ExamPaper模型表示考试试卷
# ExamRecord模型表示考试记录
# AnswerDetail模型表示答题详情
# Topic模型表示题目
# TopicExam模型表示试卷中的题目关联
# ClassName模型表示班级名称
# ClassSerializer等序列化器用于数据序列化
# QwenAIService类提供AI服务功能
# OperationLogger类用于记录操作日志
from .models import Class, User, ExamPaper, ExamRecord, ExamParticipation, AnswerDetail, Topic, TopicExam, ClassName, WrongTopic
from .serializers import ClassSerializer, StudentSerializer, ExamSerializer, PaperSerializer, ReportSerializer, ClassNameSerializer
from .ai_service import QwenAIService
from .utils import OperationLogger

# 确保Python使用UTF-8编码
# 检查当前Python默认编码是否为UTF-8，如果不是则设置为UTF-8
# 这样可以确保程序正确处理中文字符和其他Unicode字符
if sys.getdefaultencoding() != 'utf-8':
    # 设置Python默认编码为UTF-8
    # 这对于处理包含中文等Unicode字符的数据非常重要
    sys.setdefaultencoding('utf-8')


# 用户登录认证视图 - 用于用户登录并获取认证Token
# 使用@api_view装饰器将普通函数转换为REST API视图
# 指定该视图只接受POST请求
@api_view(['POST'])
# 使用@permission_classes装饰器设置视图权限
# AllowAny权限类允许任何用户（包括未认证用户）访问该视图
# 这样未登录用户也可以调用登录接口
@permission_classes([AllowAny])
def obtain_auth_token(request):
    """
    用户登录认证接口
    
    接收用户名和密码，验证成功后返回认证Token和用户信息。
    这是一个公共接口，不需要认证即可访问。
    
    请求方法: POST
    请求参数:
        - username (str): 用户名
        - password (str): 密码
    
    返回:
        - 成功: {
            'token': '认证令牌',
            'user': {
                'id': 用户ID,
                'username': 用户名,
                'role': 用户角色
            }
        }
        - 失败: {
            'detail': '错误信息'
        }
    
    状态码:
        - 200: 认证成功
        - 400: 用户名或密码错误/为空
    """
    # 从请求数据中获取用户名和密码
    # request.data是Django REST framework提供的字典，包含客户端发送的所有数据
    # 使用get方法安全地获取数据，如果键不存在则返回None
    username = request.data.get('username')
    password = request.data.get('password')
    
    # 检查用户名和密码是否存在
    # 确保用户名和密码都不为空，避免处理空值
    if username and password:
        # 验证用户凭据
        # 使用Django内置的authenticate函数验证用户名和密码
        # 如果凭据有效，返回User对象；否则返回None
        user = authenticate(username=username, password=password)
        if user:
            # 删除旧的token（如果存在）
            # 使用Token.objects.filter查找指定用户的Token对象
            # delete()方法删除找到的所有Token对象
            # 这样确保每个用户只有一个有效的Token
            Token.objects.filter(user=user).delete()
            # 创建新的token
            # 使用Token.objects.create为用户创建新的认证Token
            # Token.key是自动生成的唯一字符串，用于用户认证
            token = Token.objects.create(user=user)
            
            # 返回token和用户信息
            # 构造包含Token和用户基本信息的响应数据
            # user.id是用户唯一标识符
            # user.username是用户名
            # user.role是用户角色（如学生、教师）
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            })
        else:
            # 用户凭据无效
            # 当authenticate返回None时，说明用户名或密码错误
            # 返回400状态码和错误信息
            return Response({'detail': '用户名或密码错误'}, status=400)
    else:
        # 用户名或密码为空
        # 当用户名或密码任一为空时，返回400状态码和错误信息
        return Response({'detail': '用户名和密码不能为空'}, status=400)


# 获取当前用户信息的API视图
# 使用@api_view装饰器将函数转换为API视图，只接受GET请求
@api_view(['GET'])
# 设置权限类为IsAuthenticated，只允许已认证用户访问
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    获取当前登录用户的信息接口
    
    返回当前已认证用户的基本信息。
    需要有效的认证令牌才能访问。
    
    请求方法: GET
    
    返回:
        {
            'id': 用户ID,
            'username': 用户名,
            'role': 用户角色,
            'first_name': 名字,
            'last_name': 姓氏,
            'email': 邮箱
        }
    
    状态码:
        - 200: 获取成功
    """
    # 获取当前请求的用户对象
    # request.user是Django认证系统提供的属性，包含当前认证用户的信息
    # 如果用户未认证，则为AnonymousUser对象
    user = request.user
    # 返回用户基本信息的响应
    # 包括用户ID、用户名、角色、名字、姓氏和邮箱
    return Response({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    })


# 班级视图集 - 提供班级信息的增删改查操作
# 继承自Django REST framework的ModelViewSet
# ModelViewSet提供了完整的CRUD操作（创建、读取、更新、删除）
class ClassViewSet(viewsets.ModelViewSet):
    """
    班级信息管理视图集
    
    提供对班级信息的完整CRUD操作：
    - 列出所有班级
    - 获取单个班级详情
    - 创建新班级
    - 更新班级信息
    - 删除班级
    
    使用ClassSerializer进行序列化。
    """
    # 查询集：获取所有班级记录
    # queryset是Django ORM查询集，定义视图操作的数据源
    # Class.objects.all()返回Class模型的所有记录
    queryset = Class.objects.all()
    # 序列化器类
    # serializer_class指定用于序列化和反序列化数据的类
    # ClassSerializer定义了班级数据的序列化规则
    serializer_class = ClassSerializer


# 学生视图集 - 提供学生信息的增删改查操作
# 继承自Django REST framework的ModelViewSet
class StudentViewSet(viewsets.ModelViewSet):
    """
    学生信息管理视图集
    
    提供对学生信息的完整CRUD操作：
    - 列出学生（仅教师可访问）
    - 获取单个学生详情
    - 创建学生账户
    - 更新学生信息
    - 删除学生账户
    
    使用StudentSerializer进行序列化。
    """
    # 查询集：获取所有学生记录
    # User.objects.all()返回User模型的所有记录
    queryset = User.objects.all()
    # 序列化器类
    # StudentSerializer定义了学生数据的序列化规则
    serializer_class = StudentSerializer

    # 重写get_queryset方法以实现自定义查询逻辑
    def get_queryset(self):
        """
        获取查询集，根据用户角色过滤数据
        
        只有教师可以访问学生信息，并且可以根据班级ID进行筛选。
        
        查询参数:
            - class_id (int, 可选): 班级ID，用于筛选特定班级的学生
            
        返回:
            QuerySet: 过滤后的学生记录查询集
            
        异常:
            PermissionDenied: 如果当前用户不是教师
        """
        # 检查用户是否为教师
        # request.user.is_authenticated检查用户是否已认证
        # request.user.is_teacher()检查用户是否为教师角色
        if not self.request.user.is_authenticated or not self.request.user.is_teacher():
            # 如果用户未认证或不是教师，抛出权限拒绝异常
            # PermissionDenied是Django提供的异常类，会返回403状态码
            raise PermissionDenied("只有教师可以访问学生信息")
            
        # 获取所有用户记录
        # User.objects.all()获取User模型的所有记录
        queryset = User.objects.all()
        # 获取查询参数中的班级ID
        # request.query_params是包含URL查询参数的字典
        # get方法安全地获取class_id参数，如果不存在则返回None
        class_id = self.request.query_params.get('class_id', None)
        # 如果提供了班级ID，则过滤该班级的学生
        # filter方法用于筛选满足条件的记录
        if class_id is not None:
            # 筛选class1字段等于class_id的用户记录
            queryset = queryset.filter(class1=class_id)
        # 返回过滤后的查询集
        return queryset


# 考试视图集 - 提供考试信息的增删改查操作
# 继承自Django REST framework的ModelViewSet
class ExamViewSet(viewsets.ModelViewSet):
    """
    考试信息管理视图集
    
    提供对考试信息的完整CRUD操作：
    - 列出所有考试
    - 获取单个考试详情
    - 创建新考试
    - 更新考试信息
    - 删除考试
    
    使用ExamSerializer进行序列化。
    """
    # 查询集：获取所有考试记录
    # ExamPaper.objects.all()返回ExamPaper模型的所有记录
    queryset = ExamPaper.objects.all()
    # 序列化器类
    # ExamSerializer定义了考试数据的序列化规则
    serializer_class = ExamSerializer
    
    # 重写get_queryset方法以实现自定义查询逻辑
    def get_queryset(self):
        """
        获取查询集，控制不同用户角色对考试信息的访问权限
        
        所有已认证用户（包括学生和教师）都可以看到所有考试信息。
        
        返回:
            QuerySet: 所有考试记录查询集
            
        异常:
            PermissionDenied: 如果用户未登录
        """
        # 检查用户是否已登录
        # request.user.is_authenticated检查用户是否已通过认证
        if not self.request.user.is_authenticated:
            # 如果用户未认证，抛出权限拒绝异常
            raise PermissionDenied("用户未登录")
            
        # 所有用户（包括学生和教师）都可以看到所有考试
        # 返回ExamPaper模型的所有记录查询集
        return ExamPaper.objects.all()


# 试卷视图集 - 提供试卷记录的增删改查操作
# 继承自Django REST framework的ModelViewSet
class PaperViewSet(viewsets.ModelViewSet):
    """
    试卷记录管理视图集
    
    提供对试卷记录的完整CRUD操作：
    - 列出试卷记录
    - 获取单个试卷记录详情
    - 创建试卷记录
    - 更新试卷记录
    - 删除试卷记录
    
    还提供自动批改客观题和手动批改主观题的自定义操作。
    
    使用PaperSerializer进行序列化。
    """
    # 查询集：获取所有试卷记录
    # ExamRecord.objects.all() 返回 ExamRecord 模型的所有记录
    queryset = ExamRecord.objects.all()
    # 序列化器类
    # PaperSerializer定义了试卷记录数据的序列化规则
    serializer_class = PaperSerializer

    # 重写get_queryset方法以实现自定义查询逻辑
    def get_queryset(self):
        """
        获取查询集，根据用户角色过滤试卷记录
        
        学生只能查看自己的试卷记录，教师可以查看所有学生的试卷记录。
        支持按考试ID、学生ID和班级ID进行筛选。
        
        查询参数:
            - exam_id (int, 可选): 考试ID，用于筛选特定考试的试卷记录
            - student_id (int, 可选): 学生ID，用于筛选特定学生的试卷记录（仅教师可用）
            - class_id (int, 可选): 班级ID，用于筛选特定班级的试卷记录
            
        返回:
            QuerySet: 过滤后的试卷记录查询集
            
        异常:
            PermissionDenied: 如果用户未登录或学生试图查看他人记录
        """
        # 检查用户是否已登录
        # request.user.is_authenticated检查用户是否已通过认证
        if not self.request.user.is_authenticated:
            # 如果用户未认证，抛出权限拒绝异常
            raise PermissionDenied("用户未登录")
            
        # 获取所有试卷记录
        # ExamRecord.objects.all() 获取 ExamRecord 模型的所有记录
        queryset = ExamRecord.objects.all()
        # 获取查询参数中的考试ID和学生ID
        # 从URL查询参数中提取筛选条件
        exam_id = self.request.query_params.get('exam_id', None)
        student_id = self.request.query_params.get('student_id', None)
        class_id = self.request.query_params.get('class_id', None)
        
        # 如果是学生用户
        # request.user.is_student()检查当前用户是否为学生角色
        if self.request.user.is_student():
            # 学生只能查看自己的记录
            # filter方法筛选user字段等于当前用户的记录
            queryset = queryset.filter(user=self.request.user)
            # 如果尝试查看其他学生的记录，则拒绝访问
            # 检查请求中是否包含student_id参数且不等于当前用户ID
            if student_id and int(student_id) != self.request.user.id:
                # 抛出权限拒绝异常，防止学生查看他人试卷记录
                raise PermissionDenied("学生只能查看自己的试卷记录")
        else:
            # 如果是教师用户，可以查看指定学生的记录
            # 检查请求中是否包含student_id参数
            if student_id is not None:
                # 筛选指定学生的试卷记录
                queryset = queryset.filter(user_id=student_id)
                
        # 如果提供了考试ID，则过滤该考试的试卷记录
        # 检查请求中是否包含exam_id参数
        if exam_id is not None:
            # 筛选 exam_paper__number 字段等于 exam_id 的记录
            queryset = queryset.filter(exam_paper__number=exam_id)
            
        # 如果提供了班级ID，则过滤该班级的试卷记录
        # 检查请求中是否包含class_id参数
        if class_id is not None:
            # 筛选 user__class1 字段等于 class_id 的记录
            queryset = queryset.filter(user__class1=class_id)
        # 返回过滤后的查询集
        return queryset

    # 重写list方法以返回详细的成绩信息
    def list(self, request, *args, **kwargs):
        """
        重写list方法以返回详细的试卷信息，包括客观题和主观题得分
        """
        # 过滤查询集
        queryset = self.filter_queryset(self.get_queryset())
        
        # 定义客观题类型常量（兼容多种命名格式）
        OBJECTIVE_TYPES = ['单项选择题', '多项选择题', '判断题', '单选题', '多选题']
        
        # 为每个试卷添加详细的成绩信息
        papers_data = []
        for paper in queryset:
            # 获取答题详情
            answer_details = AnswerDetail.objects.filter(record_id=paper.number)
            
            # 计算客观题和主观题得分
            objective_score = 0
            subjective_score = 0
            total_objective_score = 0
            total_subjective_score = 0
            objective_count = 0  # 客观题数量
            subjective_count = 0  # 主观题数量
            
            # 收集主观题详情和客观题详情
            subjective_details = []
            objective_details = []
            
            # 遍历答题详情
            for answer_detail in answer_details:
                # 获取题目信息
                topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                max_score = topic.score if topic else (answer_detail.score or 0)

                # 根据 type1 判断题型
                if answer_detail.type1 in OBJECTIVE_TYPES:  # 客观题
                    total_objective_score += max_score  # 题目满分
                    objective_score += answer_detail.score or 0  # 实际得分
                    objective_count += 1  # 统计客观题数量
                    # 收集客观题详情
                    objective_details.append({
                        'question_number': answer_detail.question_number,
                        'score': answer_detail.score or 0,
                        'max_score': max_score,
                        'is_correct': answer_detail.true_false
                    })
                else:  # 主观题
                    total_subjective_score += max_score  # 题目满分
                    subjective_score += answer_detail.score or 0  # 实际得分
                    subjective_count += 1  # 统计主观题数量
                    # 收集主观题详情
                    subjective_details.append({
                        'question_number': answer_detail.question_number,
                        'score': answer_detail.score or 0,
                        'max_score': max_score
                    })
            
            # 将试卷数据添加到列表中
            papers_data.append({
                'id': paper.number,
                'number': paper.number,
                'user': {
                    'id': paper.user.id if paper.user else None,
                    'username': paper.user.username if paper.user else None,
                    'first_name': paper.user.first_name if paper.user else None,
                    'last_name': paper.user.last_name if paper.user else None,
                    'class1': {
                        'name': paper.user.class1.name if paper.user and paper.user.class1 else None
                    } if paper.user else None
                },
                'end_time': paper.end_time,
                'status': paper.status,
                'end_score': paper.end_score,
                'exam_paper': paper.exam_paper.number if paper.exam_paper else None,
                'objective_score': objective_score,
                'subjective_score': subjective_score,
                'total_objective_score': total_objective_score,
                'total_subjective_score': total_subjective_score,
                'objective_count': objective_count,  # 添加客观题数量
                'subjective_count': subjective_count,  # 添加主观题数量
                'objective_details': objective_details,  # 添加客观题详情
                'subjective_details': subjective_details  # 添加主观题详情
            })
        
        # 直接返回数据而不是序列化后的数据
        return Response(papers_data)

    # 定义自定义操作：自动批改客观题
    # 使用@action装饰器创建自定义视图操作
    # detail=True表示该操作作用于单个对象
    # methods=['post']表示该操作只接受POST请求
    @action(detail=True, methods=['post'])
    def auto_grade_objective(self, request, pk=None):
        """
        自动批改客观题操作
        
        对指定试卷记录中的客观题进行自动批改，比较学生答案与标准答案。
        只有教师可以执行此操作。
        
        路径: POST /papers/{id}/auto_grade_objective/
        
        参数:
            pk (int): 试卷记录ID
            
        返回:
            Response: 包含批改结果的响应
            
        异常:
            PermissionDenied: 如果用户不是教师
        """
        # 检查用户权限
        # 确保用户已认证且为教师角色
        # TODO: 测试完成后请取消下面这行的注释以恢复权限验证
        # if not request.user.is_authenticated or not request.user.is_teacher():
        #     raise PermissionDenied("只有教师可以进行自动批改")
            
        # 获取试卷对象
        # get_object()是ModelViewSet提供的方法，用于获取当前操作的对象
        try:
            paper = self.get_object()
        except Exception as e:
            # 如果获取试卷对象失败，返回错误响应
            return Response({
                'error': f'获取试卷失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷对应的所有答题详情
        # AnswerDetail.objects.filter 根据 record_id 筛选答题详情
        # record_id 关联的是 ExamRecord 的 number 字段
        print(f"试卷对象：{paper}, 类型：{type(paper)}")
        print(f"试卷 number: {paper.number}")
        answer_details = AnswerDetail.objects.filter(record_id=paper.number)
        print(f"试卷 Number: {paper.number}, 答题详情数量：{answer_details.count()}")
        # 检查是否有答题详情
        # exists() 方法检查查询集是否包含任何记录
        if not answer_details.exists():
            # 如果没有答题详情，返回错误响应
            return Response({
                'error': '试卷中没有答题记录'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷对应的所有题目
        # 获取试卷对象关联的考试信息
        exam_paper = paper.exam_paper
        if not exam_paper:
            # 如果试卷信息不完整，返回错误响应
            return Response({
                'error': '试卷信息不完整'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷中的所有题目
        # TopicExam.objects.filter根据examPaper_number筛选试卷题目关联
        topic_exams = TopicExam.objects.filter(examPaper_number=exam_paper.number)
        # 提取题目编号列表
        topic_numbers = [te.topic_number for te in topic_exams]
        
        # 检查是否有题目
        if not topic_numbers:
            # 如果试卷中没有题目，返回错误响应
            return Response({
                'error': '试卷中没有题目'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 根据题目编号列表获取题目对象
        topics = Topic.objects.filter(topic_number__in=topic_numbers)
        
        # 检查是否获取到题目
        if not topics.exists():
            # 如果无法获取试卷题目信息，返回错误响应
            return Response({
                'error': '无法获取试卷题目信息'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建题目字典，便于查找标准答案
        # 使用字典推导式创建题目编号到题目对象的映射
        topic_dict = {topic.topic_number: topic for topic in topics}
        
        # 定义客观题类型常量（兼容多种命名格式）
        OBJECTIVE_TYPES = ['单项选择题', '多项选择题', '判断题', '单选题', '多选题']
        
        # 统计客观题数量和得分
        objective_count = 0
        objective_score = 0
        total_objective_score = 0
        
        # 保存批改详情用于展示
        # 初始化批改详情列表
        grading_details = []
        
        # 用于记录错误题目
        wrong_topics = []

        # 在遍历答题详情的循环中，确保topic变量正确初始化
        print(f'\n========== 开始批改试卷 {paper.number} ==========')
        print(f'答题详情总数：{answer_details.count()}')
        print(f'OBJECTIVE_TYPES: {OBJECTIVE_TYPES}')
        for answer_detail in answer_details:
            # 打印每道题的信息用于调试
            is_obj = answer_detail.type1 in OBJECTIVE_TYPES
            print(f'题目编号: {answer_detail.question_number}, type1: "{answer_detail.type1}", 是否客观题: {is_obj}')
            
            # 根据 type1 字段判断是否为客观题（单项选择题、多项选择题、判断题）
            # 兼容多种题型名称格式
            if answer_detail.type1 in OBJECTIVE_TYPES:
                # 增加客观题计数
                objective_count += 1

                # 查找对应题目的标准答案
                topic = topic_dict.get(answer_detail.question_number)
                print("题目",topic)
                if topic:
                    # 累加题目满分（从Topic表获取）
                    total_objective_score += topic.score or 0
                    a_d=None
                    # 根据题型处理答案对比
                    is_correct = False
                    correct_answer = topic.topic_answer or ''
                    
                    if answer_detail.type1 == '单项选择题':
                        # 单项选择题：根据选项查找答案
                        option_field = answer_detail.answer
                        if hasattr(topic, option_field):
                            selected_option_value = getattr(topic, option_field) or ''
                            a_d=selected_option_value
                            is_correct = selected_option_value.strip() == correct_answer.strip()
                    elif answer_detail.type1 == '多项选择题':
                        # 多项选择题：分割选项并查找对应答案
                        student_options = [opt.strip() for opt in (answer_detail.answer or '').split(',')]
                        correct_options = []
                        
                        for opt in student_options:
                            option_field = opt
                            if hasattr(topic, option_field):
                                selected_option_value = getattr(topic, option_field) or ''
                                correct_options.append(selected_option_value)
                        
                        # 将正确选项值用逗号连接并与标准答案比较
                        student_answer_combined = ','.join(correct_options)
                        a_d=student_answer_combined
                        is_correct = student_answer_combined.strip() == correct_answer.strip()
                    elif answer_detail.type1 == '判断题':
                        # 判断题：直接比较答案（对/错 或 True/False）
                        student_answer = (answer_detail.answer or '').strip().lower()
                        correct_answer_normalized = correct_answer.strip().lower()
                        
                        # 标准化答案：支持多种格式
                        positive_answers = ['对', '正确', 'true', 't', '√', 'yes', 'y']
                        negative_answers = ['错', '错误', 'false', 'f', '×', 'no', 'n']
                        
                        # 转换学生答案为统一格式
                        if student_answer in positive_answers:
                            student_normalized = '对'
                        elif student_answer in negative_answers:
                            student_normalized = '错'
                        else:
                            student_normalized = student_answer
                        
                        # 转换标准答案为统一格式
                        if correct_answer_normalized in positive_answers:
                            correct_normalized = '对'
                        elif correct_answer_normalized in negative_answers:
                            correct_normalized = '错'
                        else:
                            correct_normalized = correct_answer_normalized
                        
                        a_d = student_normalized
                        is_correct = student_normalized == correct_normalized

                    score = 0
                    if is_correct:
                        # 答案正确，加上该题分数
                        score = topic.score or 0
                        objective_score += score

                    # 保存学生的实际得分到数据库
                    answer_detail.score = score
                    answer_detail.save()
                    
                    # 记录批改详情
                    # 将批改结果添加到详情列表中
                    grading_details.append({
                        'question_number': answer_detail.question_number,
                        'student_answer': a_d or '',
                        'correct_answer': topic.topic_answer or '',
                        'is_correct': is_correct,
                        'score': score,
                        'max_score': topic.score or 0,
                        'type': answer_detail.type1
                    })
                    
                    # 如果答案错误，将题目添加到错题列表
                    if not is_correct:
                        wrong_topics.append({
                            'user': paper.user,
                            'topic_number': answer_detail.question_number,
                            'topic_knowledge': topic.topic_knowledge
                        })
                else:
                    # 如果找不到题目，使用answer_detail中的score作为后备
                    total_objective_score += answer_detail.score or 0
                    answer_detail.score = 0  # 默认得分为0
                    answer_detail.save()

                    # 记录批改详情
                    # 将批改结果添加到详情列表中
                    grading_details.append({
                        'question_number': answer_detail.question_number,
                        'student_answer': answer_detail.answer or '',
                        'correct_answer': '',
                        'is_correct': False,
                        'score': 0,
                        'max_score': answer_detail.score or 0,
                        'type': answer_detail.type1
                    })
            else:
                # 非选择题类型的客观题跳过批改
                continue
            
        # 重新计算试卷总分（包括客观题和主观题）
        # 初始总分为客观题得分
        total_score = objective_score
        # 添加主观题得分
        for answer_detail in answer_details:
            # 根据 type1 判断是否为主观题
            if answer_detail.type1 not in ['单项选择题', '多项选择题', '判断题'] and answer_detail.score is not None:
                # 累加主观题得分到总分
                total_score += answer_detail.score
        
        # 更新试卷总分
        # 设置试卷记录的最终得分
        paper.end_score = total_score
        # 标记为已批改（status=True表示已批改）
        paper.status = True  # 标记为已批改
        # 保存试卷记录的更改
        paper.save()

        # 将错误题目添加到错题本
        for wrong_topic in wrong_topics:
            # 检查是否已存在该错题
            existing_wrong_topic = WrongTopic.objects.filter(
                user=wrong_topic['user'],
                topic_number=wrong_topic['topic_number']
            ).first()
            
            if existing_wrong_topic:
                # 如果已存在，增加错误次数
                existing_wrong_topic.error_times += 1
                existing_wrong_topic.active = True  # 确保题目处于激活状态
                existing_wrong_topic.save()
            else:
                # 如果不存在，创建新的错题记录
                WrongTopic.objects.create(
                    user=wrong_topic['user'],
                    topic_number=wrong_topic['topic_number'],
                    error_times=1,
                    active=True,
                    topic_knowledge=wrong_topic['topic_knowledge']
                )

        # 记录操作日志
        # 使用OperationLogger记录教师的操作
        print(f'========== 批改完成 ==========')
        print(f'客观题数量: {objective_count}')
        print(f'客观题得分: {objective_score}/{total_objective_score}')
        OperationLogger.log_grading_operation(user=request.user,
                                             content=f"为试卷 {paper.number} 的客观题进行自动批改，得分:{objective_score}/{total_objective_score}")

        # 返回批改结果响应
        return Response({
            'message': f'试卷 {paper.number} 的客观题已自动批改',
            'paper_id': paper.number,
            'objective_count': objective_count,
            'objective_score': objective_score,
            'total_objective_score': total_objective_score,
            'total_score': total_score,
            'grading_details': grading_details  # 添加批改详情
        })

    # 定义自定义操作：手动批改主观题
    # 使用@action装饰器创建自定义视图操作
    @action(detail=True, methods=['post'])

    def manual_grade_subjective(self, request, pk=None):
        """
        手动批改主观题操作
        
        对指定试卷记录中的主观题进行手动批改，接受教师输入的评分。
        只有教师可以执行此操作。
        
        路径: POST /papers/{id}/manual_grade_subjective/
        
        参数:
            pk (int): 试卷记录ID
            request.data: {
                'subjective_scores': [
                    {
                        'question_number': 题目编号,
                        'score': 得分
                    },
                    ...
                ]
            }
            
        返回:
            Response: 包含批改结果的响应
            
        异常:
            PermissionDenied: 如果用户不是教师
        """
        # 检查用户权限
        # 确保用户已认证且为教师角色
        if not request.user.is_authenticated or not request.user.is_teacher():
            # 如果用户不是教师，抛出权限拒绝异常
            raise PermissionDenied("只有教师可以进行手动批改")
            
        # 获取试卷对象
        # get_object()是ModelViewSet提供的方法，用于获取当前操作的对象
        try:
            paper = self.get_object()
        except Exception as e:
            # 如果获取试卷对象失败，返回错误响应
            return Response({
                'error': f'获取试卷失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取主观题评分数据
        # 从请求数据中提取subjective_scores字段
        subjective_scores = request.data.get('subjective_scores', [])
        
        # 检查评分数据是否存在
        if not subjective_scores:
            # 如果缺少主观题评分数据，返回错误响应
            return Response({
                'error': '缺少主观题评分数据'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷对应的所有答题详情
        # AnswerDetail.objects.filter根据record_id筛选答题详情
        answer_details = AnswerDetail.objects.filter(record_id=paper.number)
        
        # 检查是否有答题详情
        if not answer_details.exists():
            # 如果试卷中没有答题记录，返回错误响应
            return Response({
                'error': '试卷中没有答题记录'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建题目编号到评分的映射
        # 使用字典推导式创建题目编号到评分的映射
        score_map = {item['question_number']: item['score'] for item in subjective_scores}
        
        # 统计主观题数量和得分
        subjective_count = 0
        subjective_score = 0
        total_subjective_score = 0
        
        # 用于记录错误题目（得分低于满分的题目）
        wrong_topics = []
        
        # 更新主观题得分
        for answer_detail in answer_details:
            # 检查答题详情是否为主观题（排除所有客观题类型：单项选择题、多项选择题、判断题）
            if answer_detail.type1 not in ['单项选择题', '多项选择题', '判断题']:
                # 增加主观题计数
                subjective_count += 1
                # 获取题目满分
                topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                max_score = topic.score if topic else (answer_detail.score or 0)
                # 累加题目满分
                total_subjective_score += max_score
                
                # 如果提供了该题的评分，则更新得分
                # 检查题目编号是否在评分映射中
                if answer_detail.question_number in score_map:
                    # 从评分映射中获取新得分
                    new_score = score_map[answer_detail.question_number]
                    # 更新答题详情的得分
                    answer_detail.score = new_score
                    # 保存答题详情的更改
                    answer_detail.save()
                    # 累加新得分到主观题总分
                    subjective_score += new_score
                    
                    # 获取题目信息以获取满分
                    topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                    max_score = topic.score if topic else (answer_detail.score or 0)
                    
                    # 如果得分低于满分，记录为错误题目
                    if new_score < max_score:
                        if topic:
                            wrong_topics.append({
                                'user': paper.user,
                                'topic_number': answer_detail.question_number,
                                'topic_knowledge': topic.topic_knowledge or ''
                            })
        
        # 如果主观题数量为0，说明只有选择题，不需要处理主观题
        if subjective_count == 0:
            return Response({
                'message': f'试卷 {paper.number} 没有主观题需要批改',
                'paper_id': paper.number,
                'subjective_count': 0,
                'subjective_score': 0,
                'total_subjective_score': 0,
                'total_score': paper.end_score  # 使用原有的总分
            })

        # 重新计算试卷总分（包括客观题和主观题）
        # 初始总分为主观题得分
        total_score = subjective_score
        # 添加客观题得分
        for answer_detail in answer_details:
            # 根据 type1 判断是否为客观题
            if answer_detail.type1 in ['单项选择题', '多项选择题', '判断题'] and answer_detail.score is not None:
                # 累加客观题得分到总分
                total_score += answer_detail.score
        
        # 更新试卷总分
        # 设置试卷记录的最终得分
        paper.end_score = total_score
        # 标记为已批改（status=True表示已批改）
        paper.status = True  # 标记为已批改
        # 保存试卷记录的更改
        paper.save()

        # 将错误题目添加到错题本
        for wrong_topic in wrong_topics:
            try:
                # 检查是否已存在该错题
                existing_wrong_topic = WrongTopic.objects.filter(
                    user=wrong_topic['user'],
                    topic_number=wrong_topic['topic_number']
                ).first()
                
                if existing_wrong_topic:
                    # 如果已存在，增加错误次数
                    existing_wrong_topic.error_times += 1
                    existing_wrong_topic.active = True  # 确保题目处于激活状态
                    existing_wrong_topic.save()
                    print(f"✓ [手动批改] 更新主观题错题: 题目编号={wrong_topic['topic_number']}, 错误次数={existing_wrong_topic.error_times}")
                else:
                    # 如果不存在，创建新的错题记录
                    WrongTopic.objects.create(
                        user=wrong_topic['user'],
                        topic_number=wrong_topic['topic_number'],
                        error_times=1,
                        active=True,
                        topic_knowledge=wrong_topic['topic_knowledge'] or ''
                    )
                    print(f"✓ [手动批改] 添加主观题错题: 题目编号={wrong_topic['topic_number']}")
            except Exception as e:
                print(f"✗ [手动批改] 添加错题失败: {str(e)}")
                import traceback
                traceback.print_exc()

        # 记录操作日志
        # 使用OperationLogger记录教师的操作
        OperationLogger.log_grading_operation(user=request.user,
                                             content=f"为主观题进行手动批改，试卷 {paper.number} 得分:{subjective_score}/{total_subjective_score}")

        # 返回批改结果响应
        return Response({
            'message': f'试卷 {paper.number} 的主观题已手动批改',
            'paper_id': paper.number,
            'subjective_count': subjective_count,
            'subjective_score': subjective_score,
            'total_subjective_score': total_subjective_score,
            'total_score': total_score
        })

    # 定义自定义操作：获取试卷主观题详情
    # 使用@action装饰器创建自定义视图操作
    @action(detail=True, methods=['get'])

    def get_subjective_questions(self, request, pk=None):
        """
        获取试卷主观题详情
        
        返回指定试卷记录中所有主观题的详细信息，包括题目内容、学生答案等。
        不包括单项选择题和多项选择题。
        
        路径: GET /papers/{id}/subjective_questions/
        
        参数:
            pk (int): 试卷记录ID
            
        返回:
            Response: 包含主观题详情的响应
        """
        # 获取试卷对象
        # get_object()是ModelViewSet提供的方法，用于获取当前操作的对象
        try:
            paper = self.get_object()
        except Exception as e:
            # 如果获取试卷对象失败，返回错误响应
            return Response({
                'error': f'获取试卷失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷对应的所有答题详情
        # AnswerDetail.objects.filter根据record_id筛选答题详情
        answer_details = AnswerDetail.objects.filter(record_id=paper.number)
        
        # 获取试卷对应的所有题目
        # 获取试卷对象关联的考试信息
        exam_paper = paper.exam_paper
        if not exam_paper:
            # 如果试卷信息不完整，返回错误响应
            return Response({
                'error': '试卷信息不完整'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取试卷中的所有题目
        # TopicExam.objects.filter根据examPaper_number筛选试卷题目关联
        topic_exams = TopicExam.objects.filter(examPaper_number=exam_paper.number)
        # 提取题目编号列表
        topic_numbers = [te.topic_number for te in topic_exams]
        # 根据题目编号列表获取题目对象
        topics = Topic.objects.filter(topic_number__in=topic_numbers)
        
        # 创建题目字典，便于查找题目内容
        # 使用字典推导式创建题目编号到题目对象的映射
        topic_dict = {topic.topic_number: topic for topic in topics}
        
        # 收集主观题详情（排除所有客观题类型）
        # 初始化主观题详情列表
        subjective_questions = []
        for answer_detail in answer_details:
            # 检查答题详情是否为主观题（排除单项选择题、多项选择题、判断题）
            if answer_detail.type1 not in ['单项选择题', '多项选择题', '判断题']:
                # 查找对应题目
                # 根据题目编号从题目字典中获取题目对象
                topic = topic_dict.get(answer_detail.question_number)
                if topic:
                    # 将主观题信息添加到详情列表中
                    subjective_questions.append({
                        'question_number': answer_detail.question_number,
                        'content': topic.topic_content,
                        'student_answer': answer_detail.answer or '',
                        'standard_answer': topic.topic_answer or '',
                        'score': answer_detail.score,
                        'max_score': topic.score or answer_detail.score  # 使用topic的score作为最大分值
                    })
        
        # 返回主观题详情响应
        return Response({
            'questions': subjective_questions
        })

    @action(detail=True, methods=['post'])
    def ai_grade_subjective(self, request, pk=None):
        """
        AI批改主观题
        
        使用通义千问AI模型对试卷中的主观题进行自动打分。
        只有教师可以执行此操作。
        
        路径: POST /papers/{id}/ai_grade_subjective/
        
        参数:
            pk (int): 试卷记录ID
            
        返回:
            Response: 包含AI评分结果的响应
            {
                'ai_scores': [
                    {
                        'question_number': 题目编号,
                        'ai_score': AI评分,
                        'max_score': 满分
                    },
                    ...
                ]
            }
        """
        if not request.user.is_authenticated or not request.user.is_teacher():
            raise PermissionDenied("只有教师可以进行AI批改")
        
        try:
            paper = self.get_object()
        except Exception as e:
            return Response({'error': f'获取试卷失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        answer_details = AnswerDetail.objects.filter(record_id=paper.number)
        if not answer_details.exists():
            return Response({'error': '试卷中没有答题记录'}, status=status.HTTP_400_BAD_REQUEST)
        
        exam_paper = paper.exam_paper
        if not exam_paper:
            return Response({'error': '试卷信息不完整'}, status=status.HTTP_400_BAD_REQUEST)
        
        topic_exams = TopicExam.objects.filter(examPaper_number=exam_paper.number)
        topic_numbers = [te.topic_number for te in topic_exams]
        topics = Topic.objects.filter(topic_number__in=topic_numbers)
        topic_dict = {topic.topic_number: topic for topic in topics}
        
        ai_service = QwenAIService()
        ai_scores = []
        
        for answer_detail in answer_details:
            # 检查答题详情是否为主观题（排除所有客观题类型：单项选择题、多项选择题、判断题）
            if answer_detail.type1 not in ['单项选择题', '多项选择题', '判断题']:
                topic = topic_dict.get(answer_detail.question_number)
                if topic:
                    try:
                        ai_score = ai_service.grade_subjective_question(
                            question_content=topic.topic_content or '',
                            student_answer=answer_detail.answer or '',
                            standard_answer=topic.topic_answer or '',
                            max_score=topic.score or 0
                        )
                        
                        # 打印调试信息
                        print(f'题目编号: {answer_detail.question_number}, AI原始返回: {ai_score}, 类型: {type(ai_score)}')
                        
                        # 将 AI 返回的字符串评分转换为整数
                        ai_score_value = int(ai_score) if isinstance(ai_score, (str, int)) else 0
                        
                        print(f'转换后的分数: {ai_score_value}')
                        
                        ai_scores.append({
                            'question_number': answer_detail.question_number,
                            'ai_score': ai_score_value,
                            'max_score': topic.score or 0
                        })
                    except Exception as e:
                        print(f'AI评分异常: {str(e)}')
                        ai_scores.append({
                            'question_number': answer_detail.question_number,
                            'ai_score': 0,
                            'max_score': topic.score or 0,
                            'error': str(e)
                        })
        
        print(f'最终返回的AI评分数据: {ai_scores}')
        
        return Response({'ai_scores': ai_scores})

    # 定义自定义操作：成绩整合
    # 使用@action装饰器创建自定义视图操作
    # detail=False表示该操作不作用于单个对象，而是作用于整个资源集合
    @action(detail=False, methods=['post'])
    def integrate_grades(self, request):
        """
        成绩整合操作
        
        对指定考试的所有试卷进行成绩整合统计，生成成绩报告。
        
        路径: POST /papers/integrate_grades/
        
        参数:
            request.data: {
                'exam_id': 考试ID
            }
            
        返回:
            Response: 包含成绩整合结果的响应
        """
        # 获取考试ID
        # 从请求数据中提取exam_id字段
        exam_id = request.data.get('exam_id')
        if not exam_id:
            # 如果缺少考试ID参数，返回错误响应
            return Response({
                'error': '缺少考试ID参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取考试对象
        # ExamPaper.objects.get根据number字段获取考试对象
        try:
            exam = ExamPaper.objects.get(number=exam_id)
        except ExamPaper.DoesNotExist:
            # 如果考试不存在，返回错误响应
            return Response({
                'error': '考试不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取该考试的所有试卷记录
        # ExamRecord.objects.filter根据exam_paper筛选试卷记录
        papers = ExamRecord.objects.filter(exam_paper=exam)
        
        # 统计数据
        # 计算试卷总数
        total_papers = papers.count()
        # 计算已批改试卷数
        graded_papers = papers.filter(status=True).count()
        # 计算未批改试卷数
        ungraded_papers = total_papers - graded_papers
        
        # 计算平均分
        # 提取所有试卷的最终得分（排除None值）
        total_scores = [paper.end_score for paper in papers if paper.end_score is not None]
        # 计算平均总分（处理空列表情况）
        average_total_score = sum(total_scores) / len(total_scores) if total_scores else 0

        # 计算各部分平均分
        # 初始化客观题得分和主观题得分列表
        objective_scores = []
        subjective_scores = []

        # 初始化客观题和主观题总分
        total_obj_max = 0
        total_subj_max = 0

        # 遍历所有试卷记录
        for paper in papers:
            # 获取答题详情
            answer_details = AnswerDetail.objects.filter(record_id=paper.number)
            # 初始化客观题得分和主观题得分
            obj_score = 0
            subj_score = 0

            # 遍历答题详情
            for detail in answer_details:
                # 获取题目信息
                topic = Topic.objects.filter(topic_number=detail.question_number).first()

                # 根据 type1 判断题型
                if detail.type1 in ['单项选择题', '多项选择题', '判断题']:  # 客观题
                    obj_score += detail.score or 0  # 实际得分
                    # 使用topic.score作为题目满分，如果没有topic则使用detail.score作为后备
                    total_obj_max += topic.score if topic else (detail.score or 0)
                else:  # 主观题
                    subj_score += detail.score or 0  # 实际得分
                    # 使用topic.score作为题目满分，如果没有topic则使用detail.score作为后备
                    total_subj_max += topic.score if topic else (detail.score or 0)

            # 将得分添加到对应列表中
            objective_scores.append(obj_score)
            subjective_scores.append(subj_score)

        # 计算客观题和主观题的平均分
        average_objective_score = sum(objective_scores) / len(objective_scores) if objective_scores else 0
        average_subjective_score = sum(subjective_scores) / len(subjective_scores) if subjective_scores else 0
        
        # 计算最高分
        # 从总分、客观题分和主观题分中找出最高分
        highest_total_score = max(total_scores) if total_scores else 0
        highest_objective_score = max(objective_scores) if objective_scores else 0
        highest_subjective_score = max(subjective_scores) if subjective_scores else 0
        
        # 计算及格率和优秀率（假设满分100分）
        # 统计及格人数（>=60分）
        pass_count = len([s for s in total_scores if s >= 60]) if total_scores else 0
        # 统计优秀人数（>=85分）
        excellent_count = len([s for s in total_scores if s >= 85]) if total_scores else 0
        # 计算及格率和优秀率
        pass_rate = (pass_count / len(total_scores) * 100) if total_scores else 0
        excellent_rate = (excellent_count / len(total_scores) * 100) if total_scores else 0
        
        # 试卷详细信息
        # 初始化试卷详情列表
        paper_details = []
        for paper in papers:
            # 获取答题详情
            answer_details = AnswerDetail.objects.filter(record_id=paper.number)
            # 初始化客观题得分和主观题得分
            obj_score = 0
            subj_score = 0
            
            # 遍历答题详情
            for detail in answer_details:
                # 根据 type1 判断题型
                if detail.type1 in ['单项选择题', '多项选择题', '判断题']:  # 客观题
                    # 累加客观题得分
                    obj_score += detail.score or 0
                else:  # 主观题
                    # 累加主观题得分
                    subj_score += detail.score or 0
            
            # 获取学生姓名
            student_name = ""
            # 检查试卷记录是否关联了用户对象
            if paper.user:
                # 根据用户信息构建学生姓名
                if paper.user.last_name and paper.user.first_name:
                    # 如果同时有姓和名，组合成完整姓名
                    student_name = f"{paper.user.last_name}{paper.user.first_name}"
                elif paper.user.first_name:
                    # 如果只有名，使用名作为学生姓名
                    student_name = paper.user.first_name
                else:
                    # 如果以上信息都不存在，使用用户名作为学生姓名
                    student_name = paper.user.username
            
            # 将试卷详情添加到列表中
            paper_details.append({
                'paper_id': paper.number,
                'student_name': student_name,
                'status': '已批改' if paper.status else '未批改',
                'objective_score': obj_score,
                'subjective_score': subj_score,
                'total_score': paper.end_score or 0
            })
        
        # 返回成绩整合结果响应
        return Response({
            'exam_name': exam.name,
            'stats': {
                'total_papers': total_papers,
                'graded_papers': graded_papers,
                'ungraded_papers': ungraded_papers,
                'average_total_score': round(average_total_score, 2),
                'average_objective_score': round(average_objective_score, 2),
                'average_subjective_score': round(average_subjective_score, 2),
                'highest_total_score': highest_total_score,
                'highest_objective_score': highest_objective_score,
                'highest_subjective_score': highest_subjective_score,
                'pass_rate': round(pass_rate, 2),
                'excellent_rate': round(excellent_rate, 2)
            },
            'paper_details': paper_details,
            'message': '成绩整合完成'
        })


# 报告视图集 - 提供成绩报告相关功能
# 继承自Django REST framework的ModelViewSet
class ReportViewSet(viewsets.ModelViewSet):
    # 查询集：获取所有考试记录
    # ExamRecord.objects.all()返回ExamRecord模型的所有记录
    queryset = ExamRecord.objects.all()
    # 序列化器类
    # ReportSerializer定义了报告数据的序列化规则
    serializer_class = ReportSerializer
    
    # 重写dispatch方法以确保响应使用UTF-8编码
    def dispatch(self, request, *args, **kwargs):
        """
        重写dispatch方法，确保响应使用UTF-8编码
        """
        # 确保响应使用UTF-8编码
        # 调用父类的dispatch方法处理请求
        response = super().dispatch(request, *args, **kwargs)
        # 设置响应的Content-Type头，确保使用UTF-8编码
        response['Content-Type'] = 'application/json; charset=utf-8'
        # 返回处理后的响应
        return response

    # 重写get_queryset方法以实现自定义查询逻辑
    def get_queryset(self):
        """
        获取查询集，根据用户角色过滤报告数据
        教师可以看到所有报告，学生只能看到自己的
        """
        # 检查用户是否已登录
        # request.user.is_authenticated检查用户是否已通过认证
        if not self.request.user.is_authenticated:
            # 如果用户未认证，抛出权限拒绝异常
            raise PermissionDenied("用户未登录")
            
        # 获取所有考试记录
        # ExamRecord.objects.all()获取ExamRecord模型的所有记录
        queryset = ExamRecord.objects.all()
        # 获取查询参数中的考试ID
        # 从URL查询参数中提取exam_id
        exam_id = self.request.query_params.get('exam_id', None)
        
        # 如果是学生用户，只能查看自己的报告
        # request.user.is_student()检查当前用户是否为学生角色
        if self.request.user.is_student():
            # 筛选user字段等于当前用户的记录
            queryset = queryset.filter(user=self.request.user)
        # 如果提供了考试ID，则过滤该考试的记录
        if exam_id is not None:
            # 筛选exam_paper__number字段等于exam_id的记录
            queryset = queryset.filter(exam_paper__number=exam_id)
        # 返回过滤后的查询集
        return queryset

    # 重写list方法以返回详细的试卷信息
    def list(self, request, *args, **kwargs):
        """
        重写list方法以返回详细的试卷信息
        """
        # 过滤查询集
        # 调用filter_queryset方法对查询集进行过滤
        queryset = self.filter_queryset(self.get_queryset())
        
        # 获取考试ID
        # 从URL查询参数中提取exam_id
        exam_id = request.query_params.get('exam_id', None)
        
        # 为每个试卷添加详细的成绩信息
        # 初始化试卷数据列表
        papers_data = []
        for paper in queryset:
            # 获取答题详情
            # AnswerDetail.objects.filter根据record_id筛选答题详情
            answer_details = AnswerDetail.objects.filter(record_id=paper.number)
            
            # 计算客观题和主观题得分
            # 初始化各类得分变量
            objective_score = 0
            subjective_score = 0
            total_objective_score = 0
            total_subjective_score = 0
            
            # 收集主观题详情和客观题详情
            # 初始化主观题详情和客观题详情列表
            subjective_details = []
            objective_details = []
            
            # 遍历答题详情
            # 在遍历答题详情时：
            for answer_detail in answer_details:
                # 获取题目信息
                topic = Topic.objects.filter(topic_number=answer_detail.question_number).first()
                max_score = topic.score if topic else (answer_detail.score or 0)

                # 根据 type1 判断题型
                if answer_detail.type1 in ['单项选择题', '多项选择题', '判断题']:  # 客观题
                    total_objective_score += max_score  # 题目满分
                    objective_score += answer_detail.score or 0  # 实际得分
                else:  # 主观题
                    total_subjective_score += max_score  # 题目满分
                    subjective_score += answer_detail.score or 0  # 实际得分
                    # 实际得分已在手动批改中设置
                    # 收集主观题详情
                    subjective_details.append({
                        'question_number': answer_detail.question_number,
                        'score': answer_detail.score or 0,
                        'max_score': answer_detail.score or 0  # 这里暂时使用score作为max_score，实际应该从题目表获取
                    })
            
            # 计算客观题数量
            # 使用len函数获取客观题详情列表的长度
            objective_count = len(objective_details)
            # 计算主观题数量
            # 使用len函数获取主观题详情列表的长度
            subjective_count = len(subjective_details)
            
            # 将试卷数据添加到列表中
            papers_data.append({
                'id': paper.number,
                'user': paper.user.id if paper.user else None,
                'end_time': paper.end_time,
                'status': paper.status,
                'end_score': paper.end_score,
                'exam_paper': paper.exam_paper.number if paper.exam_paper else None,
                'objective_score': objective_score,
                'subjective_score': subjective_score,
                'total_objective_score': total_objective_score,
                'total_subjective_score': total_subjective_score,
                'objective_count': objective_count,  # 添加客观题数量
                'subjective_count': subjective_count,  # 添加主观题数量
                'subjective_details': subjective_details,  # 添加主观题详情
                'objective_details': objective_details  # 添加客观题详情
            })
        
        # 直接返回数据而不是序列化后的数据
        # 使用Response类返回处理后的数据
        return Response(papers_data)

    # 定义自定义操作：根据考试ID获取参加该考试的班级列表
    # 使用@action装饰器创建自定义视图操作
    @action(detail=False, methods=['get'], url_path='get_classes_by_exam')
    def get_classes_by_exam(self, request):
        """
        根据考试ID获取参加该考试的学生所在的班级列表
        只有教师可以查看这些信息
        """
        # 检查用户权限
        # 确保用户已认证且为教师角色
        if not request.user.is_authenticated or not request.user.is_teacher():
            # 如果用户不是教师，抛出权限拒绝异常
            raise PermissionDenied("只有教师可以查看班级信息")
            
        # 获取请求参数
        exam_id = request.query_params.get('exam_id', None)
        
        # 检查是否提供了考试ID
        if not exam_id:
            return Response({'error': '缺少考试ID参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取参加该考试的所有学生试卷记录
            exam_records = ExamRecord.objects.filter(exam_paper__number=exam_id).select_related('user__class1__class1')
            
            # 获取唯一的班级列表
            classes = set()
            for record in exam_records:
                if record.user and record.user.class1:
                    classes.add(record.user.class1)
            
            # 格式化班级数据
            class_list = []
            for cls in classes:
                if cls.class1:  # 确保班级有名称信息
                    class_list.append({
                        'id': cls.id,
                        'name': cls.class1.class_name
                    })
            
            return Response(class_list)
            
        except Exception as e:
            return Response({'error': f'获取班级列表失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 定义自定义操作：获取个人报告
    # 使用@action 装饰器创建自定义视图操作
    @action(detail=False, methods=['get'], url_path='personal')
    def get_personal_report(self, request):
        """
        获取学生个人成绩报告
        学生只能查看自己的报告
        """
        # 检查用户权限
        # 确保用户已认证
        if not request.user.is_authenticated:
            raise PermissionDenied("用户未登录")
                
        # 获取请求参数
        exam_id = request.query_params.get('exam_id', None)
            
        # 检查是否提供了考试 ID
        if not exam_id:
            return Response({'error': '缺少考试 ID 参数'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 获取当前用户的试卷记录
            print(f"\n=== 开始查询个人报告 ===")
            print(f"当前用户：{request.user.username} (ID: {request.user.id})")
            print(f"请求的考试 ID: {exam_id}")
            
            # 先查询该用户的所有考试记录
            all_records = ExamRecord.objects.filter(user=request.user)
            print(f"用户 {request.user.username} 共有 {all_records.count()} 条考试记录")
            for record in all_records:
                print(f"  - 记录 ID: {record.number}, 考试：{record.exam_paper}, 考试编号：{record.exam_paper.number if record.exam_paper else None}")
            
            # 查询指定考试的记录
            paper = ExamRecord.objects.filter(
                exam_paper__number=exam_id,
                user=request.user
            ).first()
            
            print(f"查询结果：paper={paper}")
            if paper:
                print(f"  找到记录 - ID: {paper.number}, 考试：{paper.exam_paper.name if paper.exam_paper else None}")
            else:
                print(f"  未找到考试编号为 {exam_id} 的记录")
                # 尝试查询该用户的所有 ExamRecord，看看 exam_paper 字段是否为空
                all_records_with_details = ExamRecord.objects.filter(user=request.user).select_related('exam_paper')
                print(f"\n详细检查所有记录：")
                for record in all_records_with_details:
                    print(f"  - Record number={record.number}, exam_paper={record.exam_paper}, exam_paper.number={record.exam_paper.number if record.exam_paper else 'None'}")
                
            # 检查是否存在记录
            if not paper:
                return Response({'message': '暂无数据，请选择其他考试'})
                
            # 获取答题详情
            answer_details = AnswerDetail.objects.filter(record_id=paper.number)
                
            # 计算客观题和主观题得分
            objective_score = 0
            objective_total = 0
            subjective_score = 0
            subjective_total = 0
                
            for detail in answer_details:
                topic = Topic.objects.filter(topic_number=detail.question_number).first()
                if topic:
                    # 根据 type1 判断题型
                    if detail.type1 in ['单项选择题', '多项选择题', '判断题']:  # 客观题
                        objective_score += detail.score or 0
                        objective_total += topic.score or 0
                    else:  # 主观题
                        subjective_score += detail.score or 0
                        subjective_total += topic.score or 0
                
            # 计算总分
            total_score = objective_score + subjective_score
            total_total = objective_total + subjective_total
                
            # 计算成绩等级
            if total_total > 0:
                percentage = (total_score / total_total) * 100
                if percentage >= 90:
                    score_level = "优秀"
                elif percentage >= 80:
                    score_level = "良好"
                elif percentage >= 60:
                    score_level = "及格"
                else:
                    score_level = "不及格"
            else:
                score_level = "未评分"
                
            # 获取考试名称
            exam_name = paper.exam_paper.name if paper.exam_paper else "未知考试"
                
            # 构建能力分析数据（按知识点统计）
            abilities = []
            knowledge_stats = {}
                
            for detail in answer_details:
                topic = Topic.objects.filter(topic_number=detail.question_number).first()
                if topic and topic.topic_knowledge:
                    knowledge = topic.topic_knowledge
                    if knowledge not in knowledge_stats:
                        knowledge_stats[knowledge] = {'total': 0, 'scored': 0}
                    knowledge_stats[knowledge]['total'] += topic.score or 0
                    knowledge_stats[knowledge]['scored'] += detail.score or 0
                
            # 转换为图表所需格式
            for knowledge, stats in knowledge_stats.items():
                score_percentage = (stats['scored'] / stats['total'] * 100) if stats['total'] > 0 else 0
                abilities.append({
                    'name': knowledge,
                    'score': round(score_percentage, 1)
                })
                
            # 构建响应数据
            report_data = {
                'exam_name': exam_name,
                'objective_score': round(objective_score, 1),
                'objective_total': round(objective_total, 1),
                'subjective_score': round(subjective_score, 1),
                'subjective_total': round(subjective_total, 1),
                'total_score': round(total_score, 1),
                'total_total': round(total_total, 1),
                'score_level': score_level,
                'class_rank': 1,  # 简化版本，后续可添加实际排名计算
                'school_rank': 1,
                'class_rank_change': 0,
                'school_rank_change': 0,
                'exceed_percentage': 0,
                'abilities': abilities
            }
                
            return Response(report_data)
                
        except Exception as e:
            return Response({'error': f'获取个人报告失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
