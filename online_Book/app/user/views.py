from django.shortcuts import render, redirect
from django.urls import reverse  # 从Django2.0版本开始，导入reverse采用此方式
from django.core.mail import send_mail
from django.core.paginator import Paginator

from django.http import HttpResponse
from django.views.generic import View
from .models import User, Address
from goods.models import GoodsSKU  # 此报错可忽略，系统未识别相对路径信息
from order.models import OrderInfo, OrderGoods
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  # 使用模块中进行Web数据加密的模块
# 两大功能 -1、加密
from itsdangerous import SignatureExpired
# -2、设置有效时限，逾期重新发送激活消息
from django.conf import settings  # 借助Django内置的settings
from celery_tasks.tasks import send_register_active_mail
from django.contrib.auth import authenticate, login, logout  # 直接使用函数保存
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection
import re


# Create your views here.
# 1-注册直接版
# /user/register/
def register(request):
    """显示注册界面"""
    if request.method == 'GET':
        # 显示注册页面
        return render(request, 'register.html')  # 获取请求，返回Register页面
    elif request.method == 'POST':
        """进行注册处理"""
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        # 使用DJango自带的密码加密手法
        email = request.POST.get('email')  # 获取名字对应HTML页面里name的名字
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):  # 判断是否数据完整
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):  # 输入的邮箱，进行正则匹配
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)  # 摒弃传统注册方式，直接调用内置的存储构造方法
        user.is_active = False  # 注册状态，默认为假
        user.save()

        # 返回应答,跳转首页
        return redirect(reverse('goods:index'))
        # 调用goods里的index方法，用到了反向解析，方便调用并跳转到goods中的界面，因为默认是user/XXXX


# 2-注册优化版
# 上面已经将注册处理和加载页面进行了合并，使得URL合二为一更加简洁
def register_handle(request):
    """进行注册处理"""
    # 接受数据
    username = request.POST.get('user_name')
    password = request.POST.get('pwd')
    # 使用DJango自带的密码加密手法
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 进行数据校验
    if not all([username, password, email]):  # 判断是否数据完整
        # 数据不完整
        return render(request, 'register.html', {'errmsg': '数据不完整'})
    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):  # 输入的邮箱，进行正则匹配
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '请同意协议'})
    # 校验用户名是否重复
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        # 用户名不存在
        user = None
    if user:
        # 用户名已存在
        return render(request, 'register.html', {'errmsg': '用户名已存在'})
    # 进行业务处理：进行用户注册
    user = User.objects.create_user(username, email, password)  # 摒弃传统注册方式，直接调用内置的存储构造方法
    user.is_active = False  # 注册状态，默认为假
    user.save()

    # 返回应答,跳转首页
    return redirect(reverse('goods:index'))
    # 调用goods里的index方法，用到了反向解析，方便调用并跳转到goods中的界面，因为默认是user/XXXX


# 3、注册、利用Django内置模块优化版
# /user/register
class RegisterView(View):
    '''注册类'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        # 使用DJango自带的密码加密手法
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):  # 判断是否数据完整
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):  # 输入的邮箱，进行正则匹配
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)  # 摒弃传统注册方式，直接调用内置的存储构造方法
        user.is_active = False  # 注册状态，默认为假
        user.save()
        print('用户新建！！！！')

        # 发送激活邮件，包含激活链接：http://127.0.0.1:8000/user/active/1
        # 激活链接中需要包含用户的身份信息，并且要把身份信息进行加密
        # It's dangerous模块进行加密

        # 加密用户的身份信息，生成激活的token
        serializer = Serializer(settings.SECRET_KEY, 3600)

        info = {'confirm': user.id}
        print('用户新建成功', end='')
        print(user.id)

        token = serializer.dumps(info)  # bytes数据
        token = token.decode()  # 默认解码方式是UTF-8

        print('加密成功', end='')
        print(token)

        # 发邮件
        send_register_active_mail.delay(email, username, token)  # delay放入任务队列

        # subject = "研途无忧欢迎信息"
        # message = ''
        # # 使用HTML_Message才能解析HTML语言，显示出该有的样式
        # html_message = '<h1>%s,欢迎您成为研途无忧注册会员</h1>' \
        #                '请点击以下链接激活您的账户<br/>' \
        #                '<a href="http://127.0.0.1:8000/user/active/%s">' \
        #                'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)  # 邮件正文
        # sender = settings.EMAIL_FROM  # 引用setting中的Email_FROM设置
        # receiver = [email]
        # send_mail(subject, message, sender, receiver, html_message=html_message)

        # 返回应答,跳转首页
        return redirect(reverse('goods:index'))
        # 调用goods里的index方法，用到了反向解析，方便调用并跳转到goods中的界面，因为默认是user/XXXX


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        """进行用户激活"""
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        print('解密器创建成功', end='')

        try:
            info = serializer.loads(token.encode())
            user_id = info['confirm']
            print('成功获取用户id', end='')
            print(user_id)

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            print('激活成功', end='')
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')


# /user/login
class LoginView(View):
    """登录"""

    def get(self, request):
        """显示登录页面"""
        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 可以使用模板

        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            print(username)
            print(password)
            return render(request, 'login.html', {'errmsg': '数据不完整'})
        # 业务处理：登录校验
        # 常规操作 User.objects.get(username=username, password=password)
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户若已激活
                # 记录用户登录状态
                login(request, user)

                # 获取登录后所要跳转的页面地址
                # 默认跳转到首页地址
                next_url = request.GET.get('next', reverse('goods:index'))
                # 重定向页面如上：若get到链接则进入，但默认情况下进入good/index
                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名字
                remember = request.POST.get('remember')
                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)  # 分配缓存，存储用户名
                else:
                    response.delete_cookie('username')
                # 返回response
                return response
            else:
                print("用户未激活")
                return render(request, 'login.html', {'errmsg': '请激活您的账户'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

        # 返回应答


# /user/logout
class LoginOutView(View):
    """退出登录"""

    def get(self, request):  # 使用内置认证系统
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))


# 三用户页面的显示
# /user
class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页面"""

    def get(self, request):
        """显示"""
        # page =  'user'：
        # request.user.is.authenticated()-以下两个类都有这个方法
        # 如果用户登录->User类的一个实例->true
        # 如果用户未登录->AnonymousUser类的一个实例->false

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # 1、传统方法
        # from redis import StrictRedis
        # con = StrictRedis(host='127.0.0.1', port='6379', db='9')
        con = get_redis_connection('default')

        # 取出用户的历史浏览记录
        history_key = 'history_%d' % user.id  # %d用user.id替换

        # 获取用户最新浏览的5个商品id
        sku_ids = con.lrange(history_key, 0, 4)  # [2, 3, 1]，取出0-4前五条信息

        # 从数据库中查询用户浏览的商品其具体信息
        # goods_li = GoodsSKU.objects.filter(id_in=sku_ids)
        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li
                   }

        # 除了传递给模板文件的模板变量外，Django本身也会将request.user也传给模板文件
        return render(request, 'user_center_info.html', context)


# /user/order
class UserOrderView(LoginRequiredMixin, View):
    '''用户中心-订单页'''

    def get(self, request, page):
        '''显示'''
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount,保存订单商品的小计
                order_sku.amount = amount

            # 动态给order增加属性，保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        # 使用模板
        return render(request, 'user_center_order.html', context)


# /user/address
class AddressView(LoginRequiredMixin, View):
    '''用户中心-地址页'''

    def get(self, request):
        '''显示'''
        # 获取登录用户对应User对象
        user = request.user

        # 获取用户的默认收货地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True)  # models.Manager
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        # 使用模板
        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone, type]):
            print("数据不完整")
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            print("手机号码格式不对")
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))  # get请求方式
