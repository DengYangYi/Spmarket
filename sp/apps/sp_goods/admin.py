from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline
from sp_goods.models import (Category,
							 Unit,
							 GoodsSKU,
							 GoodsSPU,
							 Gallery,
							 Banner)

admin.site.site_header = "超级电商管理平台"


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
	# 商品分类
	pass


@admin.register(Unit)
class UnitAdmin(ModelAdmin):
	# 商品单位
	pass


@admin.register(GoodsSPU)
class GoodsSPUAdmin(ModelAdmin):
	# 商品SPU
	pass

@admin.register(Banner)
class BannerAdmin(ModelAdmin):
	# 商品SPU
	pass


class GoodsSKUAdminInLine(TabularInline):
	model = Gallery
	extra = 1
	fields = ["goods_sku", "img_url"]


class BannerAdminInLine(TabularInline):
	model = Banner
	extra = 1
	fields = ["name", "goods_sku", "img_url",]
	pass


@admin.register(GoodsSKU)
class GoodsSKUAdmin(ModelAdmin):
	# 商品SKU
	inlines = [
		GoodsSKUAdminInLine,
		BannerAdminInLine,
	]
	pass
