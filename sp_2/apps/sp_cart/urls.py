from django.conf.urls import url

from sp_cart.views import (CartAddView,
                           CartDeleteView,
                           CartShowView, )

urlpatterns = [
    url(r'^cart/$', CartShowView.as_view(), name='index'),  # 购物车首页
    url(r'^cartAdd/$', CartAddView.as_view(), name='addCart'),  # 加入购物车
    url(r'^cartDelete/$', CartDeleteView.as_view(), name='cartDelete'),  # 购物车删除
]
