from rest_framework import serializers
from management.models import OperationRecord


class OperationRecordSerializer(serializers.ModelSerializer):
    """操作记录序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = OperationRecord
        fields = ['id', 'user', 'username', 'operation_type', 'content', 'operation_time']
        read_only_fields = ['id', 'operation_time']