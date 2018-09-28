from django.contrib import admin

# Register your models here.
from sp_user.models import User


@admin.register(User)
class SpUserAdmin(admin.ModelAdmin):
    fields = ['nickname', 'phone','gender','head','birthday','school_name','address','hometown']
