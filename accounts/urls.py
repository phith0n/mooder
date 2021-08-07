from django.urls import path, re_path, include, reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    logout_then_login,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.views.generic import TemplateView
from registration.backends.default import views as registration_views

from django.conf import settings
from . import forms


class ActivationView(registration_views.ActivationView):
    def get_success_url(self, user):
        return ('accounts:registration_activation_complete', (), {})


registration_urls = [
    path('register/',
         registration_views.RegistrationView.as_view(success_url=reverse_lazy('accounts:registration_complete')),
         name='registration_register'
         ),
    path('activate/complete/',
         TemplateView.as_view(template_name='registration/activation_complete.html'),
         name='registration_activation_complete'
         ),
    path('activate/resend/',
         registration_views.ResendActivationView.as_view(),
         name='registration_resend_activation'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    path('activate/<activation_key>/',
         ActivationView.as_view(),
         name='registration_activate'),
    path('register/complete/',
         TemplateView.as_view(template_name='registration/registration_complete.html'),
         name='registration_complete'),
    path('register/closed/',
         TemplateView.as_view(template_name='registration/registration_closed.html'),
         name='registration_disallowed'),
]

app_name = 'accounts'
urlpatterns = [
    path('', include(registration_urls)),

    path('login/', LoginView.as_view(authentication_form=forms.MyAuthenticationForm), name='login'),
    path('logout/', logout_then_login, name='logout'),
    path('password_change/',
         PasswordChangeView.as_view(success_url=reverse_lazy('accounts:password_change_done')),
         name='password_change'
         ),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(
        form_class=forms.MyPasswordResetForm,
        from_email=settings.EMAIL_HOST_USER,
        success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(success_url=reverse_lazy('accounts:password_reset_complete')),
         name='password_reset_confirm'
         ),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
