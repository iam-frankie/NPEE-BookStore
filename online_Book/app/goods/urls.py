from django.urls import path, re_path
from django.conf.urls import url
from .views import IndexView, DetailView, ListView

urlpatterns = [
    # path('index/', IndexView.as_view(), name='index'),  # 首页
    url(r'^index/$', IndexView.as_view(), name='index'),  # 首页
    # path("goods/<goods_id>d+", DetailView.as_view(), name='detail'),  # 详情页
    # url(r'^goods/(?P<goods_id>\\d+)$', DetailView.as_view(), name='detail'),  # 详情页
    re_path(r'goods/(?P<goods_id>\d+)', DetailView.as_view(), name='detail'),  # 详情页

    # path("goods/<goods_id>", DetailView.as_view(), name='detail'),
    # re_path('page=(?P<goods_id>\d+)&key=(?P<key>\w+)', DetailView.as_view(), name="detail"),

    # url(r'^list/(?P<type_id>\\d+)/(?P<page>\\d+)$', ListView.as_view(), name='list'),  # 列表页
    re_path(r'list/(?P<type_id>\d+)/(?P<page>\d+)', ListView.as_view(), name='list'),  # 列表页
    # d+:匹配一个种类的id

    # re_path(r'index/(\d+)/',views.index),
]
