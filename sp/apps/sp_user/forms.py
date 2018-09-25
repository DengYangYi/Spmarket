from django import forms
from django.core import validators
from sp_user.helper import set_password
from sp_user.models import Users


# 新建form, 前台一个表单后台一个form类,它是不存在数据库内的
class RegisterForm(forms.ModelForm):
	repassword = forms.CharField(
		max_length=16,
		min_length=6,
		error_messages={'required': "请填写确认密码"},
		widget=forms.PasswordInput(
			attrs={"class": "login-password", "placeholder": "请输入确认密码"}),
	)
	verify_code = forms.CharField(
		required=True,
		error_messages={"required": "请填写验证码!"},
		widget=forms.TextInput(attrs={"class": "reg-yzm", "placeholder": "输入验证码"})
	)
	agree = forms.BooleanField(
		required=True,
		error_messages={"required": "必须同意用户协议"}
	)

	class Meta:
		model = Users
		fields = ['phone', 'password']
		# 样式
		widgets = {
			"phone": forms.TextInput(attrs={"class": "login-name", "placeholder": "请输入手机号码"}),
			"password": forms.PasswordInput(attrs={"class": "login-password", "placeholder": "请输入密码"}),
		}
		# 自定义错误信息
		error_messages = {
			"phone": {
				"required": "请填写手机号!"
			},
			"password": {
				"required": "请填写密码!",
				"min_length": "密码必须大于6个字符!",
				"max_length": "密码必须小于16个字符!",
			}
		}

	# 重写__init__,初始化方法
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)  # 调用父类方法
		# 自定义的验证 密码长度的验证 6-16 位
		self.fields['password'].validators.append(validators.MinLengthValidator(6))
		self.fields['password'].validators.append(validators.MaxLengthValidator(16))

	# 自定义单个验证手机号码是否已经被注册
	def clean_phone(self):
		phone = self.cleaned_data.get("phone")  # 提取传入的手机号码
		rs = Users.objects.filter(phone=phone).exists()  # 从数据库查询手机号码已存在
		if rs:
			raise forms.ValidationError("该手机号码已经被注册")  # 抛出异常
		return phone  # 返回清洗后的值

	# 验证码的验证
	def clean_verify_code(self):
		verify_code = self.cleaned_data.get('verify_code')  # 获取提交的验证码
		session_code = self.data.get('session_code')  # 获取数据中保存的session验证码
		if verify_code != session_code:  # 如果相等
			raise forms.ValidationError("验证码错误!")  # 抛出错误
		return verify_code  # 返回值

	# 综合验证
	def clean(self):
		cleaned_data = super().clean()  # 所有清洗后的数据
		pwd1 = cleaned_data.get('password')  # 获取密码
		pwd2 = cleaned_data.get('repassword')  # 获取确认密码
		if pwd1 and pwd2 and pwd1 != pwd2:  # 两次密码存在并且不相等
			raise forms.ValidationError({"repassword": "两次密码不一致!"})  # 抛出错误
		else:
			if pwd1:  # 避免为空
				cleaned_data['password'] = set_password(pwd1)  # 对密码进行加密
		return cleaned_data  # 返回所有清洗后的数据


# 登录页面的form
class LoginForm(forms.ModelForm):
	class Meta:
		model = Users
		fields = ['phone', 'password']
		# 表单样式
		widgets = {
			'phone': forms.TextInput(attrs={"class": "login-name", "placeholder": "请输入手机号"}),
			"password": forms.PasswordInput(attrs={"class": "login-password", "placeholder": "请输入密码"})
		}
		# 错误提示
		error_messages = {
			"phone": {
				"required": "请填写手机号",
			},
			"password": {
				"required": "请填写密码",
			}
		}

	# 综合校验，验证手机号码和密码是否正确
	def clean(self):
		c_data = super().clean()  # 获取所有数据
		phone = c_data.get('phone')  # 调出手机号码
		password = c_data.get('password', "")  # 调出密码
		user = Users.objects.filter(phone=phone).first()  # 通过手机号码查询数据
		# 手机号为空
		if user is None:
			raise forms.ValidationError({"phone": "该手机号码没有注册"})
		# 存在手机号, 验证密码
		else:
			p_in_db = user.password  # 提取数据库内加密了的密码
			password = set_password(password)
			if p_in_db != password:
				raise forms.ValidationError({"password": "密码错误!"})
			else:
				c_data['user'] = user
				return c_data  # 保存用户的信息对象到c_data后返回出去
