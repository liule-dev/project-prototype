from django.apps import AppConfig


class TeacherTopicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teacher_topic'

    def ready(self):
        import teacher_topic.signals  # 添加这行来导入信号
