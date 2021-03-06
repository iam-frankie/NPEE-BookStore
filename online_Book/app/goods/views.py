from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator  # 导入分页器
from .models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from order.models import OrderGoods  # 报错可忽略
from django_redis import get_redis_connection


# Create your views here.

# 动态增加属性
# class Test(object):
#     def __init__(self):
#         self.name = 'abc'
#
# t = Test()
# t.age = 10
# print(t.age)


# http://127.0.0.1:8000


class IndexView(View):
    '''首页'''

    def get(self, request):
        '''显示首页'''
        # 尝试从缓存中获取数据
        # context = cache.get('index_page_data')

        # if context is None:
        #     print('设置缓存')
        # 缓存中没有数据
        # 获取商品的种类信息
        types = GoodsType.objects.all()

        # 获取首页轮播商品信息
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')  # 默认升序 0 1 2 3

        # 获取首页促销活动信息
        promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

        # 获取首页分类商品展示信息
        for type in types:  # GoodsType
            # 获取type种类首页分类商品的图片展示信息
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
            # 获取type种类首页分类商品的文字展示信息
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

            # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
            type.image_banners = image_banners
            type.title_banners = title_banners

        # 设置缓存
        # key-缓存数据名称 value-缓存内容 timeout-缓存保留时间
        # cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:  # 是属性不是方法
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        # 组织传输到前端的
        context = {'types': types,  # type是一个数据集合
                   'goods_banners': goods_banners,
                   'promotion_banners': promotion_banners,
                   'cart_count': cart_count
                   }
        # context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)


# /goods/商品id
class DetailView(View):
    '''详情页'''

    def get(self, request, goods_id):
        '''显示详情页'''
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()  # 用于转到其他商品界面

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]  # 只取前两个

        # 获取同一个SPU的其他规格商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取用户购物车中商品的数目-与前面主页一致，都需要获取用户的购物车
        user = request.user
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id-从左侧开始left
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧lpush
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {'sku': sku, 'types': types,  # sku商品标签
                   'sku_orders': sku_orders,
                   'new_skus': new_skus,
                   'same_spu_skus': same_spu_skus,
                   'cart_count': cart_count}

        # 使用模板
        return render(request, 'detail.html', context)


# goods/1（restful的设计风格）
# 种类id 页码 排序方式
# restful api -> 请求一种资源
# /list?type_id = 种类id    &   page=页码     &     sort=排序方式
# /list/种类id/页码/排序方式
# /list/种类id/页码？sort=排序方式
class ListView(View):
    """列表页面"""

    def get(self, request, type_id, page):
        """显示列表页"""
        # 获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
            print('存在')
            print("商品的种类id是" + type_id)
            print("商品的页数是" + page)
        except GoodsType.DoesNotExist:
            # 种类不存在
            print('不存在')
            print("商品的种类id是" + type_id)
            print("商品的页数是" + page)
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取排序方式 和分类商品信息
        # sort = default 按照默认id排序
        # sort = price 按照商品价格排序
        # sort = hot 按照销量排序
        sort = request.GET.get('sort')

        if sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)

        # todo: 进行页码控制，页面上最多显示5个页码
        # 1、总页数小于5页，页面上显示所有页码
        # 2、如果是前3页，显示1-5页
        # 3、如果当前页是后3页，显示后五页
        # 4、其他情况，显示当前页，前2页，后2页
        num_pages = paginator.num_pages  # 获取当前页数
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(num_pages - 2, num_pages + 3)  # 前闭后开，用3包含2

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]  # 只取前两个

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated:  # 是属性不是方法
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {
            'type': type,  # 种类信息
            'types': types,  # 分类信息
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'pages': pages,
            'sort': sort
        }

        return render(request, 'list.html', context)
    # context 用于传输上下文 ，否则会与NoReverseMatch的报错
