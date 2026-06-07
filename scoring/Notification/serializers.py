from rest_framework import serializers
from management.models import Notification, User
from .notification_constants import NotificationType

class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    - 序列化通知模型，包括所有字段。
    - 设置只读字段：id 和 created_at。
    """
    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "receiver",
            "title",
            "content",
            "type",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]  # 这些字段只读
        
    def validate_receiver(self, value):
        """
        验证接收者字段
        """
        if not value:
            raise serializers.ValidationError("接收者不能为空")
        return value
        
    def validate_type(self, value):
        """
        验证通知类型
        """
        if not NotificationType.is_valid_type(value):
            raise serializers.ValidationError(f"无效的通知类型: {value}")
        return value
        
    def validate(self, attrs):
        """
        验证整体数据
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            # 在创建时，如果未指定发送者，则默认为当前用户
            if 'sender' not in attrs or attrs['sender'] is None:
                attrs['sender'] = request.user
                
            # 验证发送者权限
            sender = attrs.get('sender', request.user)
            notification_type = attrs.get('type', NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION)
            
            # 检查发送者角色是否允许发送该类型的通知
            user_role = getattr(sender, 'role', 'student')
            
            if sender.is_superuser:
                # 超级管理员可以发送所有类型的通知
                allowed_types = NotificationType.TYPES
            else:
                # 根据角色获取允许的通知类型
                allowed_types = CanSendNotification.ALLOWED_TYPES_BY_ROLE.get(user_role, [])
                    
            if notification_type not in allowed_types and not sender.is_superuser:
                raise serializers.ValidationError(f"用户角色 '{user_role}' 不允许发送 '{notification_type}' 类型的通知")
                
        return attrs

# 导入CanSendNotification以在验证中使用
from .permissions import CanSendNotification