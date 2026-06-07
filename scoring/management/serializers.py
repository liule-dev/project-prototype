from rest_framework import serializers
from .models import Class, User, ExamPaper, ExamRecord, ClassName


class ClassNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassName
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    class1 = ClassNameSerializer(read_only=True)
    
    class Meta:
        model = Class
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # 创建用户时加密密码
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamPaper
        fields = '__all__'
        # 确保包含所有字段，特别是name字段


class PaperSerializer(serializers.ModelSerializer):
    exam_paper = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ExamRecord
        fields = '__all__'
        depth = 1


class SubjectiveAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamRecord
        fields = '__all__'


class ReportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.IntegerField(allow_null=True)
    end_time = serializers.DateTimeField()
    status = serializers.BooleanField()
    end_score = serializers.FloatField(allow_null=True)
    exam_paper = serializers.IntegerField(allow_null=True)
    objective_score = serializers.FloatField()
    subjective_score = serializers.FloatField()
    total_objective_score = serializers.FloatField()
    total_subjective_score = serializers.FloatField()


from rest_framework import serializers
from management.models import OperationRecord


class OperationRecordSerializer(serializers.ModelSerializer):
    """操作记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationRecord
        fields = ['id', 'user', 'username', 'operation_type', 'content', 'operation_time']
        read_only_fields = ['id', 'operation_time']