import uuid

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
# from django.utils.decorators import method_decorator
from django.views import View

from db.base_view import BaseVerifyView
from sp_user.forms import RegisterForm, LoginForm
from sp_user.helper import verify_login_required, send_sms
from sp_user.models import Users


class RegisterView(View):
	# 注册功能
	def get(self, request):
		# 使用form渲染页面
		form = RegisterForm()
		return render(request, "sp_user/reg.html", {"form": form})

	def post(self, request):
		# 1. 接收数据
		session_code = request.session.get('random_code')  # 提取出验证码
		# 2. 处理数据
		data = request.POST.dict()
		data['session_code'] = session_code  # 强制转换成字典
		form = RegisterForm(data)
		# 3. 响应
		if form.is_valid():
			form.save()  # 全部合法上传数据库
			return redirect(reverse("sp_user:login"))  # 注册成功跳转到登录页面
		return render(request, "sp_user/reg.html", {"form": form})  # 注册失败跳转注册页面,提示错误信息


# 登录功能
class LoginView(View):
	def get(self, request):
		login_form = LoginForm()
		return render(request, "sp_user/login.html", {"form": login_form})

	def post(self, request):
		# 1.接收数据
		# 2.处理数据
		l_form = LoginForm(request.POST)
		# 3.响应
		# 如果验证成功保存到session中
		if l_form.is_valid():
			user = l_form.cleaned_data.get("user")  # 从cleaned_data中拿到user
			request.session['ID'] = user.pk  # 找到数据库中用户名id
			request.session['phone'] = user.phone  # 找到数据库中用户名手机号
			request.session.set_expiry(0)  # 有效期,在关闭浏览器失效，需要重登
			return redirect(reverse('sp_user:center'))  # 跳转用户中心
		return render(request, "sp_user/login.html", {"form": l_form})  # 验证失败,回到原来页面


# 个人中心功能
class CenterView(BaseVerifyView):
	def get(self, request):
		phone = request.session.get('phone')  # 通过session获取电话号码
		context = {
			"phone": phone
		}
		return render(request, "sp_user/member.html", context)

	def post(self, request):
		pass


# 收货地址功能
class AddressView(BaseVerifyView):
	def get(self, request):
		pass

	def post(self, request):
		pass


# 个人资料功能
class InfoView(BaseVerifyView):
	def get(self, request):
		user_id = request.session.get("ID")  # 从session中提取id
		# 查询当前用户的所有信息
		user = Users.objects.filter(pk=user_id).first()
		context = {
			"user": user
		}
		return render(request, "sp_user/infor.html", context)

	def post(self, request):
		# 1. 接收数据
		user_id = request.session.get("ID")
		data = request.POST
		file = request.FILES['head']
		# 2. 处理数据
		# 更新用户的头像
		user = Users.objects.get(pk=user_id)
		user.head = file
		user.save()
		# 3. 响应
		return redirect(reverse("sp_user:center"))


# 退出功能
class LogoutView(View):
	def get(self, request):
		pass

	def post(self, request):
		pass


# 验证码
class SendCodeView(View):
	def post(self, request):
		# 1.接收数据
		phone = request.POST.get("tel", "")  # 最好给个默认值
		# 2.处理数据
		import re
		phone_re = re.compile("^1[3-9]\d{9}$")  # re是正则,设置手机号的正则规则
		res = re.search(phone_re, phone)  # search查询手机号字符串(规则,对象)
		# 如果手机号码为空,格式错误
		if res is None:
			return JsonResponse({"status": "400", "msg": "手机号码格式错误"})
		# 若库中手机号存在
		res = Users.objects.filter(phone=phone).exists()
		if res:
			return JsonResponse({"status": "400", "msg": "手机号码已经注册"})

		# 生成随机验证码
		import random
		random_code = "".join([str(random.randint(0, 9)) for _ in range(4)])  #0~9随机生成4个

		# 开发自己模拟效果
		print("----code : {}----".format(random_code))
		# __business_id = uuid.uuid1()
		# params = "{\"code\":\"%s\"}" % random_code
		# rs = send_sms(__business_id, phone, "签名", "工单号", params)
		# print(rs)

		# 将生成的随机码也保存到session中,并且60秒过期
		request.session['random_code'] = random_code
		request.session.set_expiry(60)

		# 3.响应 json , 告知 ajax是否发送成功
		return JsonResponse({"status": "200"})
