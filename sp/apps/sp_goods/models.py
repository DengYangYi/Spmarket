from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from db.base_model import BaseModel

is_on_sale_choices = (
	(0, "下架"),
	(1, "上架"),
)


# 分类名称
class Category(BaseModel):
	cate_name = models.CharField(verbose_name="分类名称",
								 max_length=20
								 )
	brief = models.CharField(verbose_name="描述",
							 max_length=200,
							 null=True,
							 blank=True
							 )

	def __str__(self):
		return self.cate_name

	class Meta:
		verbose_name = "商品分类管理"
		verbose_name_plural = verbose_name


# 单位
class Unit(BaseModel):
	name = models.CharField(max_length=20,
							verbose_name="单位",
							)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "商品单位管理"
		verbose_name_plural = verbose_name


# 商品SPU
class GoodsSPU(BaseModel):
	spu_name = models.CharField(max_length=20,
								verbose_name="商品SPU",
								)
	content = RichTextUploadingField(verbose_name="商品详情")

	def __str__(self):
		return self.spu_name

	class Meta:
		verbose_name = "商品SPU管理"
		verbose_name_plural = verbose_name


# 商品SKU
class GoodsSKU(BaseModel):
	sku_name = models.CharField(max_length=100,
								verbose_name="商品SKU"
								)
	brief = models.CharField(verbose_name="商品简介",
							 max_length=200,
							 null=True,
							 blank=True
							 )
	price = models.DecimalField(verbose_name="价格",
								max_digits=9,
								decimal_places=2,
								default=0,
								)
	unit = models.ForeignKey(to="Unit",
							 verbose_name="单位",
							 )
	stock = models.IntegerField(verbose_name="库存",
								default=0,
								)
	sale_num = models.IntegerField(verbose_name="销量",
								   default=0,
								   )
	logo = models.ImageField(verbose_name="封面图片",
							 upload_to="goods/%Y%m/%d"
							 )
	is_on_sale = models.BooleanField(verbose_name="是否上架",
									 choices=is_on_sale_choices,
									 default=0,
									 )
	calgary = models.ForeignKey(to="Category",
								verbose_name="商品分类",
								)
	goods_spu = models.ForeignKey(to="GoodsSPU",
								  verbose_name="商品SPU",
								  )

	def __str__(self):
		return self.sku_name

	class Meta:
		verbose_name = "商品SKU管理"
		verbose_name_plural = verbose_name


# 相册管理
class Gallery(BaseModel):
	img_url = models.ImageField(verbose_name="相册图片地址",
								upload_to="goods_gallery/%Y%m/%d",
								)
	goods_sku = models.ForeignKey(to="GoodsSKU",
								  verbose_name="SKU商品",
								  )

	def __str__(self):
		return '商品:%s的相册' % self.goods_sku.sku_name

	class Meta:
		verbose_name = "相册管理"
		verbose_name_plural = verbose_name


# 首页轮播管理
class Banner(BaseModel):
	name = models.CharField(verbose_name="首页轮播活动名",
							max_length=150,
							)
	goods_sku = models.ForeignKey(to="GoodsSKU",
								  verbose_name="SKU商品",
								  )
	img_url = models.ImageField(verbose_name="轮播图片地址",
								upload_to="banner/%Y%m/%d",
								)
	order = models.SmallIntegerField(verbose_name="排序",
									 default=0,
									 )

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "首页轮播管理"
		verbose_name_plural = verbose_name


# 活动管理
class Activity(BaseModel):
	title = models.CharField(verbose_name="活动名称",
							 max_length=150,
							 )
	img_url = models.ImageField(verbose_name="活动图片地址",
								upload_to="activity/%Y%m/%d"
								)
	url_site = models.CharField(verbose_name="活动url地址",
								max_length=200
								)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "活动管理"
		verbose_name_plural = verbose_name


# 活动专区管理
class ActivityZone(BaseModel):
	title = models.CharField(verbose_name="活动专区名称",
							 max_length=150,
							 )
	brief = models.CharField(verbose_name="活动专区简介",
							 max_length=200,
							 null=True,
							 blank=True,
							 )
	order = models.SmallIntegerField(verbose_name="排序",
									 default=0,
									 )
	is_on_sale = models.BooleanField(verbose_name="是否上线",
									 choices=is_on_sale_choices,
									 default=0
									 )

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "活动专区管理"
		verbose_name_plural = verbose_name


# 专区
class ActivityZoneGoods(BaseModel):
	activity_zone = models.ForeignKey(to="ActivityZone",
									  verbose_name="活动专区ID",
									  )
	goods_sku = models.ForeignKey(to="GoodsSKU",
								  verbose_name="专区商品SKU_ID"
								  )
