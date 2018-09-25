from django.utils.decorators import method_decorator
from django.views import View
from sp_user.helper import verify_login_required
class BaseVerifyView(View):
    """
        基础类视图，用于验证是否登录
    """
    @method_decorator(verify_login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseVerifyView, self).dispatch(request, *args, **kwargs)