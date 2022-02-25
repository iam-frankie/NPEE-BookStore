from django.db import models

'''模型抽象基类'''
class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')
    '''说明是一个抽象模型类'''
    class Meta:
        abstract = True