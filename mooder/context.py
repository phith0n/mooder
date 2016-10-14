from django.core.urlresolvers import resolve
from archives.models import Link


def global_site_context(request):
    links = Link.objects.all()
    return {
        'website': {
            'title': "安全盒子内部贡献平台",
        },
        'view': {
            'name': resolve(request.path).view_name
        },
        'links': links
    }