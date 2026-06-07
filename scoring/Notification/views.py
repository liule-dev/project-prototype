from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import models
from management.models import Notification, User
from .permissions import IsSuperAdminOrReadOnly, IsReceiverOrAdmin, CanSendNotification
from .serializers import NotificationSerializer
from .notification_constants import NotificationType


class NotificationViewSet(viewsets.ModelViewSet):
    """
    通知视图集
    - 提供对通知的增删查改功能。
    - 支持权限控制：接收者可以查看自己的通知，超级管理员可以查看所有通知。
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    # 权限设置：超级管理员有全部权限，普通用户只能查看自己的通知
    permission_classes = [IsSuperAdminOrReadOnly, IsReceiverOrAdmin]

    # 过滤器设置：支持根据接收者、通知类型等字段进行过滤
    filterset_fields = ["receiver", "type", "is_read"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # 定义搜索字段
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "is_read"]

    # 权限控制：用户只能操作与自己相关的通知
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'role', '') == 'admin':
            # 超级管理员和管理员可以看到所有通知
            return Notification.objects.all()
        elif getattr(user, 'role', '') == 'teacher':
            # 教师可以看到自己接收的通知以及自己发送的通知
            return Notification.objects.filter(
                models.Q(receiver=user) | models.Q(sender=user)
            ).distinct()
        else:
            # 其他用户（学生）只能查看自己接收的通知
            return Notification.objects.filter(receiver=user)

    def perform_create(self, serializer):
        """
        创建通知时，自动设置发送者为当前用户
        """
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        """
        更新通知时，无需特别处理
        """
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """
        获取单个通知时，将该通知标记为已读
        """
        instance = self.get_object()
        instance.is_read = True
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[CanSendNotification])
    def mark_as_read(self, request):
        """
        批量标记通知为已读
        """
        user = request.user
        # 检查用户是否为认证用户
        if not user.is_authenticated:
            return Response({"error": "用户未认证"}, status=401)

        notifications = Notification.objects.filter(receiver=user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "成功标记所有通知为已读"})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        获取未读通知数量
        """
        user = request.user
        count = Notification.objects.filter(receiver=user, is_read=False).count()
        return Response({"unread_count": count})
        
    @action(detail=False, methods=['post'], permission_classes=[CanSendNotification], url_path='send-to-user')  # 允许管理员发送通知
    def send_to_user(self, request):
        """
        发送通知给指定用户
        """
        user = request.user
        user_role = getattr(user, 'role', 'student')
        
        # 获取通知类型
        notification_type = request.data.get('type', NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION)
        
        # 检查用户角色是否允许发送该类型的通知
        allowed_types = CanSendNotification.ALLOWED_TYPES_BY_ROLE.get(user_role, [])
        if not user.is_superuser and notification_type not in allowed_types:
            return Response({"error": f"您没有权限发送'{notification_type}'类型的通知"}, status=403)
            
        # 根据用户角色自动确定接收者
        from django.contrib.auth import get_user_model
        User = get_user_model()


        receivers = User.objects.filter(role='student')


        # 为每个接收者创建通知
        notifications_data = []
        for receiver in receivers:
            notification_data = {
                'receiver': receiver.id,
                'title': request.data.get('title'),
                'content': request.data.get('content'),
                'type': notification_type
            }
            notifications_data.append(notification_data)
            
        # 使用 NotificationSerializer 来处理数据
        created_notifications = []
        errors = []
        
        for notification_data in notifications_data:
            serializer = NotificationSerializer(data=notification_data, context={'request': request})
            if serializer.is_valid():
                serializer.save(sender=request.user)
                created_notifications.append(serializer.data)
            else:
                errors.append(serializer.errors)
                
        if errors:
            return Response({
                "message": f"部分通知发送成功，{len(errors)}个失败",
                "errors": errors,
                "success_count": len(created_notifications)
            }, status=201 if created_notifications else 400)
            
        return Response({
            "message": f"通知发送成功，共发送{len(created_notifications)}条",
            "notifications": created_notifications
        }, status=201)
        
    @action(detail=False, methods=['delete'], url_path='delete-read', permission_classes=[CanSendNotification])
    def delete_read_notifications(self, request):
        """
        删除用户已读的通知
        """
        user = request.user
        # 检查用户是否为认证用户
        if not user.is_authenticated:
            return Response({"error": "用户未认证"}, status=401)
        
        # 只能删除自己的已读通知
        read_notifications = Notification.objects.filter(receiver=user, is_read=True)
        count = read_notifications.count()
        print(count)
        read_notifications.delete()
        return Response({
            "message": f"成功删除 {count} 条已读通知",
            "deleted_count": count
        }, status=200)
