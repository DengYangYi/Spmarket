from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from sp_goods.models import (GoodsSKU,
							 Category,
							 )

from django_redis import get_redis_connection


class IndexView(View):
	"""首页"""

	def get(self, request):
		return render(request, 'sp_goods/index.html')


"""
  1. 展示sku商品， 只展示一种分类下的商品
  2. 用户点击那种分类就展示那种分类 --- 点击的 url 传递分类的id
  3. 如果用户第一次进入页面，默认展示第一个分类下的所有的商品
  4. 排序 --- 用户点击 排序 ---- url 传递一个参数 order 代表的是使用哪种排序规则 
      综合（id 升序） 销量（sale_num 降序） 价格降序（price） 价格升序(price)  新品(create_time 降序)
      order_by('id') 升序  order_by('-id') 降序
      order_rule = ['id','sale_num','-price','price','-create_time']
"""


# category/
class CategoryView(View):
	"""分类列表页"""

	def get(self, request, cate_id=0, order=0):
		# 参数类型为字符串 转成数字
		cate_id = int(cate_id)
		order = int(order)

		# 获取所有的分类信息
		categorys = Category.objects.filter(is_delete=False)

		# 展示对应分类下的商品 如果 cate_id 不为零 就查询出对应分类的下商品 如果为0是默认使用第一个分类下的商品
		if cate_id == 0:
			category = categorys.first()
			cate_id = category.pk
		else:
			category = Category.objects.get(pk=cate_id)

		# 获取对应分类下的所有的商品
		goodsSkuList = category.goodssku_set.all()

		# 读取购物车中当前用户的商品总数
		cart_total = 0
		if request.session.get("ID"):
			cnn = get_redis_connection('default')
			cart_key = "cart_%s" % request.session.get("ID")
			vars = cnn.hvals(cart_key)
			if len(vars) > 0:
				for v in vars:
					cart_total += int(v)

		# 处理排序
		# 定义一个列表， 代表的是排序规则
		order_rule = ['id', '-sale_num', '-price', 'price', '-create_time']
		# 获取当前应该属于那种排序
		current_order_rule = order_rule[order]
		goodsSkuList = goodsSkuList.order_by(current_order_rule)

		# 渲染数据到页面
		context = {
			'categorys': categorys,
			'cate_id': cate_id,
			'order': order,
			'goodsSkuList': goodsSkuList,
			'cart_total': cart_total,
		}
		return render(request, 'sp_goods/category.html', context)


# 连接 detail/1111/
class DetailView(View):
	"""商品详情"""

	def get(self, request, sku_id):
		# sku_id 类型字符串
		# 商品sku id
		sku_id = int(sku_id)
		# 数据库查找对应的商品
		try:
			goodsSku = GoodsSKU.objects.filter(is_delete=False).get(pk=sku_id)
		except GoodsSKU.DoesNotExist:
			# 如果查找不到该商品跳转到首页
			return redirect(reverse('sp_goods:index'))

		# 渲染数据
		context = {
			'goodsSku': goodsSku,
		}
		return render(request, 'sp_goods/detail.html', context)
