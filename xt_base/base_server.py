from tornado.web import Application

from dtlib.tornado.base_hanlder import MyUserBaseHandler
from dtlib.tornado.const_data import FieldDict
from dtlib.web.valuedict import ValueDict

commentKeep_ValueDict = ValueDict(0, '')


class MyApplication(Application):
    """
    加入一些自定义的应用
    """

    def set_async_redis(self, async_rc_pool):
        """
        设置连接池
        :param async_rc_pool:
        :return:
        """
        self.settings[FieldDict.key_async_redis_pool] = async_rc_pool
        pass

    def set_sync_redis(self, sync_rc_pool):
        """
        获取同步类型的redis的连接池
        :return:
        """
        self.settings[FieldDict.key_sync_redis_pool] = sync_rc_pool
        pass

    def set_async_mongo(self, async_mongo_pool):
        """
        异步的mongo连接池
        :param async_mongo_pool:
        :return:
        """
        self.settings[FieldDict.key_async_mongo_pool] = async_mongo_pool


class MyBaseHandler(MyUserBaseHandler):
    """
    自定义session的类,基于tornado的

    - logsession是登录的token,使用mongodb来存储
    - sessionid使用redis来存储,以后用token,不用session了

    """

    def __init__(self, *args, **kwargs):
        super(MyBaseHandler, self).__init__(*args, **kwargs)
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie')
        self.set_header('Access-Control-Allow-Methods',
                        'POST, GET, OPTIONS')

    def set_http_tag(self):
        """
        设置http的标记
        :return:
        """
        new_tag = dict(
            ip = self.request.remote_ip,  # 客户端访问的IP
            user_agent = self.request.headers.get('User-Agent', None),
            cookie = self.request.headers.get('Cookie', None),
            referrer = self.request.headers.get('Referer', None)
        )
        return new_tag
