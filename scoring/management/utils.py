from django.utils import timezone
from management.models import OperationRecord


class OperationLogger:
    """操作日志记录工具类"""

    # 操作类型常量
    QUESTION_BANK = '题库管理'
    EXAM_CREATION = '考试创建'
    ANSWER_SUBMISSION = '答题提交'
    GRADING = '评分'
    OTHER = '其他'

    OPERATION_TYPES = [
        QUESTION_BANK,
        EXAM_CREATION,
        ANSWER_SUBMISSION,
        GRADING,
        OTHER
    ]

    @staticmethod
    def log_operation(user, operation_type, content):
        """
        记录操作日志

        Args:
            user: 操作用户对象
            operation_type: 操作类型
            content: 操作内容描述

        Returns:
            新建的OperationRecord对象
        """
        if operation_type not in OperationLogger.OPERATION_TYPES:
            raise ValueError(f"不支持的操作类型: {operation_type}")

        return OperationRecord.objects.create(
            user=user,
            operation_type=operation_type,
            content=content,
            operation_time=timezone.now()
        )

    @staticmethod
    def log_question_bank_operation(user, content):
        """
        记录题库管理操作日志
        
        Args:
            user: 操作用户对象
            content: 操作内容描述
            
        Returns:
            新建的OperationRecord对象
        """
        return OperationLogger.log_operation(user, OperationLogger.QUESTION_BANK, content)

    @staticmethod
    def log_exam_creation_operation(user, content):
        """
        记录考试创建操作日志
        
        Args:
            user: 操作用户对象
            content: 操作内容描述
            
        Returns:
            新建的OperationRecord对象
        """
        return OperationLogger.log_operation(user, OperationLogger.EXAM_CREATION, content)

    @staticmethod
    def log_answer_submission_operation(user, content):
        """
        记录答题提交操作日志
        
        Args:
            user: 操作用户对象
            content: 操作内容描述
            
        Returns:
            新建的OperationRecord对象
        """
        return OperationLogger.log_operation(user, OperationLogger.ANSWER_SUBMISSION, content)

    @staticmethod
    def log_grading_operation(user, content):
        """
        记录评分操作日志
        
        Args:
            user: 操作用户对象
            content: 操作内容描述
            
        Returns:
            新建的OperationRecord对象
        """
        return OperationLogger.log_operation(user, OperationLogger.GRADING, content)