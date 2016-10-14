from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def allow_read_post(context, post, content):
    user = context['request'].user
    if user.is_superuser or post.author_id == user.id:
        pass
    elif post.visible == 'private':
        content = '''<div class="am-alert am-alert-secondary" data-am-alert>
  <p>该贡献未公开，只有作者能够查看。</p>
</div>'''
    elif post.visible == 'sell' and not post.buyers.filter(id=user.id).exists():
        url = reverse('archive:buy', kwargs={'pk': post.id})
        content = '''<div class="am-alert am-alert-secondary" data-am-alert>
  <p>该贡献未公开，是否要购买并查看？</p>
  <p>价格：<span class="am-text-danger">%s</span> 金币， 你的余额： <span class="am-text-danger">%s</span> 金币</p>
  <p><a class="am-btn am-btn-primary am-btn-sm confirm-alert" href="javascript:submit('%s');">购买</a></p>
</div>''' % (post.price, user.coin, url, )

    return mark_safe(content)
