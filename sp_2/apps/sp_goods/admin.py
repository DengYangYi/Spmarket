from django.contrib import admin

from sp_goods.models import Category, Unit, GoodsSPU, GoodsSKU, Gallery


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 商品分类
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    # 商品单位
    pass


@admin.register(GoodsSPU)
class GoodsSPUAdmin(admin.ModelAdmin):
    # 商品SPU
    pass


# 关联商品的相册
class GoodsSKUAdminInLine(admin.StackedInline):
    model = Gallery
    extra = 2
    fields = ['goods_sku', 'img_url', 'img_url_show']
    readonly_fields = ('img_url_show',)


# 注册GoodsSKU的模型到后台
@admin.register(GoodsSKU)
# 定制显示效果
class GoodsSKUAdmin(admin.ModelAdmin):
    # 设计后台界面
    list_per_page = 20  # 每页显示条数
    list_display = ["id", 'sku_name', 'price', 'stock', 'sale_num', 'sup_name', 'category_name', 'is_on_sale','logo_img',
                    'create_time']  # 列表页显示字段
    list_display_links = ['sku_name', 'price', 'sup_name']

    list_filter = ['sku_name', "price"]
    search_fields = ['sku_name', "price", "create_time", "is_on_sale"]

    readonly_fields = ('logo_img',)
    fieldsets = (
        ("基本信息", {"fields": ('sku_name', 'brief', 'price', 'stock', 'sale_num', 'is_on_sale')}),
        ("详细信息", {"fields": ('logo_img', 'logo', 'unit', 'category', 'goods_spu', 'is_delete')}),
    )
    # 商品SPU
    # 关联模型展示
    inlines = [
        GoodsSKUAdminInLine
    ]
