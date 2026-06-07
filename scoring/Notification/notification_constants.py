class NotificationType:
    """通知类型常量类"""
    # 考试通知
    EXAM_NOTIFICATION = '考试通知'
    # 成绩通知
    GRADE_NOTIFICATION = '成绩通知'
    # 题目审核通知
    QUESTION_REVIEW_NOTIFICATION = '题目审核通知'
    # 系统公告通知
    SYSTEM_ANNOUNCEMENT_NOTIFICATION = '系统公告通知'
    # 错题本更新通知
    WRONG_BOOK_UPDATE_NOTIFICATION = '错题本更新通知'
    # 学习计划推荐通知
    LEARNING_PLAN_RECOMMENDATION_NOTIFICATION = '学习计划推荐通知'
    
    # 通知类型列表
    TYPES = [
        EXAM_NOTIFICATION,
        GRADE_NOTIFICATION,
        QUESTION_REVIEW_NOTIFICATION,
        SYSTEM_ANNOUNCEMENT_NOTIFICATION,
        WRONG_BOOK_UPDATE_NOTIFICATION,
        LEARNING_PLAN_RECOMMENDATION_NOTIFICATION
    ]
    
    @staticmethod
    def is_valid_type(type_code):
        """检查通知类型是否有效"""
        return type_code in NotificationType.TYPES
    
    @staticmethod
    def get_all_types():
        """获取所有通知类型"""
        return NotificationType.TYPES
    
    @staticmethod
    def get_type_choices():
        """获取通知类型选择项"""
        return [
            (NotificationType.EXAM_NOTIFICATION, NotificationType.EXAM_NOTIFICATION),
            (NotificationType.GRADE_NOTIFICATION, NotificationType.GRADE_NOTIFICATION),
            (NotificationType.QUESTION_REVIEW_NOTIFICATION, NotificationType.QUESTION_REVIEW_NOTIFICATION),
            (NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION, NotificationType.SYSTEM_ANNOUNCEMENT_NOTIFICATION),
            (NotificationType.WRONG_BOOK_UPDATE_NOTIFICATION, NotificationType.WRONG_BOOK_UPDATE_NOTIFICATION),
            (NotificationType.LEARNING_PLAN_RECOMMENDATION_NOTIFICATION, NotificationType.LEARNING_PLAN_RECOMMENDATION_NOTIFICATION)
        ]
    
    @staticmethod
    def get_type_display_name(type_code):
        """获取通知类型的显示名称"""
        return type_code  # 由于值本身就是中文显示名称，直接返回
    
    @staticmethod
    def get_type_by_display_name(display_name):
        """根据显示名称获取通知类型代码"""
        # 由于值本身就是中文显示名称，直接返回
        if display_name in NotificationType.TYPES:
            return display_name
        return None

# 各类通知的内容示例（实际使用时可根据具体情况动态生成）
exam_notification_content = "您有一场新的考试即将开始，请按时参加。考试名称：{exam_name}，开始时间：{start_time}，时长：{duration}分钟。"
grade_notification_content = "您的考试成绩已发布，点击查看详情。考试名称：{exam_name}，您的成绩为：{score}。"
question_review_notification_content = "您提交审核的题目已完成审核，审核结果为：{review_result}。题目详情：{question_detail}。"
system_announcement_notification_content = "系统发布重要公告：{announcement_content}。请您知悉并留意相关信息。"
wrong_book_update_notification_content = "您的错题本已更新，新增错题数量：{new_wrong_count}。快去复习巩固吧！"
learning_plan_recommendation_notification_content = "为您推荐个性化学习计划：{learning_plan_detail}。希望对您的学习有所帮助！"