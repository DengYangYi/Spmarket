from django import forms
from django.core import validators
from django.contrib.auth import authenticate
from sp_user.helper import set_password
from sp_user.models import User


# 注册表单
class RegisterForm(forms.ModelForm):
    # 重复密码
    repassword = forms.CharField(min_length=6,
                                 max_length=16,
                                 widget=forms.PasswordInput(attrs={'class': 'login-password', 'placeholder': '确认密码'}),
                                 error_messages={
                                     "required": ""
                                 }
                                 )

    # 是否同意用户协议 默认同意
    agree = forms.BooleanField(widget=forms.CheckboxInput,
                               initial=0,
                               error_messages={
                                   "required": "必须同意用户协议!"
                               })

    verify_code = forms.CharField(error_messages={"required": "请填写验证"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 验证手机号码格式是否正确
        self.fields['phone'].validators.append(validators.RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!"))
        # 密码 在form中要求 6-16 个
        self.fields['password'].validators.append(validators.MinLengthValidator(6))
        self.fields['password'].validators.append(validators.MaxLengthValidator(16))

    class Meta:
        model = User
        # 注册只验证手机和密码
        fields = ['phone', 'password']
        # 错误信息提示
        error_messages = {
            'password': {
                'min_length': "密码长度至少6个字符!",
                'max_length': "密码长度不能大于16个字符!",
                'required': "请填写密码!",
            },
            "phone": {
                "required": "手机号码必须填写!",
            }
        }
        # form字段样式设置
        widgets = {
            "phone": forms.TextInput(attrs={'class': 'login-name', 'placeholder': '请输入手机号'}),
            "password": forms.PasswordInput(attrs={'class': 'login-password', 'placeholder': '请输入密码'}),
        }

    # 检测用户手机是否已经被注册
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        rs = User.objects.filter(phone=phone).exists()
        if rs:
            raise forms.ValidationError("该手机号码已经被注册!")
        return phone

    # 单独使用一个方法校验 验证码
    def clean_verify_code(self):
        # 表单传入的验证码
        verify_code = self.cleaned_data.get('verify_code')
        sid_verify_code = self.data.get('sid_verify_code')
        if int(verify_code) != sid_verify_code:
            raise forms.ValidationError("验证码输入有误")
        return verify_code



    # 综合校验
    def clean(self):
        # 获取所有清洗后的数据
        data = super(RegisterForm, self).clean()
        pwd1 = data.get('password')
        pwd2 = data.get('repassword')
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError({'repassword': '两次密码输入不一致!'})
        else:
            # 取密码
            if pwd1:
                # 如果密码不为空 进行加密
                data['password'] = set_password(pwd1)
        return data


# 登陆表单
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        # 只验证用户手机和密码
        fields = ['phone', 'password']
        # 错误信息
        error_messages = {
            'phone': {
                "required": "手机号码必填!",
            },
            "password": {
                "required": "请填写密码!",
                "min_length": "密码不得少于6个字符!",
                "max_length": "密码不得大于16个字符!",
            }
        }

        # 添加前端样式
        widgets = {
            "phone": forms.TextInput(attrs={'class': 'login-name', 'placeholder': '请输入手机号'}),
            "password": forms.PasswordInput(attrs={'class': 'login-password', 'placeholder': '请输入密码'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 验证手机号码格式是否正确
        self.fields['phone'].validators.append(validators.RegexValidator(r'^1[3-9]\d{9}$', "手机号码格式错误!"))
        # 密码 在form中要求 6-16 个
        self.fields['password'].validators.append(validators.MinLengthValidator(6))
        self.fields['password'].validators.append(validators.MaxLengthValidator(16))

    # 排除唯一性验证
    # https://docs.djangoproject.com/en/2.1/ref/models/instances/#validating-objects
    def validate_unique(self):
        pass


# 修改个人资料
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        # 排除那些字段不用验证
        exclude = ['create_time', 'update_time', 'is_delete', 'password']
        # 修改样式
        widgets = {
            "nickname": forms.TextInput(attrs={'class': "infor-tele", "placeholder": "请填写昵称"}),
            "gender": forms.RadioSelect(),
            "birthday": forms.DateInput(attrs={'class': "infor-tele", "type": 'date'}, format='%Y-%m-%d'),
            "school_name": forms.TextInput(attrs={'class': "infor-tele", "placeholder": "请输入学校"}),
            "address": forms.TextInput(attrs={'class': "infor-tele", "placeholder": "请输入地址"}),
            "hometown": forms.TextInput(attrs={'class': "infor-tele", "placeholder": "请输入老家"}),
            "phone": forms.TextInput(attrs={'class': "infor-tele", "placeholder": "请输入手机号"}),
        }

    # 排除唯一性验证
    # https://docs.djangoproject.com/en/2.1/ref/models/instances/#validating-objects
    def validate_unique(self):
        pass


# 验证前端表单
class Xxxform(forms.Form):
    phone = forms.CharField(max_length=11,
                            validators=[
                                validators.RegexValidator(r'^1[3-9]\d{9}', "手机号码格式错误!")
                            ],
                            )
    password = forms.CharField(max_length=16, min_length=6)
    repassword = forms.CharField(max_length=16, min_length=6)
    agree = forms.BooleanField()
