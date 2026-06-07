import datetime
import json
import random



from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin import action
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views import View
from rest_framework import viewsets,status,permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from management.models import User, Class, Specialty, Grade, ClassName
from qd.serializer import UserSerializer, ClassSerializer, SpecialtySerializer, GradeSerializer, ClassNameSerializer
import random
import requests
import uuid
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.conf import settings
from management.models import User  # 导入自定义用户模型
import requests
import uuid
from django.shortcuts import redirect, HttpResponse
from django.contrib.auth import login
from django.conf import settings
from management.models import User  # 导入自定义用户模型
from .permission import StudentPermission, ManagePermission
from .utils import OperationLogger

e={0,}
@csrf_exempt
def email_verify(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        
        # 验证用户名和邮箱是否同时提供
        if username and email:
            # 查找用户
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({'error': '用户名不存在'}, status=status.HTTP_400_BAD_REQUEST)
            # 验证邮箱是否匹配
            if user.email != email:
                return JsonResponse({'error': '用户名和邮箱不匹配'}, status=status.HTTP_400_BAD_REQUEST)
            # 使用用户的邮箱
            email = user.email
        elif username and not email:
            # 只提供用户名，查找邮箱
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({'error': '用户名不存在'}, status=status.HTTP_400_BAD_REQUEST)
            if not user.email:
                return JsonResponse({'error': '该用户未设置邮箱，无法发送验证码'}, status=status.HTTP_400_BAD_REQUEST)
            email = user.email
        elif email and not username:
            # 只提供邮箱，验证邮箱是否存在
            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'error': '该邮箱未注册'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error': '请提供用户名或邮箱'}, status=status.HTTP_400_BAD_REQUEST)
        
        random_code=0
        t=1
        while t:
            try:
                while random_code in e:
                    random_code = random.randint(100000,999999)
                e.add(random_code)
                t=0
            except:
                t=1
        try:
            send_mail(
                subject='邮箱验证',
                message=f'题库系统验证码为：{random_code}',
                from_email='794926067@qq.com',
                recipient_list=[email]
            )
            print(random_code)
            print(email)
            return JsonResponse({'message': '邮件发送成功，请查收'},status=status.HTTP_200_OK)
        except Exception as e1:
            return JsonResponse({'message': '邮件发送失败'+e1.args[0]},status=status.HTTP_400_BAD_REQUEST)




def quickauth_wechat_login(request):
    """生成QuickAuth授权链接，引导用户跳转"""
    state = str(uuid.uuid4())
    request.session['quickauth_state'] = state  # 用于防止CSRF攻击

    params = {
        "type": "wechat",  # 固定参数，指定微信登录
        "appkey": settings.QUICKAUTH_APPID,  # 对应目标链接的 appkey，用配置的 AppID 赋值
        "state": state,  # 与目标链接一致，或用随机值
        "redirect": settings.QUICKAUTH_REDIRECT_URI # 回调地址（目标链接没显式带，但授权后需跳转，必须加）
    }

    # 3. 生成最终授权链接（用 requests 工具自动编码特殊字符，避免空格/中文问题）
    auth_url = f"{settings.QUICKAUTH_AUTH_URL}?{requests.compat.urlencode(params)}"
    print("最终授权链接：",
          auth_url)  # 打印到终端，确认格式是否为 https://api.qauth.cn/oauth?type=wechat&appkey=e0176d4b&state=login&redirect_uri=xxx
    return redirect(auth_url)

def quickauth_callback(request):
    """处理QuickAuth回调，获取用户信息并登录或注册"""
    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.session.get('quickauth_state')

    if not code or not state or state != session_state:
        return HttpResponse("授权失败，请求参数无效")

    # 换取access_token
    token_params = {
        "appid": settings.QUICKAUTH_APPID,
        "secret": settings.QUICKAUTH_APPSECRET or settings.QUICKAUTH_APPID,  # 若未获取到Secret，可尝试用AppID代替
        "code": code,
        "grant_type": "authorization_code"
    }

    try:
        token_response = requests.get(settings.QUICKAUTH_TOKEN_URL, params=token_params, timeout=10)
        token_data = token_response.json()

        if "access_token" not in token_data:
            return HttpResponse(f"获取token失败：{token_data.get('errmsg', '未知错误')}")

        # 获取用户信息
        userinfo_params = {
            "access_token": token_data["access_token"],
            # 按照QuickAuth文档要求，补充其他必要参数，如openid等
        }

        userinfo_response = requests.get(settings.QUICKAUTH_USERINFO_URL, params=userinfo_params, timeout=10)
        userinfo_data = userinfo_response.json()

        if "uid" not in userinfo_data:
            return HttpResponse(f"获取用户信息失败：{userinfo_data.get('errmsg', '未知错误')}")

        # 关联/创建Django用户
        user_unique_id = userinfo_data["uid"]

        try:
            user = User.objects.get(quickauth_uid=user_unique_id)
        except User.DoesNotExist:
            username = f"wechat_{user_unique_id[:10]}"  # 生成唯一用户名
            user = User.objects.create_user(
                username=username,
                quickauth_uid=user_unique_id,
                wechat_nickname=userinfo_data.get("nickname", "微信用户"),
                wechat_avatar=userinfo_data.get("avatar", "")
            )
        # 登录用户
        login(request, user)
        return redirect("/")  # 登录成功后，跳转至首页

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"网络请求错误：{str(e)}")
    except Exception as e:
        return HttpResponse(f"服务器错误：{str(e)}")
@csrf_exempt
def logout_view(request):

    """注销登录"""
    try:
        # # 记录操作日志
        # date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #
        # users = User.objects.filter(id=request.user.id).first()
        #
        # OperationLogger.log_operation(
        #     user=users,
        #     operation_type=OperationLogger.OTHER,
        #     content=f"管理员添加账户，用户ID:{users.id}，身份：{users.role}用户名:{users.username}，注册时间:{date}"
        # )
        logout(request)
        return JsonResponse({'message': '成功注销登录'}, status=status.HTTP_200_OK)
    except Exception as exc:
        return JsonResponse({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class QueryAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    @action(detail=False, methods=['POST'])
    def query_user(self, request):
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if user is not None:
            serializer = UserSerializer(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(detail=False, methods=['GET'])
    def query_class(self, request):
        if request.method == 'GET':
            queryset = Class.objects.all()
            serializer1 = ClassSerializer(queryset, many=True)
            return JsonResponse(serializer1.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '请求方式错误'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(detail=False, methods=['GET'])
    def query_classname(self, request):
        if request.method == 'GET':
            queryset = ClassName.objects.all()
            serializer = ClassNameSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '请求方式错误'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(detail=False, methods=['GET'])
    def query_grade(self, request):
        if request.method == 'GET':
            queryset = Grade.objects.all()
            serializer = GradeSerializer(queryset, many=True)
            return JsonResponse(serializer.data,  safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '请求方式错误'}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @action(detail=False, methods=['GET'])
    def query_specialty(self, request):
        if request.method == 'GET':
            queryset = Specialty.objects.all()
            serializer = SpecialtySerializer(queryset, many=True)
            return JsonResponse(serializer.data,  safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '请求方式错误'}, status=status.HTTP_400_BAD_REQUEST)


class StudentAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['POST'])
    def user_update(self, request):
        data = json.loads(request.body)
        user = User.objects.filter(username=request.data.get('username')).first()
        user.email = data.get('email')
        user.phone = data.get('phone')
        class1 = data.get('class')
        grade1 = data.get('grade')
        specialty1 = data.get('specialty')

        # 构建查询条件
        query = Q()
        if class1:
            query &= Q(class1_id=class1)
            print(1)
        else:
            query &= Q(class1_id__isnull=True)
            print(2)

        if grade1:
            query &= Q(grade1_id=grade1)
            print(3)
        else:
            query &= Q(grade1_id__isnull=True)
            print(4)

        if specialty1:
            query &= Q(specialty1_id=specialty1)
            print(5)
        else:
            query &= Q(specialty1_id__isnull=True)
            print(6)

        # 执行查询并处理结果
        class_obj = Class.objects.filter(query).first()
        if class_obj:
            class_id = class_obj.id
        else:
            class_id = None  # 如果找不到匹配的班级，则设为 None

        user.class1_id = class_id
        user2 = User.objects.filter(email=user.email).exclude(username=user.username).first()
        user3 = User.objects.filter(phone=user.phone).exclude(username=user.username).first()

        if user2 is None and user3 is None:
            # 记录操作日志
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            users = User.objects.filter(id=request.user.id).first()
            OperationLogger.log_operation(
                user=users,
                operation_type=OperationLogger.OTHER,
                content=f"用户更改自己账户信息，用户ID:{users.id}，身份：{users.role}用户名:{users.username}，注册时间:{date}"
            )
            user.save()
            return JsonResponse({'message': '成功'}, status=status.HTTP_200_OK)

        return JsonResponse({'error': '用户名或邮箱或手机号已存在'}, status=status.HTTP_400_BAD_REQUEST)


class ManageAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [ManagePermission]

    @action(detail=False, methods=['GET'])
    def query_all_user(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'])
    def add_user(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            role = data.get('role')
            email = data.get('email')
            phone = data.get('phone')
            class1 = data.get('class')
            grade1 = data.get('grade')
            specialty1 = data.get('specialty')

            # 构建查询条件
            query = Q()
            if class1:
                query &= Q(class1_id=class1)
                print(1)
            else:
                query &= Q(class1_id__isnull=True)
                print(2)

            if grade1:
                query &= Q(grade1_id=grade1)
                print(3)
            else:
                query &= Q(grade1_id__isnull=True)
                print(4)

            if specialty1:
                query &= Q(specialty1_id=specialty1)
                print(5)
            else:
                query &= Q(specialty1_id__isnull=True)
                print(6)

            # 执行查询并处理结果
            class_obj = Class.objects.filter(query).first()
            if class_obj:
                class_id = class_obj.id
            else:
                class_id = None  # 如果找不到匹配的班级，则设为 None

            # 检查用户是否已存在
            user1 = User.objects.filter(username=username).first()
            user2 = User.objects.filter(email=email).first()
            user3 = User.objects.filter(phone=phone).first()

            if user1 is None and user2 is None and user3 is None:
                # 创建新用户
                User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    phone=phone,
                    class1_id=class_id,
                    role=role
                )

                # 记录操作日志
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                users = User.objects.filter(id=request.user.id).first()
                OperationLogger.log_operation(
                    user=users,
                    operation_type=OperationLogger.OTHER,
                    content=f"管理员添加账户，用户ID:{users.id}，身份：{users.role}用户名:{users.username}，注册时间:{date}"
                )

                return JsonResponse({'message': '成功'}, status=status.HTTP_200_OK)

            return JsonResponse({'error': '用户名或邮箱或手机号已存在'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def update_user(self, request):
        data = json.loads(request.body)
        user = User.objects.filter(id=request.data.get('id')).first()
        user.username = data.get('username')
        if data.get('password') != '':
            user.set_password(raw_password=data.get('password'))
        user.email = data.get('email')
        user.phone = data.get('phone')
        user.role = data.get('role')

        class1 = data.get('class')
        grade1 = data.get('grade')
        specialty1 = data.get('specialty')

        query = Q()

        # 允许 class1 为空
        if class1:
            query &= Q(class1_id=class1)
            print(1)
        else:
            query &= Q(class1_id__isnull=True)
            print(2)

        # 允许 grade1 为空
        if grade1:
            query &= Q(grade1_id=grade1)
            print(3)
        else:
            query &= Q(grade1_id__isnull=True)
            print(4)

        # 允许 specialty1 为空
        if specialty1:
            query &= Q(specialty1_id=specialty1)
            print(5)
        else:
            query &= Q(specialty1_id__isnull=True)
            print(6)

        # 执行查询并处理结果
        class_obj = Class.objects.filter(query).first()
        if class_obj:
            class_id = class_obj.id
        else:
            class_id = None  # 如果找不到匹配的班级，则设为 None

        user.class1_id = class_id
        user1 = User.objects.filter(username=user.username).exclude(id=user.id).first()
        user2 = User.objects.filter(email=user.email).exclude(id=user.id).first()
        user3 = User.objects.filter(phone=user.phone).exclude(id=user.id).first()

        if user1 is None and user2 is None and user3 is None:
            # 记录操作日志
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            users = User.objects.filter(id=request.user.id).first()
            OperationLogger.log_operation(
                user=users,
                operation_type=OperationLogger.OTHER,
                content=f"管理员更改账户信息，用户ID:{users.id}，身份：{users.role}用户名:{users.username}，注册时间:{date}"
            )
            user.save()
            return JsonResponse({'message': '成功'}, status=status.HTTP_200_OK)
        return JsonResponse({'error': '用户名或邮箱或手机号已存在'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def delete_user(self, request):
        user_id = request.data.get('id')
        user = User.objects.filter(id=user_id).first()
        if user is not None:

            # 记录操作日志
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            users = User.objects.filter(id=request.user.id)[0]
            OperationLogger.log_operation(
                user=users,
                operation_type=OperationLogger.OTHER,
                content=f"管理员删除用户，用户ID:{users.id}，身份：{users.role}用户名:{users.username}，注册时间:{date}"
            )
            user.delete()
            return JsonResponse({'message': '成功'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)
    #
    # @action(detail=False, methods=['POST'])
    # def manage_register(self, request, *args, **kwargs):
    #     username = request.data.get('username')
    #     password = request.data.get('password')
    #     email = request.data.get('email')
    #     is_active = request.data.get('is_active')
    #     role = request.data.get('role')
    #
    #     class1 = request.data.get('class')
    #     grade1 = request.data.get('grade')
    #     specialty1 = request.data.get('specialty')
    #     class_id = Class.objects.filter(class1_id=class1, grade1_id=grade1, specialty1_id=specialty1).first().id
    #     user = User.objects.create_user(username=username, password=password, email=email, role=role,
    #                                     is_active=is_active, class1_id=class_id)
    #     if user is not None:
    #
    #         date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         OperationLogger.log_operation(
    #             user=user,
    #             operation_type=OperationLogger.OTHER,
    #             content=f"管理员注册账户，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，注册时间:{date}"
    #         )
    #         return JsonResponse({'message': '注册成功'}, status=status.HTTP_200_OK)
    #     else:
    #         return JsonResponse({'message': '注册失败'}, status=status.HTTP_400_BAD_REQUEST)


# Create your views-wrong here.
class LoginApi(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 添加这行，允许任何人访问这个视图集

    @action(detail=False, methods=['POST'])
    def login1(self,request):
        if request.method == 'POST':
            logout(request)
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request=request, user=user)
                    user = request.user

                    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    retoken = RefreshToken.for_user(user)
                    if user.role == 'teacher':
                        OperationLogger.log_operation(
                            user=user,
                            operation_type=OperationLogger.OTHER,
                            content=f"教师登录系统，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，登录时间:{date}"
                        )
                        return JsonResponse({'refresh': str(retoken),'access':str(retoken.access_token),'role':'teacher','username':user.username,'id':user.id},status=status.HTTP_200_OK)
                    elif user.role == 'student':
                        OperationLogger.log_operation(
                            user=user,
                            operation_type=OperationLogger.OTHER,
                            content=f"用户登录系统，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，登录时间:{date}"
                        )
                        return JsonResponse({'refresh': str(retoken),'access':str(retoken.access_token),'role':'student','username':user.username,'id':user.id},status=status.HTTP_200_OK)
                    elif user.role == 'admin':
                        OperationLogger.log_operation(
                            user=user,
                            operation_type=OperationLogger.OTHER,
                            content=f"管理员登录系统，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，登录时间:{date}"
                        )
                        return JsonResponse({'refresh': str(retoken),'access':str(retoken.access_token),'role':'admin','username':user.username,'id':user.id},status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'error': '账号'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': '用户名或密码错误'},status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['POST'])
    def register1(self,request, *args, **kwargs):
        code = int(request.data.get('code'))
        if code in e and code != '':
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            user1 = User.objects.filter(username=username).first()
            user2 = User.objects.filter(email=email).first()
            if user1 is None and user2 is None:
                if User.objects.filter(username=username).exists():
                    return JsonResponse({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.create_user(username=username, password=password, email=email, role='student',
                                                class1_id=None)
                if user is not None:
                    e.remove(code)
                    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    OperationLogger.log_operation(
                        user=user,
                        operation_type=OperationLogger.OTHER,
                        content=f"普通用户注册账户，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，注册时间:{date}"
                    )
                    return JsonResponse({'message': '注册成功'}, status=status.HTTP_200_OK)
                else:
                    return JsonResponse({'message': '注册失败'}, status=status.HTTP_200_OK)
            return JsonResponse({'message': '用户名或邮箱已存在'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': '验证码错误'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def reset_password(self, request, *args, **kwargs):
        """重置密码接口"""
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            verify_code_str = request.data.get('verifyCode')
            new_password = request.data.get('newPassword')

            # 验证参数
            if not username or not email or not verify_code_str or not new_password:
                return JsonResponse({'error': '参数不完整'}, status=status.HTTP_400_BAD_REQUEST)

            # 转换验证码为整数
            try:
                verify_code = int(verify_code_str)
            except (ValueError, TypeError):
                return JsonResponse({'error': '验证码格式错误'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证验证码
            if verify_code not in e:
                return JsonResponse({'error': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)

            # 查找用户（根据用户名）
            user = User.objects.filter(username=username).first()
            if not user:
                return JsonResponse({'error': '用户名不存在'}, status=status.HTTP_400_BAD_REQUEST)

            # 验证邮箱是否匹配
            if user.email != email:
                return JsonResponse({'error': '用户名和邮箱不匹配'}, status=status.HTTP_400_BAD_REQUEST)

            # 更新密码
            user.set_password(new_password)
            user.save()

            # 移除已使用的验证码
            e.remove(verify_code)

            # 记录操作日志
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            OperationLogger.log_operation(
                user=user,
                operation_type=OperationLogger.OTHER,
                content=f"用户重置密码，用户ID:{user.id}，身份：{user.role}用户名:{user.username}，操作时间:{date}"
            )

            return JsonResponse({'message': '密码重置成功，请使用新密码登录'}, status=status.HTTP_200_OK)

        except Exception as exc:
            return JsonResponse({'error': f'重置失败: {str(exc)}'}, status=status.HTTP_400_BAD_REQUEST)