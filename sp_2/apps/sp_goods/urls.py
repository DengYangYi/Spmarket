from django.conf.urls import url

from sp_goods.views import (IndexView,
                            CategoryView,
                            DetailView,
                            )

urlpatterns = [
    # 首页路由绑定
    url(r'^$', IndexView.as_view(), name='index'),
    # 商品列表页
    url(r'^category/(?P<cate_id>\d+)_(?P<order>\d).html$', CategoryView.as_view(), name='category'),
    # 商品详情页
    url(r'^detail/(?P<sku_id>\d+)/$', DetailView.as_view(), name='detail'),
]
