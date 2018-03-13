"""
企业组织所共享的资源:

1. ssh-key
#. 服务器

其它：
#. 图书
#. 电脑设备
"""
from aiomotorengine import StringField
from dtlib.aio.base_mongo import MyDocument
from dtlib.tornado.base_docs import OrgUserDataDocument


class InfoAsset(OrgUserDataDocument):
    """
    企业组织的信息资产设备，主要是服务器
    """
    __collection__ = "info_asset"

    ip_addr = StringField()  # IP地址
    usage = StringField()  # 使用备注


class AuthCallbackPage(OrgUserDataDocument):
    """
    第三方认证后回调的页面
    """
    __collection__ = "auth_cb_page"

    url = StringField()  # 回调url
    name = StringField()  # 此应用页面的名称，要显示的
    mark = StringField()  # 备注

    def set_template(self):
        self.url = 'http://www.baidu.com'
        self.name = '本系统名称'
        self.mark = '这里面是这个系统的描述'


class Sshkey(OrgUserDataDocument):
    """
    ssh-key
    """
    __collection__ = "user_ssh_key"
    name = StringField()  # key的名称代号
    sshkey = StringField()  # sshkey,pub
    mark = StringField()  # 标记


class SdkDemoCallCounts(OrgUserDataDocument):
    """
    企业的SDK页面的调用情况统计(waste)
    """

    __collection__ = 'sdk_demo_call_counts'


class SdkDemoCallDetail(MyDocument):
    """
    企业的SDK页面的调用情况统计的历史记录
    """

    __collection__ = 'sdk_demo_call_detail'
