# permissions.py
from rest_framework.permissions import BasePermission
from .notification_constants import NotificationType

class IsSuperAdminOrReadOnly(BasePermission):
    """
    权限类：超级管理员或只读权限
    - 超级管理员有全部权限
    - 其他用户在只读操作时允许访问
    """
    def has_permission(self, request, view):
        # 如果是安全方法（GET、HEAD、OPTIONS）或超级管理员，允许访问
        if request.method in ["GET", "HEAD", "OPTIONS"] or request.user.role == 'admin':
            return True
        return False

class IsReceiverOrAdmin(BasePermission):
    """
    权限类：接收者或管理员访问
    - 接收者用户可以访问
    - 管理员用户也可以访问
    """
    def has_permission(self, request, view):
        # 对于列表视图，允许认证用户访问
        # 检查是否为函数视图
        if hasattr(view, 'action') and view.action == 'send_to_user':
            # send_to_user 需要特殊权限处理
            return request.user.role == 'admin'
        # 对于函数视图，直接返回用户是否已认证
        elif not hasattr(view, 'action'):
            return request.user.is_authenticated
        
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 超级管理员有权操作所有通知
        if request.user.role == 'admin':
            return True
        
        # 对于删除已读通知的操作，允许用户删除自己已读的通知
        if hasattr(view, 'action') and view.action == 'delete_read_notifications':
            # 这是批量删除操作，我们在视图中检查权限
            return True
        
        # 普通用户只能访问自己接收的通知
        return obj.receiver == request.user

class CanSendNotification(BasePermission):
    """
    权限类：根据用户角色控制发送通知的权限
    - 管理员可以发送所有类型的通知
    - 教师可以发送特定类型的通知
    - 学生不能发送通知
    """
    
    # 各角色可以发送的通知类型
    ALLOWED_TYPES_BY_ROLE = {
        'admin': NotificationType.TYPES,  # 管理员可以发送所有类型的通知
        'teacher': [
            NotificationType.EXAM_NOTIFICATION,
            NotificationType.GRADE_NOTIFICATION,
            NotificationType.QUESTION_REVIEW_NOTIFICATION,
            NotificationType.LEARNING_PLAN_RECOMMENDATION_NOTIFICATION
        ],
        'student': [
            NotificationType.QUESTION_REVIEW_NOTIFICATION
        ]  # 学生可以发送题目审核通知
    }
    
    def has_permission(self, request, view):
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            return False
            
        # 只有send_to_user操作需要检查此权限
        if hasattr(view, 'action') and view.action == 'send_to_user':
            user_role = getattr(request.user, 'role', 'student')  # 默认为学生
            # 管理员和教师可以发送通知
            # 学生也可以发送通知给教师
            return user_role in ['admin', 'teacher', 'student']
            
        return True
    
    def has_object_permission(self, request, view, obj):
        # 对象级别的权限检查
        if request.user.role == 'admin':
            return True
            
        user_role = getattr(request.user, 'role', 'student')
        notification_type = obj.type
        
        # 检查用户角色是否允许发送该类型的通知
        allowed_types = self.ALLOWED_TYPES_BY_ROLE.get(user_role, [])
        return notification_type in allowed_types