# 使用celery
import os
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader, RequestContext
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
# 此报错可忽略，系统未识别相对路径信息


import time

# 创建一个Celery的实例对象

app = Celery('celery_tasks.tasks', broker='redis://:chengtong1999@127.0.0.1:6379/8')


# 定义任务函数
@app.task  # 使用task方法进行装饰,等于是丰富完整了task里头的方法（封装），方便发邮件时使用
def send_register_active_mail(to_email, username, token):
    """发送激活邮件"""
    # 组织邮件信息
    subject = "研途无忧欢迎信息"
    message = ''
    # 使用HTML_Message才能解析HTML语言，显示出该有的样式
    html_message = '<h1>%s,欢迎您成为研途无忧注册会员</h1>' \
                   '请点击以下链接激活您的账户<br/>' \
                   '<a href="http://127.0.0.1:8000/user/active/%s">' \
                   'http://127.0.0.1:8000/user/active/%s</a>' % (username, token, token)  # 邮件正文
    sender = settings.EMAIL_FROM  # 引用setting中的Email_FROM设置
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)


@app.task
def generate_static_index_html():
    """用于产生首页静态页面"""
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types: # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {'types': types,
                'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')
    # # 2.定义模板上下文-->可以省略
    # context = RequestContext(request, context)
    # 2.模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:     # write表示写文件
        f.write(static_index_html)

