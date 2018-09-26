from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# 商城首页
from sp_goods.models import Category, GoodsSKU, Banner


class IndexView(View):
	def get(self, request):
		banner_all = Banner.objects.filter()
		context = {
			'banner_all': banner_all,
		}
		return render(request, 'sp_goods/index.html', context)


# 分类页
class CategoryView(View):

	def get(self, request, cate_id=0, order=0):  # 分类id默认为0
		# 列表展示
		cate_id = int(cate_id)  # 字符串转成数字
		order = int(order)
		category_all = Category.objects.filter(is_delete=False)  # 获取所有的分类信息
		if cate_id == 0:  # 为0默认使用第一个分类下的商品，cate_id 不为零查询出对应分类的商品，
			category = category_all.first()
			cate_id = category.pk
		else:
			category = Category.objects.get(pk=cate_id)
		goodssku_list = category.goodssku_set.all()  # 根据获得的分类id，一对多反向查询。category if或else都要用到

		# 处理排序
		order_rule = ['id', '-sale_num', '-price', 'price', '-create_time']  # 定义一个列表排序规则
		current_order_rule = order_rule[order]  # 获取当前应该属于那种排序
		goodssku_list = goodssku_list.order_by(current_order_rule)  # 更新商品列表按排序展示

		# 渲染数据到页面
		context = {
			'category_all': category_all,
			'cate_id': cate_id,
			'order': order,
			'goodssku_list': goodssku_list,
		}
		return render(request, 'sp_goods/category.html', context)


# 商品详情
class DetailView(View):
	"""商品详情"""

	def get(self, request, sku_id):
		# 最好转一下参数类型,字符串转成数字
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
