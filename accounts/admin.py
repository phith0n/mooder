from django.contrib import admin
from . import models


class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'nickname', 'date_joined')

# Register your models here.
admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Invitecode)