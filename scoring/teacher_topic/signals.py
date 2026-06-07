from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from management.models import Topic  # 修改导入路径

@receiver(post_save, sender=Topic)
def update_question_count_on_save(sender, instance, **kwargs):
    if instance.Q_data:
        instance.Q_data.save()

@receiver(post_delete, sender=Topic)
def update_question_count_on_delete(sender, instance, **kwargs):
    if instance.Q_data:
        instance.Q_data.save()
