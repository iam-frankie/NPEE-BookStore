from django.contrib import admin
from .models import GoodsType, IndexPromotionBanner, IndexGoodsBanner, IndexTypeGoodsBanner, GoodsSKU, Goods, GoodsImage
from celery_tasks.tasks import generate_static_index_html
from django.core.cache import cache


# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """新增、更新表中数据时可以调用"""
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker重新生成首页静态页面（在虚拟机上端）
        generate_static_index_html.delay()

        # 清除首页的缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """删除表中数据时使用"""
        super().delete_model(request, obj)
        # 发出任务，让celery worker重新生成首页静态页
        generate_static_index_html.delay()

        # 清楚首页的缓存
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


class GoodsSKUAdmin(BaseModelAdmin):
    pass


class GoodsSPUAdmin(BaseModelAdmin):
    pass


class GoodsImageAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)

admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(Goods, GoodsSPUAdmin)
admin.site.register(GoodsImage, GoodsImageAdmin)
