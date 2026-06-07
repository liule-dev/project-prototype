from django.urls import path
from . import views

urlpatterns = [
    # 错题相关接口
    path('api/wrong-topics/add/', views.add_wrong_topic, name='add_wrong_topic'),
    path('api/wrong-topics/user/<int:user_id>/', views.get_wrong_topics, name='get_wrong_topics'),
    path('api/wrong-topics/update/<int:wrong_topic_id>/', views.update_wrong_topic_status,
         name='update_wrong_topic_status'),

    # 练习记录相关接口
    path('api/contact-records/add/', views.add_contact_record, name='add_contact_record'),
    path('api/contact-records/user/<int:user_id>/', views.get_contact_records, name='get_contact_records'),

    # 复习记录相关接口
    path('api/review-records/add/', views.add_review_record, name='add_review_record'),
    path('api/review-records/user/<int:user_id>/', views.get_review_records, name='get_review_records'),

    # AI 助手功能
    path('api/ai/study-plan/', views.generate_study_plan_api, name='generate_study_plan'),
    path('api/ai/analyze-wrong-topics/<int:user_id>/', views.analyze_wrong_topics_api, name='analyze_wrong_topics'),
    path('api/ai/chat/', views.chat_with_ai, name='chat_with_ai'),
]

