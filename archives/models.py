import io, os
from datetime import datetime
from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings
from uuid import uuid4
from django.template.defaultfilters import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.templatetags.static import static

__all__ = [
    'VERIFY_STATUS_CHOICES',
    'VISIBLE_STATUS_CHOICES',
    'LEVEL_STATUS_CHOICES',
    'Post',
    'Comment',
    'Category',
    'PostImage',
    'Link',
]

VERIFY_STATUS_CHOICES = (
    ('wait', '待审核'),
    ('pass', '通过'),
    ('failed', '未通过')
)
VISIBLE_STATUS_CHOICES = (
    ('private', '私密的'),
    ('sell', '出售的'),
    ('public', '公开的')
)
LEVEL_STATUS_CHOICES = (
    ('low', '低危'),
    ('medium', '中危'),
    ('high', '高危'),
    ('grave', '严重')
)
generate_random_filename = lambda a,b:b


def check_image_extension(field):
    _allowed_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    _, ext = os.path.splitext(field.name)
    ext = ext.lower()
    if ext not in _allowed_ext:
        raise ValidationError("图片文件只允许以下后缀： %s." % (','.join(_allowed_ext), ))


def generate_attachment_filename(instance, filename):
    filename, ext = os.path.splitext(filename)
    if ext not in ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.rar', '.gz', '.zip', '.7z', '.txt', '.pdf',
                   '.doc', '.docx', '.ppt', '.pptx', ):
        ext = '.attach'
    filename = "%s-%s%s" % (uuid4(), get_random_string(length=8), ext)

    tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
    date_dir = date(datetime.now(tz=tzinfo), 'Y/m')

    return "attachment/%s/%s" % (date_dir, filename)


def generate_image_filename(instance, filename):
    filename, ext = os.path.splitext(filename)
    filename = "%s-%s%s" % (uuid4(), get_random_string(length=8), ext)

    tzinfo = timezone.get_current_timezone() if settings.USE_TZ else None
    date_dir = date(datetime.now(tz=tzinfo), 'Y/m/d')

    return "images/%s/%s" % (date_dir, filename)


class FrontPostManager(models.Manager):
    def get_queryset(self):
        return super(FrontPostManager, self).get_queryset().filter(show=True)


# Create your models here.
class Post(models.Model):
    title = models.CharField('标题', max_length=256)
    content = models.TextField('内容', blank=True)
    description = models.TextField('简要描述', blank=True)
    verify = models.CharField('状态', max_length=8, choices=VERIFY_STATUS_CHOICES, default='wait')
    visible = models.CharField('公开度', max_length=8, choices=VISIBLE_STATUS_CHOICES, default='private')
    show = models.BooleanField('显示', default=True)
    rank = models.PositiveIntegerField('Rank', default=0)
    level = models.CharField('等级', max_length=8, choices=LEVEL_STATUS_CHOICES, default='low')
    attachment = models.FileField('附件', blank=True, upload_to=generate_attachment_filename)
    remark = models.TextField('评价', null=True, blank=True)

    price = models.PositiveIntegerField('价格', default=0)
    buyers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_buy_post', blank=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE, related_name='author_post')
    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)
    verify_time = models.DateTimeField('审核时间', blank=True, null=True)

    objects = models.Manager()
    posts = FrontPostManager()

    class Meta:
        ordering = ['-created_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('archive:detail', kwargs=dict(pk=self.id))


class Comment(models.Model):
    content = models.TextField('评论')
    post = models.ForeignKey(Post, verbose_name='文章', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='作者', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', verbose_name='父评论', blank=True, null=True)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['created_time']
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s's Comment" % self.author.nickname


@receiver(pre_save, sender=Comment)
def pre_save_comment_receiver(sender, instance, *args, **kwargs):
    if instance.parent is None:
        return

    try:
        comment = Comment.objects.get(pk=instance.parent.id)
    except Comment.DoesNotExist:
        instance.parent = None
        return

    if comment.post_id != instance.post_id:
        instance.parent = None


class Category(models.Model):
    name = models.CharField('分类名', max_length=30)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class PostImage(models.Model):
    file = models.ImageField('图片', upload_to=generate_image_filename, validators=[check_image_extension], blank=True)
    name = models.CharField('文件名', blank=True, null=True, max_length=256)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='上传者', on_delete=models.CASCADE)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    def __str__(self):
        return self.file.url


class Link(models.Model):
    title = models.CharField('名称', max_length=32)
    link = models.URLField('链接')

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['created_time']
        verbose_name = "应用链接"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Gift(models.Model):
    name = models.CharField('名称', max_length=256)
    link = models.URLField('参考链接', null=True, blank=True)
    photo = models.ImageField('图片', upload_to=generate_image_filename,
                              validators=[check_image_extension], null=True, blank=True)
    description = models.TextField('描述', blank=True)
    price = models.PositiveIntegerField('价格')
    amount = models.PositiveIntegerField('数量', default=0)
    show = models.BooleanField('显示', default=True)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-price']
        verbose_name = '礼物'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        else:
            return static('img/gift.jpg')

    def get_absolute_url(self):
        return reverse('archive:gift', kwargs=dict(pk=self.id))


class GiftLog(models.Model):
    gift = models.ForeignKey(Gift, verbose_name='礼物')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='购买者')
    cost = models.PositiveIntegerField('花费')
    delivery = models.BooleanField('发货', default=False)

    address = models.CharField('收货地址', max_length=512, help_text='填写收件地址，虚拟物品则填写邮箱或QQ', null=True)
    remark = models.TextField('备注', null=True, blank=True, help_text='没有则无需填写')

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)
    delivery_time = models.DateTimeField('发货时间', blank=True, null=True)

    reply = models.TextField('管理员回复', null=True, blank=True, help_text='发货订单号等')

    class Meta:
        ordering = ['-created_time']
        verbose_name = '购买记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ""

    def get_absolute_url(self):
        return reverse('archive:order', kwargs=dict(pk=self.id))