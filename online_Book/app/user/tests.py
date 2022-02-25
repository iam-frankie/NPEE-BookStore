from django.test import TestCase, override_settings, Client
from django.urls import resolve
from django.http import HttpRequest

from .models import User


# Create your tests here.


class UserViewTestCase(TestCase):
    # 注册测试页面
    def user_register_test(self):
        self.client = Client()
        rep = self.client.get('/user/register')  # 请求访问注册页
        self.assertEqual(rep.status_code, 200)  # 判断返回状态码
        self.assertContains(rep, 'content')  # 判断是否有返回页面内容

    # 测试用户存在性
    def user_exist_test(self):
        rep = self.client.get('/user/register_exist/?uname=frank')  # 判断用户frank是否存在
        self.assertEqual(rep.status_code, 200)  # 判断返回状态码
        self.assertIs(rep, rep, {'count': 1})  # 返回json数据一致性

    # 测试用户登录
    def user_login_test(self):
        rep = self.client.get('/user/login/')  # 请求登录页
        self.assertEqual(rep.status_code, 200)  # 判断返回状态码
        # 以POST方式模拟登录，用户名：11，密码：66668888
        login_status = self.client.post('/user/login', {'username': 'frank', 'pwd': 'chengtong1999'})
        # 如果数据库查询时，发现用户名和密码正确，返回正常状态码200
        self.assertEqual(login_status.status_code, 200)

    # 测试用户的信息界面
    def user_info_test(self):
        rep = self.client.get('/user/info')  # 请求访问用户信息
        # 当未登录时，返回状态码302.这时url重定向
        self.assertEqual(rep.status_code, 302)
        self.assertEqual(rep['location'], 'user/login/')
        # 判断处理该url请求的视图是否正确
        found = resolve('user/info')
        self.assertEqual(found.func.user_center_info)
