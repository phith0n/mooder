from django.contrib import admin
from .models import Post, Category, Link, Comment, Gift, GiftLog

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'verify', 'visible', 'level', 'rank']
    date_hierarchy = 'created_time'
    actions = ['ignore_post']

    def ignore_post(self, request, queryset):
        queryset.update(verify='failed')

    ignore_post.short_description = "忽略所选文章"


# Register your models here.
admin.site.register(Category)
admin.site.register(Link)
admin.site.register(Comment)
admin.site.register(Gift)
admin.site.register(GiftLog)