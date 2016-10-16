from django.conf.urls import url, include
from . import views
from django.contrib.auth.views import (
    login,
    logout_then_login,
    password_change,
    password_change_done,
    password_reset,
    password_reset_done,
    password_reset_confirm,
    password_reset_complete,
)
from django.conf import settings
from . import forms

urlpatterns = [
    url(r'^', include('registration.backends.default.urls')),

    url(r'^login/$', login, name='login', kwargs=dict(authentication_form=forms.MyAuthenticationForm)),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^password_change/$', password_change, name='password_change'),
    url(r'^password_change/done/$', password_change_done, name='password_change_done'),
    url(r'^password_reset/$', password_reset, name='password_reset', kwargs=dict(password_reset_form=forms.MyPasswordResetForm, from_email=settings.EMAIL_HOST_USER)),
    url(r'^password_reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', password_reset_complete, name='password_reset_complete'),
]