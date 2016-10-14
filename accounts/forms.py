from django import forms
from django.db import transaction
from . import models
from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import CaptchaField

__all__ = [
    "SignupForm",
    "SigninForm",
]

USERNAME_RE = r'^[a-zA-Z0-9_.\u4e00-\u9fa5]+$'
User = get_user_model()


class MyAuthenticationForm(AuthenticationForm):
    captcha = CaptchaField(label='验证码',
                           output_format='<div class="row"><div class="col-sm-8">%(text_field)s %(hidden_field)s</div><div class="col-sm-4 padding">%(image)s</div></div>')

    class Meta:
        fields = [
            'email',
            'password',
            'captcha',
        ]


class MyPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(label='验证码', output_format='<div class="row"><div class="col-sm-8">%(text_field)s %(hidden_field)s</div><div class="col-sm-4 padding">%(image)s</div></div>')

    class Meta:
        fields = [
            'email'
            'captcha',
        ]


class SignupForm(RegistrationFormUniqueEmail):
    invitecode = forms.CharField(widget=forms.TextInput,
                                label="邀请码")
    nickname = forms.RegexField(regex=USERNAME_RE,
                                widget=forms.TextInput,
                                max_length=64,
                                label="昵称",
                                error_messages={'invalid': '昵称只能包含字母、数字、汉字、下划线和点'})
    captcha = CaptchaField(label='验证码',
                           output_format='<div class="row"><div class="col-sm-8">%(text_field)s %(hidden_field)s</div><div class="col-sm-4 padding">%(image)s</div></div>')

    class Meta:
        model = User
        fields = [
            'invitecode',
            'nickname',
            'email',
            'password1',
            'password2',
            'captcha'
        ]

    def clean_nickname(self):
        qs = User.objects.filter(nickname=self.cleaned_data.get('nickname'))
        if qs.exists():
            raise forms.ValidationError('该昵称已被注册')

        return self.cleaned_data.get('nickname')

    def clean_invitecode(self):
        if not models.Invitecode.objects.filter(code=self.cleaned_data['invitecode'], used=False).exists():
            raise forms.ValidationError('邀请码错误')

        return self.cleaned_data.get('invitecode')

    @transaction.atomic
    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=True)
        code = models.Invitecode.objects.get(code=self.cleaned_data['invitecode'])
        code.usedby = user
        code.used_time = user.date_joined
        code.used = True
        code.save()
        return user


class ProfileForm(forms.ModelForm):
    nickname = forms.RegexField(
        regex=USERNAME_RE,
        max_length=64,
        label='昵称',
        error_messages={'invalid': '昵称只能包含字母、数字、汉字、下划线和点'}
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self['mugshot'].field.widget = forms.FileInput()
        self['description'].field.widget = forms.Textarea(attrs={'rows': 3})

    class Meta:
        model = User
        fields = [
            'nickname',
            'mugshot',
            'description',
        ]