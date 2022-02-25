"""online_Book URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.urls import path, include
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),  # 富文本编辑器
    path('search', include('haystack.urls')),  # 搜索界面
    path('user/', include(('user.urls', 'user'), namespace='user')),    #用户模块
    path('order/', include(('order.urls', 'order'), namespace='order')),  #订单模块
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),   #购物模块
    path('', include(('goods.urls', 'goods'), namespace='goods')),  # 书籍商品模块
]
# path('common/', include('common.urls', namespace='common')),  # 通用模块
# path('', include('app.common.urls')),
# path('user/', include('app.user.urls')),
# path('order/', include('app.order.urls')),
# path('cart/', include('app.cart.urls')),
# path('goods', include('app.goods.urls')),
# 登记了绝对路径后，URL文件位置可简写
# path('', include('common.urls')),
# ('polls.urls', "polls")