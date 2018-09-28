import random
import re
import uuid
from django.shortcuts import render, redirect, reverse
from django.views import View
from db.base_view import BaseVerifyView
from sp_user.forms import RegisterForm, LoginForm, UserChangeForm
from sp_user.helper import check_phone_pwd, check_is_login, send_sms
from sp_user.models import User
from django.http import HttpResponse, JsonResponse


class RegisterView(View):
    """
        # 注册
    """

    def get(self, request):
        # 创建注册表单对象
        register_form = RegisterForm()
        return render(request, "sp_user/reg.html", {"form": register_form})

    def post(self, request):
        # 先将session中的验证码取出来
        sid_verify_code = request.session.get('verify_code')
        # 将 session 中的验证码 装到 request.POST 里面
        data = request.POST.dict()
        data['sid_verify_code'] = sid_verify_code

        # 创建注册表单对象 验证验证码 交给form表单验证
        register_form = RegisterForm(data)
        # 判断是否验证成功
        if register_form.is_valid():
            # 成功
            register_form.save()
            # 跳转到登陆页面进行登陆
            return redirect(reverse('sp_user:login'))
        else:
            return render(request, "sp_user/reg.html", {"form": register_form})


# 登陆

class LoginView(View):
    def get(self, request):
        login_form = LoginForm()
        return render(request, "sp_user/login.html", {"form": login_form})

    def post(self, request):
        # 创建表单对象, 传入数据校验
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 数据验证成功 必须和数据库验证
            data = login_form.cleaned_data
            phone = data.get('phone')
            password = data.get('password')
            user = check_phone_pwd(phone, password)
            if user:
                # 验证成功 ,将用户登陆标识保存到session中
                request.session.clear()  # 清空上个用户的信息
                request.session['ID'] = user.pk
                request.session['phone'] = user.phone
                request.session.set_expiry(7 * 24 * 3600)

                # 判断请求参数中是否有next
                if request.GET.get("next"):
                    return redirect(request.GET.get("next"))
                else:
                    # 跳转到用户中心
                    return redirect(reverse("sp_user:center"))
            else:
                # 添加密码错误的信息
                login_form.errors['password'] = ['密码输入错误!']
        return render(request, "sp_user/login.html", {"form": login_form})


# 视图函数
# 调用 验证登陆的装饰器
@check_is_login
def center(request):
    return render(request, "sp_user/member.html")


# 个人中心 都需要验证是否曾经登陆
class CenterView(BaseVerifyView):

    def get(self, request):
        # # 判断session中是否有登陆标识 ID phone
        # if request.session.get('ID') is None:
        #     # 没有登陆 跳转到登陆页面
        #     return redirect(reverse('sp_user:login'))
        return render(request, "sp_user/member.html")

    def post(self, request):
        pass


# 修改个人资料
class InfoView(BaseVerifyView):
    def get(self, request):
        # 查询出个人信息
        # 获取人的id
        id = request.session.get('ID')
        # 查询数据库 orm
        user = User.objects.filter(pk=id).values().first()

        # 渲染到页面
        # 使用modelform
        user_change_form = UserChangeForm(user)
        return render(request, "sp_user/infor.html", {"form": user_change_form, "head": user['head']})

    # post 提交数据
    def post(self, request):
        # 需要修改当前登陆人这个对象
        user = User.objects.filter(pk=request.session.get("ID")).first()
        # form 保持数据的 需要传第二个参数 instance = 需要修改的实例对象
        user_change_form = UserChangeForm(request.POST, instance=user)
        if user_change_form.is_valid():
            user_change_form.save()
            return redirect(reverse('sp_user:center'))
        else:
            return render(request, "sp_user/infor.html", {"form": user_change_form})


def sendMsg(request):
    """
        发送验证码
        :param request:
        :return:
    """
    # 接收到手机号码
    tel = request.GET.get('phone', '0')
    # 验证号码格式是否正确
    r = re.compile('^1[3-9]\d{9}$')
    res = re.search(r, tel)
    # print(res)
    if res is None:
        return JsonResponse({"ok": 0, "msg": "手好号码格式错误!"})

    # 随机生成验证码
    code = random.randint(1000, 9999)
    # 保存到session中 ,等你验证的时候使用
    request.session['verify_code'] = code
    # 设置过期时间 redis
    request.session.set_expiry(60)
    print(code)
    print("==================================")
    # # 生成一个唯一的字符串
    __business_id = uuid.uuid1()
    # print(__business_id)
    # 模板中的变量
    # params = "{\"code\":\"%s\"}" % code
    # rs = send_sms(__business_id, tel, "刘海", "SMS_142095014", params)
    #
    # rs = rs.decode("utf-8")
    rs = {"Code": "OK"}

    if rs['Code'] == "OK":
        return JsonResponse({"ok": 1})
    else:
        return HttpResponse({"ok": 0, "msg": "短信发送失败"})
