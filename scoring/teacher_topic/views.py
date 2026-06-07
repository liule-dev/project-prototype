from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from management.models import QuestionDatabase, Subject, Grade, User, Topic, OperationRecord  # 必须导入模型
from .serializers import QuestionSerializer, SubjectSerializer, GradeSerializer, LoginSerializer, TopicSerializer, \
    OperationRecordSerializer
from rest_framework import viewsets, filters

from .utils import OperationLogger



# 学科数据
class SubjectListView(generics.ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer



class SubjectCreateView(generics.CreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 添加用户认证信息（可选）
        data = request.data.copy()

        # 设置默认值(如果前端没有提供,则设置为0)
        
        if 'choice_count' not in data:
            data['choice_count'] = 0
        if 'choice_score' not in data:
            data['choice_score'] = 0
        if 'multiple_choice_score' not in data:
            data['multiple_choice_score'] = 0
        if 'multiple_choice_count' not in data:
            data['multiple_choice_count'] = 0
        if 'judgment_count' not in data:
            data['judgment_count'] = 0
        if 'judgment_score' not in data:
            data['judgment_score'] = 0
        if 'calculation_analysis_count' not in data:
            data['calculation_analysis_count'] = 0
        if 'calculation_analysis_score' not in data:
            data['calculation_analysis_score'] = 0
        if 'case_analysis_count' not in data:
            data['case_analysis_count'] = 0
        if 'case_analysis_score' not in data:
            data['case_analysis_score'] = 0
        if 'comprehensive_count' not in data:
            data['comprehensive_count'] = 0
        if 'comprehensive_score' not in data:
            data['comprehensive_score'] = 0

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"msg": "学科添加成功", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"msg": f"保存失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubjectDeleteView(generics.DestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # 可选：记录日志或执行其他操作
            instance.delete()
            return Response(
                {"msg": "学科删除成功"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"msg": f"删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# 年级数据
class GradeListView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class GradeCreateView(generics.CreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 添加用户认证信息（可选）
        data = request.data.copy()
        # 如果需要记录创建人，可以在这里添加
        # data['created_by'] = request.user.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"msg": "年级添加成功", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"msg": f"保存失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class GradeDeleteView(generics.DestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # 可选：记录日志或执行其他操作
            instance.delete()
            return Response(
                {"msg": "年级删除成功"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"msg": f"删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = QuestionDatabase.objects.all()
    serializer_class = QuestionSerializer
    authentication_classes = [JWTAuthentication]  # 强制JWT认证
    permission_classes = [IsAuthenticated]  # 仅允许已认证用户访问

    def create(self, request, *args, **kwargs):
        # 调试：打印认证状态和用户信息
        print(f"用户认证状态: {request.user.is_authenticated}")
        print(f"当前用户: {request.user}")  # 应输出用户名或用户对象

        # 验证用户是否已认证
        if not request.user.is_authenticated:
            return Response(
                {"msg": "用户未登录或认证失败"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 复制请求数据并强制添加user_id
        data = request.data.copy()
        data['user'] = request.user.id  # 从认证用户中获取ID
        print(f"准备保存的数据: {data}")  # 调试：确认user字段已设置

        # 添加题目数量字段（默认为0）
        data['question_total'] = 0

        # 验证并保存
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                question_bank = serializer.save()  # 保存到数据库
                # 记录题库创建操作日志
                OperationLogger.log_question_bank_operation(
                    user=request.user,
                    content=f"创建题库，题库ID:{question_bank.Question_number}，题库名称:{question_bank.name}")
                return Response(
                    {"msg": "题库添加成功", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                # 捕获数据库保存时的错误
                return Response(
                    {"msg": f"保存失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        # 更新题库信息
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            try:
                question_bank = serializer.save()

                # 创建字段名映射字典
                field_mapping = {
                    'name': '题库名称',
                    'grade1': '年级',
                    'subject': '学科',
                    'question_type': '题型',
                    'if_public': '是否公开',
                    'Question_number': '题库编号'
                }

                # 转换修改内容中的字段名为中文
                modified_content = {}
                for field, value in request.data.items():
                    chinese_field = field_mapping.get(field, field)
                    modified_content[chinese_field] = value

                # 记录题库更新操作日志
                OperationLogger.log_question_bank_operation(
                    user=request.user,
                    content=f"更新题库，题库ID:{question_bank.Question_number}，修改内容:{modified_content}"
                )

                return Response(
                    {"msg": "题库更新成功", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"msg": f"更新失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        # 删除题库
        instance = self.get_object()
        question_bank_id = instance.Question_number
        question_bank_name = instance.name

        try:
            self.perform_destroy(instance)

            # 记录题库删除操作日志
            OperationLogger.log_question_bank_operation(
                user=request.user,
                content=f"删除题库，题库ID:{question_bank_id}，题库名称:{question_bank_name}"
            )

            return Response(
                {"msg": "题库删除成功"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"msg": f"删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        grade1_id = self.request.query_params.get('grade1_id')  # 年级ID
        subject_id = self.request.query_params.get('subject_id')  # 学科ID
        question_type = self.request.query_params.get('question_type')  # 题型
        Question_number = self.request.query_params.get('Question_number')  # 编号
        queryset = QuestionDatabase.objects.all()
        users = self.request.query_params.get('users')
        sorting = self.request.query_params.get('sorting')
        publicks = self.request.query_params.get('publicks')
        teacher_name = self.request.query_params.get('teacher_name')
        types = self.request.query_params.get('types')

        if types:
            queryset = queryset.filter(status=types)

        if teacher_name:
            queryset = queryset.filter(user__username__icontains=teacher_name)

        if users:
            queryset = queryset.filter(user=self.request.user)
        if publicks:
            queryset = queryset.filter(if_public=publicks)
        # 3. 动态添加筛选条件（有参数才筛选）
        if grade1_id:
            queryset = queryset.filter(grade1_id=grade1_id)

        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        if question_type:
            queryset = queryset.filter(question_type=question_type)

        if Question_number:
            queryset = queryset.filter(Question_number=Question_number)

        if sorting:
            return queryset.order_by('-created_at')
        else:
            return queryset


class UserLoginView(APIView):
    # 假设LoginSerializer已定义，这里保持不变
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': '用户名和密码不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
            # 注意：以下是明文密码比较，非常不安全！
            if password == user.password:  # 直接比较明文密码（不推荐）
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'role': user.role
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': '密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': '用户名不存在'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': f'登录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    authentication_classes = [JWTAuthentication]  # 强制JWT认证
    permission_classes = [IsAuthenticated]
    lookup_field = 'topic_number'

    def create(self, request, *args, **kwargs):
        # 调试：打印认证状态和用户信息
        print(f"用户认证状态: {request.user.is_authenticated}")
        print(f"当前用户: {request.user}")  # 输出用户名或用户对象

        # 验证用户是否已认证
        if not request.user.is_authenticated:
            return Response(
                {"msg": "用户未登录或认证失败"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 使用请求数据（不添加user字段，因为序列化器中没有该字段）
        data = request.data.copy()

        # 获取所属题库ID
        q_data_id = data.get('Q_data')
        if q_data_id:
            try:
                # 获取题库对象
                question_database = QuestionDatabase.objects.get(Question_number=q_data_id)
                # 获取题库的题目类型并赋值给topic_type
                data['topic_type'] = question_database.question_type

                # 根据题库的学科和题目类型获取对应的分数
                subject = question_database.subject
                question_type = question_database.question_type

                # 根据题目类型从学科中获取对应分数
                if question_type == '单项选择题':  # 选择题
                    score = subject.choice_score
                elif question_type == '多项选择题':  # 多选题
                    score = subject.multiple_choice_score
                elif question_type == '判断题':  # 判断题
                    score = subject.judgment_score
                elif question_type == '计算分析题':  # 计算分析题
                    score = subject.calculation_analysis_score
                elif question_type == '案例分析题':  # 案例分析题
                    score = subject.case_analysis_score
                elif question_type == '综合题':  # 综合题
                    score = subject.comprehensive_score
                else:
                    score = 0  # 默认分数

                # 将获取的分数赋值给题目
                data['score'] = score
            except QuestionDatabase.DoesNotExist:
                return Response(
                    {"msg": "题库不存在"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except AttributeError:
                return Response(
                    {"msg": "题库或学科信息不完整"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        print(f"准备保存的数据: {data}")  # 调试：确认数据正确性

        # 验证并保存题目数据
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                topic = serializer.save()  # 保存到数据库

                # 创建题目
                OperationLogger.log_question_bank_operation(
                    user=request.user,
                    content=f"创建题目，题目ID:{topic.topic_number}"
                )  # 保存到数据库
                return Response(
                    {"msg": "题目添加成功", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                # 捕获数据库保存时的错误
                return Response(
                    {"msg": f"保存失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        # 更新题目信息
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            try:
                topic = serializer.save()

                # 创建题目字段名映射字典
                field_mapping = {
                    'topic_number': '题目编号',
                    'Q_data': '所属题库',
                    'topic_content': '题目内容',
                    'topic_answer': '题目答案',
                    'topic_diffculty': '题目难度',
                    'topic_knowledge': '知识点'
                }

                # 转换修改内容中的字段名为中文
                modified_content = {}
                for field, value in request.data.items():
                    chinese_field = field_mapping.get(field, field)
                    modified_content[chinese_field] = value

                # 更新题目
                OperationLogger.log_question_bank_operation(
                    user=request.user,
                    content=f"更新题目，题目ID:{topic.topic_number}，修改内容:{modified_content}"
                )

                return Response(
                    {"msg": "题目更新成功", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"msg": f"更新失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"msg": "数据验证失败", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        # 删除题目
        instance = self.get_object()
        topic_id = instance.topic_number

        try:
            self.perform_destroy(instance)

            # 删除题目
            OperationLogger.log_question_bank_operation(
                user=request.user,
                content=f"删除题目，题目ID:{topic_id}"
            )

            return Response(
                {"msg": "题目删除成功"},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"msg": f"删除失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        queryset = Topic.objects.all()
        # 根据序列化器中的字段添加筛选条件
        # 按难度筛选
        difficulty = self.request.query_params.get('topic_difficulty')
        if difficulty:
            queryset = queryset.filter(topic_difficulty=difficulty)

        # 按知识点筛选
        knowledge = self.request.query_params.get('topic_knowledge')
        if knowledge:
            queryset = queryset.filter(topic_knowledge=knowledge)

        # 按题型编号筛选
        topic_type = self.request.query_params.get('topic_type')
        if topic_type:
            queryset = queryset.filter(topic_number=topic_type)
        # 按题库编号查询
        Q_data = self.request.query_params.get('Q_data')
        if Q_data:
            queryset = queryset.filter(Q_data=Q_data)
        # 按题目编号查询
        topic_number = self.request.query_params.get('topic_number')
        if topic_number:
            queryset = queryset.filter(topic_number=topic_number)
        # 按创建时间倒序排列
        return queryset.order_by('-created_at')

    def get_object(self):
        try:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            return Topic.objects.get(**filter_kwargs)
        except Topic.DoesNotExist:
            raise Http404("题目不存在")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取题目失败: {str(e)}")
            raise Http404("获取题目失败")




class OperationRecordViewSet(viewsets.ModelViewSet):
    """
    操作记录视图集
    仅通过管理员页面专用入口访问
    """
    queryset = OperationRecord.objects.all().order_by('-operation_time')
    serializer_class = OperationRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operation_type', 'user']
    search_fields = ['content', 'user__username']
    ordering_fields = ['operation_time', 'id']  # 创建题目

    def get_queryset(self):
        queryset = super().get_queryset()

        # 获取日期范围参数
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        # 根据日期范围过滤
        if start_date and end_date:
            # 注意：这里需要确保日期格式正确，并包含整天的数据
            from django.utils import timezone
            from datetime import datetime, time
            try:
                # 将字符串转换为日期对象
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

                # 设置开始时间为当天00:00:00，结束时间为当天23:59:59
                start_datetime = timezone.make_aware(datetime.combine(start_date_obj, time.min))
                end_datetime = timezone.make_aware(datetime.combine(end_date_obj, time.max))

                queryset = queryset.filter(operation_time__range=(start_datetime, end_datetime))
            except ValueError:
                # 如果日期格式不正确，则不进行过滤
                pass

        return queryset
