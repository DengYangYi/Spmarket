from django.utils.decorators import method_decorator
from django.views import View

from sp_user.helper import check_is_login


class BaseVerifyView(View):
    """
        需要验证登陆的视图继承该视图类
    """

    # 视图类装饰器使用 验证登陆
    @method_decorator(check_is_login)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseVerifyView, self).dispatch(request, *args, **kwargs)
