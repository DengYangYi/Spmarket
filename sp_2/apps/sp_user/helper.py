import hashlib

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from django.conf import settings
from django.shortcuts import redirect, reverse

from sp_user.models import User


def set_password(pwd):
    # 密码加密算法
    key = settings.SECRET_KEY
    token = key + str(pwd)
    h = hashlib.sha1(token.encode('utf-8'))
    return h.hexdigest()


def check_phone_pwd(phone, pwd):
    # 验证用户名和密码 返回用户信息
    return User.objects.filter(phone=phone, password=set_password(pwd)).first()


# 装饰器 验证用户是否登陆
def check_is_login(old_func):
    # 新的方法 request 参数 里面有session
    def new_func_verify(request, *args, **kwargs):
        if request.session.get("ID") is None:
            # 没有登陆 跳转到登陆页面
            return redirect(settings.URL_LOGIN)
        else:
            # 已经登陆
            return old_func(request, *args, **kwargs)
    # 返回新函数
    return new_func_verify



# 阿里自带发送短信的方法
def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    # 注意：不要更改
    REGION = "cn-hangzhou"
    PRODUCT_NAME = "Dysmsapi"
    DOMAIN = "dysmsapi.aliyuncs.com"

    acs_client = AcsClient(settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET, REGION)
    region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 数据提交方式
    # smsRequest.set_method(MT.POST)

    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse