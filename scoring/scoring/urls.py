"""
URL configuration for scoring project.

The `urlpatterns` list routes URLs to views-wrong. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views-wrong
    1. Add an import:  from my_app import views-wrong
    2. Add a URL to urlpatterns:  path('', views-wrong.home, name='home')
Class-based views-wrong
    1. Add an import:  from other_app.views-wrong import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from management.views import ClassViewSet, StudentViewSet, ExamViewSet, PaperViewSet, ReportViewSet, obtain_auth_token, current_user
from management.export_views import export_report_view
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# 创建一个简单的测试视图
def test_view(request):
    return HttpResponse("Test view works!")

# 创建一个简单的DRF测试视图
@api_view(['GET'])
def drf_test_view(request):
    return Response({"message": "DRF test view works!"})

# 创建一个简单的导出测试视图
@api_view(['GET'])
@permission_classes([AllowAny])
def export_test_view(request):
    from django.http import HttpResponse
    response = HttpResponse(b"Test export content", content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="test_export.xlsx"'
    return response

# 创建 router 并注册 ViewSet
router = DefaultRouter()
router.register(r'classes', ClassViewSet)
router.register(r'students', StudentViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'papers', PaperViewSet)
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api1/', include(router.urls)),
    path('', include('Notification.urls')),
    path('', include('teacher_topic.urls')),
    path('', include('notebook.urls')),
    path('', include('exam.urls')),

    path('', include('qd.urls')),  # 添加这行来包含qd应用的URLs
    path('api1/api1-token-auth/', obtain_auth_token),
    path('api1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api1/users/current/', current_user),
    path('api1/export-report/', export_report_view),
    path('api1/test/', test_view),
    path('api1/drf-test/', drf_test_view),
    path('api1/export-test/', export_test_view),
    path('', include('teacher_topic.urls')),
    path('api11/token/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新令牌
    path("api11/", include("Notification.urls", namespace="Notification")),  # 引入通知模块路由

]