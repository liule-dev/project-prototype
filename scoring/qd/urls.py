from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from qd.views import LoginApi, quickauth_callback, quickauth_wechat_login, QueryAPI, email_verify, \
    logout_view, ManageAPI, StudentAPI

router = routers.DefaultRouter()
router.register('login',LoginApi,basename='login')
router.register('query',QueryAPI,basename='query')
router.register('manage',ManageAPI,basename='update')
router.register('student',StudentAPI,basename='manage_add')
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('quickauth/callback/', quickauth_callback, name='quickauth_callback'),
    path('quickauth_wechat_login', quickauth_wechat_login, name='quickauth_wechat_login'),
    path('send_code/',email_verify,name='send_code'),
    path('logout/',logout_view,name='logout')
]
urlpatterns += router.urls