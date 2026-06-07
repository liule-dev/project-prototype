# 创建了专门的视图 BatchMarkAsReadView，允许用户批量标记多个通知为已读。
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from management.models import Notification
from .permissions import IsSuperAdminOrReadOnly, IsReceiverOrAdmin
from .notification_constants import NotificationType

@api_view(['POST'])
@permission_classes([IsSuperAdminOrReadOnly, IsReceiverOrAdmin])
def mark_notifications_as_read(request):
    """
    批量标记通知为已读
    - 支持超级管理员和接收者用户操作
    - 可以指定特定的通知ID列表，或标记所有未读通知
    """
    user = request.user
    
    # 获取请求数据
    data = request.data
    notification_ids = data.get('notification_ids')  # 指定的通知ID列表
    
    if notification_ids:
        # 如果指定了通知ID列表，只更新这些通知
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            receiver=user,
            is_read=False
        )
    else:
        # 如果没有指定ID列表，标记所有未读通知为已读
        notifications = Notification.objects.filter(
            receiver=user,
            is_read=False
        )
    
    # 更新通知状态
    count = notifications.update(is_read=True)
    
    # 返回成功响应
    return Response({
        'success': True,
        'count': count,
        'message': f'成功标记 {count} 条通知为已读'
    }, status=status.HTTP_200_OK)

