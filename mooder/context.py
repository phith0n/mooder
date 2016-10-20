from django.core.urlresolvers import resolve
from archives.models import Link
from django.conf import settings


def global_site_context(request):
    links = Link.objects.all()
    return {
        'website': settings.SITE,
        'view': {
            'name': resolve(request.path).view_name
        },
        'links': links
    }