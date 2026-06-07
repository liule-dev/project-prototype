from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import QuestionViewSet, SubjectListView, GradeListView, UserLoginView, TopicViewSet, OperationRecordViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'topic', TopicViewSet, basename='topic')
router.register(r'api1/operation-records', OperationRecordViewSet)
urlpatterns = [
    path('', include('qd.urls')),
    path('', include(router.urls)),
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject-create'),
    path('subjects/<int:pk>/', views.SubjectDeleteView.as_view(), name='subject-delete'),
    path('grades/create/', views.GradeCreateView.as_view(), name='grade-create'),
    path('grades/<int:pk>/', views.GradeDeleteView.as_view(), name='grade-delete'),
    path('grades/', GradeListView.as_view(), name='grade_list'),
    # 修正登录路由配置
    path('auth/login/', UserLoginView.as_view(), name='login'),

]