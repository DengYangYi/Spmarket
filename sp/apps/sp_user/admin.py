from django.contrib import admin
from django.contrib.admin import ModelAdmin
from sp_user.models import TestImageModel, Users

@admin.register(Users)
class UsersAdmin(ModelAdmin):
	# 用户资料
	pass

@admin.register(TestImageModel)
class UsersAdmin(ModelAdmin):
	# 用户头像
	pass
