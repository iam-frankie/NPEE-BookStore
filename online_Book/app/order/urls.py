from .views import OrderPlaceView, OrderCommitView, CommentView, OrderPayView, CheckPayView
from django.urls import path, re_path

urlpatterns = [
    path("place", OrderPlaceView.as_view(), name="place"),  # 提交订单页面显示
    path('commit', OrderCommitView.as_view(), name='commit'),  # 订单提交
    path('pay', OrderPayView.as_view(), name='pay'),  # 订单支付
    path('check', CheckPayView.as_view(), name='check'),  # 订单校对
    #    re_path(r'comment/(?P<order_id>.+)', CommentView.as_view(), name='comment'),  # 订单评论
]
