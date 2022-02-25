from django.urls import path,re_path
from django.contrib.auth.decorators import login_required
from . import views
from .views \
    import RegisterView, ActiveView, LoginView, \
    UserInfoView, UserOrderView, AddressView, LoginOutView

urlpatterns = [  # 指明路径，调用的页面，还有名称
    # path("register", views.register, name="register"),  # 注册
    # path("register_handle", views.register_handle, name='register_handle'),  # 注册处理
    path("register", RegisterView.as_view(), name="register"),  # 注册-类视图注册
    # register是从父类默认继承的方法
    path("active/<token>", ActiveView.as_view(), name="active"),  # 用户激活
    # 在Django2中直接采用 path("active/<token>"方式将后面的字符直接提取并存储在token中
    path("login", LoginView.as_view(), name="login"),  # 登录
    path("logout", LoginOutView.as_view(), name="logout"),  # 登出
    # 使用了utils里用Mixin包装了一下的loginrequired之后便可以简化一下
    # path("", login_required(UserInfoView.as_view()), name="user"),  # 用户信息
    #
    # path("order", login_required(UserOrderView.as_view()), name="order"),  # 订单信息
    #
    # path("address", login_required(AddressView.as_view()), name="address"),  # 地址信息

    path("", UserInfoView.as_view(), name="user"),  # 用户中心-用户信息页

    # path("order", UserOrderView.as_view(), name="order"),  # 用户中心-订单信息页
    re_path(r'order/(?P<page>\d+)', UserOrderView.as_view(), name='order'),  # 用户中-订单信息页

    path("address", AddressView.as_view(), name="address"),  # 用户中心-地址信息页
]
