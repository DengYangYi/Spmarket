from django.contrib import admin

from sp_order.models import Transport


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    pass
