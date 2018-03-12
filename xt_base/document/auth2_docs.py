"""
和token相关的docs
本模块的所有内容都只针对于认证模块的app
"""
from dtlib.tornado.base_docs import UserToken
from aiomotorengine import DateTimeField
from aiomotorengine import FloatField
from aiomotorengine import IntField
from aiomotorengine import ReferenceField
from aiomotorengine import StringField
from dtlib.aio.base_mongo import HttpDocument, ClientTypeDocument, MyDocument
from dtlib.tornado.account_docs import User
from dtlib.utils import list_have_none_mem

from xt_base.document.source_docs import OrgUserDataDocument


class ProductResource(MyDocument):
    """
    产品资源
    """

    __collection__ = 'product_resource'

    name = StringField()  # 消费资源的名称，这都是超级管理员级别的


class AuthUser(User):
    """
    目前先直接继承本用户体系的账号
    """
    __collection__ = "g_users"


# class EnterpriseAccount(User):
#     """
#     企业用户账号。
#     一个企业可以创建多个app应用
#     这些app应用共享用户池
#     """
#     __collection__ = 'auth_enterprise'


class AuthApp(OrgUserDataDocument, ClientTypeDocument):
    """
    开放应用程序,用于做身份认证的
    """

    __collection__ = "auth_app"
    __lazy__ = False

    appid = StringField(max_length=32, unique=True)  # 公钥
    secret = StringField(max_length=32, unique=True)  # 私钥
    callback = StringField()  # 可能是web回调的url或者是回调的app应用包名称,回调的域，用于安全性检查

    async def set_default_tag(self, **kwargs):
        """
        设置默认的标记
        :param kwargs:
        :return:
        """
        client_type = kwargs.get('client_type', None)
        http_req = kwargs.get('http_req', None)

        if list_have_none_mem(*[client_type, http_req]):
            return None

        await self.set_org_user_tag(http_req=http_req)
        self.set_client_type_tag(client_type=client_type)

        # super(AuthApp, self).set_default_rc_tag()
        return True


class ResourceGroup(MyDocument):
    """
    资源套餐组，不同的套餐组有不同的限额
    """
    __collection__ = 'resource_group'
    __lazy__ = False

    name = StringField()  # 小组名称


class OrgResourceGroupRelation(OrgUserDataDocument):
    """
    组织和资源组的关系，不同的资源组有不同的限额
    """

    __collection__ = 'org_resource_grp_rel'
    __lazy__ = False

    r_grp = ReferenceField(reference_document_type=ResourceGroup)
    rg_name = StringField()  # 冗余


class ResourceGroupLimit(OrgUserDataDocument):
    """
    每个账号的相应的资源的限额
    """

    __collection__ = 'resource_group_limit'
    __lazy__ = False

    resource = ReferenceField(reference_document_type=ProductResource)
    r_name = StringField()  # 冗余 ，资源名称
    limit = IntField()  # 目录创建的数目


class OrgResourceCnt(OrgUserDataDocument):
    """
    当前组织使用资源的情况
    """
    __collection__ = 'org_resource_cnt'
    __lazy__ = False

    resource = ReferenceField(reference_document_type=ProductResource)
    r_name = StringField()  # 冗余
    cnt = IntField()


# 正面都是系统数据，当然也有可能是业务数据

class MobileSafetyData(OrgUserDataDocument, HttpDocument,
                       # OperationDocument
                       ):
    """
    手机安全数据

    """

    __collection__ = 'mobile_safety_data'

    bs = StringField()  # charging battery status
    br = FloatField()  # 电池状态，"0.36",battery rate

    carrier = StringField()  # 运营商，"\U4e2d\U56fd\U8054\U901a";
    cellular = StringField()  # LTE;
    coun = StringField()  # CN;
    dn = StringField()  # "iPhone 6s"

    idf = StringField()  # 85BA4C9DD47C4EA7B60934GG116F7631;
    imei = StringField()  # 000000000000000;
    # ip = StringField()
    lang = StringField()  # "en-CN";
    sc_w = IntField()  # screen width
    sc_h = IntField()  # screen height
    # mScreen = StringField()  # 1242x2208;
    dType = StringField()  # iPhone;
    mac = StringField()  # "00:00:00:00:00:00";
    dModel = StringField()  # "iPhone8,2";
    osType = StringField()  # ios;
    # osVerInt =StringField()# "9.3.2";
    osVerRelease = StringField()  # "9.3.2";
    route = StringField()  # "24:b2:3c:e9:3:b1";
    ssid = StringField()  # My-WIFI;
    # utc = StringField()  # "2016-07-18 06:51:53";
    uuid = StringField()  # "513DE79D-F20A-4FAA-8F5B-2FD61B2F685A";

    c_time = DateTimeField()  # 客户端时间，东8时区

    # 下面是作为SDK时需要的字段
    # gsdkVerCode = "2.16.1.25.1.x";
    # hAppVerCode = 1;
    # hAppVerName = "1.0";


class MobileAuthPcToken(UserToken):
    """
    由未登录的PC端生成的二维码的原始串号:

    - 移动端扫码后在db中生成 map_token 和用户关联
    - db中针对此用户生成web_token
    - 更新对应的 access_token
    - pc端根据 web_token 去获取 access_token
    - 正常的调用

    备注:
    - 生存周期为2分钟,2分钟后过期删除
    - 没有被使用时,每1分钟变一次
    - 被使用后,立刻删除掉
    """

    __collection__ = 'ttl_map_token'
    __lazy__ = False

    appid = StringField()  # 创建此token的appid
    # callback = StringField()  # 冗余，当前auth_app的callback
    status = IntField()  # 认证过程的状态码


class AuthMobileSessionToken(UserToken):
    """
    认证手机保存的身份token，目前先不分开
    """
    # todo 后续要和真正的应用服务端分开
    __collection__ = 'auth_ttl_mobile_token'
    __lazy__ = False


class PrivateKeyShadowToken(UserToken):
    """
    私钥的token，这样做的目的是为了让私钥有一个可变性的替身:
    1. 在第三方应用程序A启动的时候，私钥使用一次获取此privateKeyToken
    2. 然后今后A应用通过此替身来获取auth的access_token权限
    3. 生存周期。如果不使用私钥来重新获取或者更新，就一直有效
    """
    __collection__ = 'auth_private_key_token'
    __lazy__ = False

    app_secret = StringField(max_length=32, unique=True)  # 外部的键值


class ThirdAuthToken(UserToken):
    """
    第三方平台认证后的token，相当于refresh_token功能。相当于session
    然后网站主可以获取第三方平台的用户信息。方便后续做独立的扩展。

    目前为了简单，就直接使用MobileAuthPcToken来替代其功能
    """
    __collection__ = 'ttl_third_auth_token'
    __lazy__ = False

    qrtoken = StringField()  # 来自于二维码的uuid


class AuthAccessToken(UserToken):
    """
    认证平台的access_token:
    目前和客户系统的 access_token共用

    - 生存周期：2小时
    - 可用私钥来刷新
    """

    __collection__ = 'ttl_access_token'
    __lazy__ = False
