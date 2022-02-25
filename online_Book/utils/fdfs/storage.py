

from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.conf import settings


class FDFS_storage(Storage):
    """文件存储类"""

    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = get_tracker_conf(settings.FDFS_CLIENT_CONF)
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url


    def open(self, name, mode='rb'):
        """打开文件时使用"""
        pass

    def save(self, name, content, max_length=None):
        """保存文件时使用"""
        # name：所选择的上传文件的名字
        # content:包含上传文件内容的File对象

        # 创建一个Fdfs_client对象
        # client = Fdfs_client('./utils/fdfs/client.conf')
        client = Fdfs_client(self.client_conf)

        # 上传文件到fdfs系统中
        res = client.upload_appender_by_buffer(content.read())

        # @return dict {
        #     'Group name'      : group_name,
        #     'Remote file_id'  : remote_file_id,
        #     'Status'          : 'Upload successed.',
        #     'Local file name' : '',
        #     'Uploaded size'   : upload_size,
        #     'Storage IP'      : storage_ip
        # } if success else None

        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到 Fast DFS 失败')
        # 获取返回文件的id
        filename = res.get('Remote file_id')

        return filename.decode()

    def exists(self, name):
        """Django判断文件名是否可用"""
        return False

    def url(self, name):
        """返回访问文件的URL路径"""
        # return 'http://192.168.2.8:8888/' + name
        # return name
        return self.base_url+name
