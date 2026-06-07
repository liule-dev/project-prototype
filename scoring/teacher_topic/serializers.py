from rest_framework import serializers, viewsets
from management.models import Subject, QuestionDatabase, Grade, User, Topic, OperationRecord


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            'id',
            'subject_name',
            'choice_count',
            'choice_score',
            'multiple_choice_score',
            'multiple_choice_count',
            'judgment_count',
            'judgment_score',
            'calculation_analysis_count',
            'calculation_analysis_score',
            'case_analysis_count',
            'case_analysis_score',
            'comprehensive_count',
            'comprehensive_score'
        ]



class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'


# 题库
# 题库
class QuestionSerializer(serializers.ModelSerializer):
    subject_name = serializers.StringRelatedField(source='subject', read_only=True)
    grade1_name = serializers.StringRelatedField(source='grade1', read_only=True)
    creator_name = serializers.CharField(source='user.username', read_only=True)
    # 反序列化时接收 ID
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    grade1 = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all())
    # 关键修改：设置user字段为非必填，因为在视图中动态添加
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )

    status = serializers.CharField(default="未提交")

    class Meta:
        model = QuestionDatabase
        fields = ["user", "Question_number", 'question_total', "name", "question_type", "subject", "subject_name",
                  "grade1", "grade1_name", "status", "if_public", "created_at", "updated_at", 'creator_name']


# 登录
class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.CharField(required=False)  # 关键：设为非必填

    class Meta:
        model = User
        fields = ['username', 'password', 'role']


# 题目
class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'

        # 允许A, B, C, D字段为空
        extra_kwargs = {
            'A': {'required': False, 'allow_blank': True, 'allow_null': True},
            'B': {'required': False, 'allow_blank': True, 'allow_null': True},
            'C': {'required': False, 'allow_blank': True, 'allow_null': True},
            'D': {'required': False, 'allow_blank': True, 'allow_null': True},
            'E': {'required': False, 'allow_blank': True, 'allow_null': True},
            'topic_analysis': {'required': False, 'allow_blank': True, 'allow_null': True},
            'topic_knowledge': {'required': False, 'allow_blank': True, 'allow_null': True},
        }


class OperationRecordSerializer(serializers.ModelSerializer):
    """操作记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    operation_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OperationRecord
        fields = ['id', 'user', 'username', 'operation_type', 'content', 'operation_time']
        read_only_fields = ['id', 'operation_time']