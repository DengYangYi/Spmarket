from django.conf.urls import url

from sp_order.views import (OrderDisplay,
                            AddressAddView,
                            AddressListView, OrderPayView)

urlpatterns = [
    # 确认订单展示页面
    url(r'^$', OrderDisplay.as_view(), name='display'),
    # 订单支付页面
    url(r'^order/pay/$', OrderPayView.as_view(), name='pay'),
    # 用户收货地址的添加
    url(r'^address/add/$', AddressAddView.as_view(), name='address_add'),
    # 用户收货地址的列表
    url(r'^address/list/$', AddressListView.as_view(), name='address_list'),
]
