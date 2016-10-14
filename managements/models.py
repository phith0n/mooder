from django.db import models
from mooder.settings import AUTH_USER_MODEL


class CoinLog(models.Model):
    coin = models.IntegerField('金币变化')
    rest = models.PositiveIntegerField('变化后的金币')
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name='目标用户', on_delete=models.CASCADE, related_name='coin_to_user')
    admin = models.ForeignKey(AUTH_USER_MODEL, verbose_name='操作员', blank=True, null=True, related_name='coin_from_user')
    message = models.CharField('原因', max_length=256, null=True, blank=True)

    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-created_time']


def log_coin(coin, rest, fromuser, touser, message=None):
    log = CoinLog(coin=coin, rest=rest, user=touser, admin=fromuser, message=message)
    log.save()