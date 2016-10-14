import urllib, hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, UserManager
from mooder.settings import USER_LEVEL_RANGE
from django.db.models.signals import pre_save
from django.shortcuts import reverse
from urllib.parse import urlencode
from django.dispatch import receiver
from django.forms import ValidationError

from mooder.settings import AUTH_USER_MODEL


class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None, *args, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            nickname=nickname,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


USER_LEVEL = [_[1] for _ in USER_LEVEL_RANGE]
DEFAULT_USER_LEVEL = USER_LEVEL_RANGE[0][1][0]


def generate_upload_filename(instance, filename):
    return "mugshots/%s/%s" % (instance.id, filename)


# Create your models here.
class Member(AbstractUser):
    username = models.CharField('用户名', max_length=64, blank=True, null=True)
    email = models.EmailField('邮箱', max_length=255, unique=True)
    nickname = models.CharField('昵称', max_length=64, unique=True)
    mugshot = models.ImageField('头像', upload_to=generate_upload_filename, blank=True, null=True)
    rank = models.PositiveIntegerField('Rank', default=0)
    coin = models.PositiveIntegerField('金币', default=0)
    level = models.CharField('等级', max_length=16, default=DEFAULT_USER_LEVEL, choices=USER_LEVEL)
    description = models.CharField('个人简介', max_length=512, blank=True, null=True)
    is_auditor = models.BooleanField('审核员', default=False, help_text='是否能够进入审核后台')

    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        ordering = ['-rank', '-date_joined']

    def get_absolute_url(self):
        return reverse('archive:profile', kwargs=dict(uid=self.id))

    def get_mugshot_url(self):
        if self.mugshot:
            return self.mugshot.url
        else:
            gravatar_url = "//www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode()).hexdigest() + "?"
            gravatar_url += urlencode({'s': '100'})
            return gravatar_url


class Invitecode(models.Model):
    code = models.CharField('邀请码', max_length=32, unique=True)
    usedby = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='used_by_user')
    createdby = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_by_user', blank=True, null=True)
    used = models.BooleanField('使用', default=False)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)
    used_time = models.DateTimeField('使用时间', blank=True, null=True)

    class Meta:
        ordering = ['-created_time']
        verbose_name = "邀请码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code


@receiver(pre_save, sender=Member)
def pre_save_member_receiver(sender, instance, *args, **kwargs):
    for level in USER_LEVEL_RANGE:
        level_name = level[1][0]
        if level[0][0] <= instance.rank < level[0][1] and instance.level != level_name:
            instance.level = level_name
            break

    if instance.rank >= USER_LEVEL_RANGE[-1][0][0]:
        instance.level = USER_LEVEL_RANGE[-1][1][0]