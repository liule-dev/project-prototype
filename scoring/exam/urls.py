# DjangoProject4/urls.py
# DjangoProject4/urls.py
"""
URL configuration for DjangoProject4 project.

The urlpatterns list routes URLs to viewshu. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function viewshu
    1. Add an import:  from my_app import viewshu
    2. Add a URL to urlpatterns:  path('', viewshu.home, name='home')
Class-based viewshu
    1. Add an import:  from other_app.viewshu import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from exam import views

urlpatterns = [
    # 考试创建相关
    path("api/create_exam/", views.create_exam, name="create_exam"),
    path("api/ai_generate_exam/", views.ai_generate_exam, name="ai_generate_exam"),

    # 考试管理相关
    path("api/exam/<int:exam_paper_id>/", views.exam_detail_view, name="exam_detail"),
    path("api/exam/<int:exam_paper_id>/topics/", views.get_exam_topics, name="get_exam_topics"),
    path("api/user/<int:user_id>/", views.get_user_info, name="get_user_info"),
    path("api/user/<int:user_id>/scores/", views.get_user_scores, name="get_user_scores"),
    # 考试发布相关
    path("api/publish_exam/", views.publish_exam, name="publish_exam"),
    path("api/user/<int:user_id>/exam/<int:exam_paper_id>/answers/", views.get_user_exam_answers, name="get_user_exam_answers"),

    # 考试参与相关
    path("api/start_exam/", views.start_exam, name="start_exam"),
    path("api/save_progress/", views.save_progress, name="save_progress"),
    path("api/submit_exam/", views.submit_exam, name="submit_exam"),

    # 成绩相关
    path("api/generate_score_report/", views.generate_score_report, name="generate_score_report"),

    # 查询相关
    path("api/exam_participation/<int:user_id>/<int:exam_paper_id>/", views.get_user_exam_participation, name="get_user_exam_participation"),
    path("api/published_exams/", views.get_published_exams, name="get_published_exams"),
    path("api/user_exams/<int:user_id>/", views.get_user_available_exams, name="get_user_available_exams"),
    path("api/subjects/", views.get_subjects, name="get_subjects"),
    path("api/subject/<int:subject_id>/detail/", views.get_subject_detail, name="get_subject_detail"),
]
