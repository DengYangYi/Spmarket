from django.shortcuts import render, redirect, reverse
from sp_goods.models import (GoodsSKU, )
from db.base_view import BaseVerifyView
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from sp_order.forms import AddressAddForm
from sp_order.models import (Transport,
							 UserAddress,
							 OrderInfo,
							 OrderGoods,
							 )
from datetime import datetime
import random
from sp_user.models import User
from django.db import transaction


# /
class OrderDisplay(BaseVerifyView):
	"""确认订单页面， 即将生成订单的商品展示出来（价格，运输方式，收货地址）"""

	def get(self, request):
		"""
		:param skus 代表的商品的sku_id:
			1. 获取商品id （获取一个 request.GET.get() 获取多个 request.GET.getlist() ）
			2. 查询商品信息
			3. 数量从redis购物车中获取
			4. 计算商品金额
			5. 计算总金额（商品总金额加运费）
		"""
		# 用户的id
		user_id = request.session.get("ID")

		# 1.获取商品id
		sku_ids = request.GET.getlist('skus')
		# 2. 查询商品信息
		goodsList = []  # 存储多个商品信息
		total_sku_price = 0
		# 3. 数量从redis购物车中获取
		cnn = get_redis_connection('default')
		cart_key = "cart_%s" % user_id

		for sku_id in sku_ids:
			# 获取一个商品信息
			try:
				goods = GoodsSKU.objects.get(pk=sku_id)
				# goods商品对象上添加一个新的属性 count 代表商品的数量
				count = cnn.hget(cart_key, sku_id)
				count = int(count)
				goods.count = count
				goodsList.append(goods)

				# 计算的商品的总金额
				total_sku_price += count * goods.price
			except:
				return redirect(reverse("sp_cart:index"))

		# 查询配送方式
		transList = Transport.objects.filter(is_delete=False).order_by('money')
		# 计算总金额
		trans = transList.first()
		total_price = total_sku_price + trans.money

		# 当期用户收货地址的处理，显示默认收货地址
		address = UserAddress.objects.filter(is_delete=False, isDefault=True).first()

		# 渲染页面
		context = {
			'goodsList': goodsList,
			'total_sku_price': total_sku_price,
			'transList': transList,
			'total_price': total_price,
			'address': address,
		}

		# 在session中保存一个会跳地址
		request.session['bak_url'] = request.get_full_path()

		return render(request, 'sp_order/tureorder.html', context)

	# 事务
	@transaction.atomic
	def post(self, request):
		"""保存订单信息到 订单基本信息表 和 订单商品表中"""
		"""
			1. 收货地址add_id
			2. 商品sku_ids(多个 request.POST.getlist("sku_ids"))
			3. 配送方式transport
		"""
		# 获取用户id
		user_id = request.session.get("ID")
		try:
			user = User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return JsonResponse({"error": 1, "msg": "参数错误!"})

		# 接受请求参数判断
		add_id = request.POST.get("add_id")
		sku_ids = request.POST.getlist('sku_ids')
		transport = request.POST.get('transport')
		if not all([add_id, sku_ids, transport]):
			return JsonResponse({"error": 2, "msg": "参数错误!"})

		# 获取收货地址信息
		try:
			address = UserAddress.objects.filter(is_delete=False, user_id=user_id).get(pk=add_id)
		except UserAddress.DoesNotExist:
			return JsonResponse({"error": 3, "msg": "收货地址不存在!"})

		# 获取配送方式的信息
		try:
			transport = Transport.objects.filter(is_delete=False).get(pk=transport)
		except Transport.DoesNotExist:
			return JsonResponse({"error": 4, "msg": "配送方式不存在!"})

		"""
			1.添加订单基本信息表数据
			2.添加订单商品表数据
		"""
		# 设置一个保存点,以后回滚到该保存点位置
		sid = transaction.savepoint()

		# 生成一个订单编号
		order_sn = "{}{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), random.randint(1000, 9999), user_id)
		# 收货地址
		address_info = "{}{}{}{}".format(address.hcity, address.hproper, address.harea, address.brief)
		try:
			orderinfo = OrderInfo.objects.create(
				order_sn=order_sn,
				user=user,
				receiver=address.username,
				receiver_phone=address.phone,
				address=address_info,
				transport=transport,
				transport_price=transport.money
			)
			# print(orderinfo)
		except:
			return JsonResponse({"error": 5, "msg": "创建订单基本信息失败"})

		# 准备变量保存新
		order_money = 0  # 订单金额
		"""
			2.添加订单商品表数据
				商品数量 在redis
				商品价格 goodsSku表, 查询该表
		"""
		# 连接redis
		cnn = get_redis_connection("default")
		cart_key = "cart_%s" % user_id
		for sku_id in sku_ids:
			# 获取商品的信息
			# time.sleep(11)
			try:
				goods_sku = GoodsSKU.objects.select_for_update().get(pk=sku_id)
			except GoodsSKU.DoesNotExist:
				# 手动回滚事务
				transaction.savepoint_rollback(sid)
				return JsonResponse({"error": 6, "msg": "商品不存在!"})

			# 获取购物车中商品的数量
			count = cnn.hget(cart_key, sku_id)

			# 判断库存是否足够
			if goods_sku.stock < int(count):
				# 手动回滚事务
				transaction.savepoint_rollback(sid)
				return JsonResponse({"error": 7, "msg": "商品库存不足!"})

			# 保存订单商品表的数据
			try:
				order_goods = OrderGoods.objects.create(
					order=orderinfo,
					goods_sku=goods_sku,
					price=goods_sku.price,
					count=int(count)
				)
			except:
				# 手动回滚事务
				transaction.savepoint_rollback(sid)
				return JsonResponse({"error": 8, "msg": "创建订单商品数据失败!"})

			# 订单商品表保存成功, 说明该商品的库存减少
			goods_sku.stock -= int(count)
			# 销量增加
			goods_sku.sale_num += int(count)
			goods_sku.save()

			# 累计计算订单总价
			order_money += int(count) * goods_sku.price

		# 将订单商品总价保存在订单基本信息表中
		try:
			orderinfo.order_money = order_money
			orderinfo.save()
		except:
			# 手动回滚事务
			transaction.savepoint_rollback(sid)
			return JsonResponse({"error": 9, "msg": "更新订单价格失败!"})

		# 清空购物车
		cnn.hdel(cart_key, *sku_ids)
		# 提交事务
		transaction.savepoint_commit(sid)

		return JsonResponse({"error": 0, "msg": "创建订单成功", "order_sn": order_sn})


# order/pay/
class OrderPayView(BaseVerifyView):
	def get(self, request):
		# 展示订单信息
		# 获取订单信息
		order_sn = request.GET.get("order_sn")
		# 用户的id
		user_id = request.session.get("ID")
		# 订单信息
		orderinfo = OrderInfo.objects.filter(user_id=user_id).get(order_sn=order_sn)

		# 获取订单的而商品信息
		orderGoods = orderinfo.ordergoods_set.all()

		# 总金额
		total_money = orderinfo.transport_price + orderinfo.order_money
		# 渲染数据到页面
		context = {
			'orderinfo': orderinfo,
			'orderGoods': orderGoods,
			'total_money': total_money
		}
		return render(request, 'sp_order/order.html', context)

	def post(self):
		# 向第三方支付平台发起支付请求
		pass


# address/add/
class AddressAddView(BaseVerifyView):
	def get(self, request):
		return render(request, 'sp_order/address.html')

	def post(self, request):
		# 验证数据的的合法性
		data = request.POST.dict()
		data['user_id'] = request.session.get("ID")
		add_form = AddressAddForm(data)
		if add_form.is_valid():
			# 判断是否将当期地址设置为默认收货地址
			if add_form.cleaned_data.get('isDefault'):
				# 将该用户的其他收货地址设置为false
				UserAddress.objects.filter(user_id=request.session.get("ID")).update(isDefault=False)

			# 保存的时候必须有用户的id
			add_form.instance.user_id = request.session.get("ID")
			add_form.save()
			return JsonResponse({"ok": 0})
		else:
			return JsonResponse({"ok": 1, "errors": add_form.errors})


# address/list/
class AddressListView(BaseVerifyView):
	"""收货地址的列表展示"""

	def get(self, request):
		user_id = request.session.get("ID")
		# 获取当前用户的所有的收货地址
		addressList = UserAddress.objects.filter(is_delete=False, user_id=user_id).order_by('-isDefault')
		# print(request.path)
		# print(request.get_full_path())
		context = {
			"addressList": addressList
		}
		return render(request, "sp_order/address_list.html", context)

	def post(self, request):
		"""设置默认的地址"""
		user_id = request.session.get("ID")
		# 收货地址id
		add_id = request.POST.get('add_id')
		# 将该用户其他的收货地址设置为false
		UserAddress.objects.filter(is_delete=False, user_id=user_id).update(isDefault=False)
		# 当前地址设置true
		UserAddress.objects.filter(is_delete=False, user_id=user_id, pk=add_id).update(isDefault=True)
		return JsonResponse({"ok": 0})
