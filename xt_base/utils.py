"""
- 账号系统的功能
"""
import hashlib

from bson import ObjectId
from dtlib.randtool import get_uuid1_key
from dtlib.tornado.account_docs import User, Organization, UserOrgRelation
from dtlib.tornado.docs import TestDataApp
from dtlib.tornado.status_cls import UserStatus
from pymongo import DESCENDING

from xt_base.document.base_docs import Project

import math
from dtlib import jsontool
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData
from dtlib.web.tools import get_std_json_response


def wrap_org_tag(origin_dict, org_id):
    """
    包装加上组织信息
    :param org_id:
    :type org_id:str
    :return:
    """
    org_obj_id = ObjectId(str(org_id))
    origin_dict.update(organization=org_obj_id)
    return origin_dict


def wrap_project_tag(origin_dict, project):
    """

    :param origin_dict:
    :param project: Project的aio orm
    :type project:Project
    :return:
    """
    origin_dict.update(pro_id=project['_id'])  # 转化为ObjectId保存
    origin_dict.update(pro_name=project['project_name'])
    return origin_dict


async def get_org_data_paginator(self, *args, **kwargs):
    """
    直接传入项目名称和表的名称,返回分页的信息
    :param self:
    :param args:
    :param kwargs:col_name
    :return:
    """
    page_idx = self.get_argument("page_idx", '1')
    page_cap = self.get_argument('page_cap', '20')  # 一页的记录容量-var
    page_idx = int(page_idx)
    page_size = int(page_cap)  # 一页显示40条数据

    col_name = kwargs.get('col_name', None)
    pro_id = kwargs.get('pro_id', None)
    hide_fields = kwargs.get('hide_fields', None)  # 需要隐藏的字段,一个dict
    """:type:dict"""

    if list_have_none_mem(*[col_name, ]):
        return ConstData.msg_args_wrong

    # col_name = 'unit_test_data'

    mongo_coon = self.get_async_mongo()
    mycol = mongo_coon[col_name]

    user_org = await self.get_organization()
    """:type:Organization"""

    if user_org is None:
        return ConstData.msg_none

    if pro_id is None:
        msg_details = mycol.find({
            "organization": ObjectId(user_org),
            "is_del": False
        }, hide_fields).sort([('rc_time', DESCENDING)])  # 升序排列
    else:
        msg_details = mycol.find({
            "organization": ObjectId(user_org),
            'pro_id': ObjectId(str(pro_id)),
            "is_del": False
        }, hide_fields).sort([('rc_time', DESCENDING)])  # 升序排列

    msg_details_cnt = await msg_details.count()
    msg_details = msg_details.skip(page_size * (page_idx - 1)).limit(page_size)  # 进行分页

    total_page = math.ceil(msg_details_cnt / page_size)  # 总的页面数
    # dlog.debug('total page:%s' % total_page)
    # dlog.debug('msg_details.count():%s' % msg_details_cnt)

    msg_content_list = await msg_details.to_list(page_size)

    page_res = dict(
        page_idx=page_idx,
        page_total_cnts=total_page,
        page_cap=page_size,
        page_data=msg_content_list
    )

    return get_std_json_response(data=jsontool.dumps(page_res, ensure_ascii=False))


async def get_org_data(self, **kwargs):
    """
    获取本组织私有的数据
    :param self:
    :type self BaseHandler
    :param kwargs:
    :return:
    """
    collection = kwargs.get('collection', None)
    project_id = kwargs.get('pro_id', None)
    org = await self.get_organization()

    if org is None:
        return None

    db = self.get_async_mongo()
    col = db[collection]

    # 用project做筛选
    if project_id is not None:
        project_obj_id = ObjectId(str(project_id))
        data = dict(
            organization=ObjectId(org),
            project=project_obj_id,
            is_del=False
        )
    else:
        # 没有做筛选
        data = dict(
            organization=ObjectId(org),
            is_del=False
        )
    org_data = col.find(data).sort([('rc_time', DESCENDING)])
    org_cnt = await org_data.count()
    return await org_data.to_list(org_cnt)


def user_id_is_legal(user_id):
    """
    id检查

    - 不小于6位
    - 只能是数字,字母，下划线组合

    :param passwd:
    :return:
    """

    if len(user_id) < 6:
        return False

    # todo 还有其它更严格的检查
    return True


async def create_default_sys_user_by_wechat(
        default_new_user_id,
        default_user_name):
    """
    根据新入系统的微信登录信息,创建默认的用户及相关组织关系
    :return:
    """

    new_user = User(
        user_id=default_new_user_id,
        # salt=rand_salt,  # 防止别人md5撞库反向破解的随机数
        # passwd=StringField()  # 密码,通过第三方登录的默认不设置
        nickname=default_user_name,
        status=UserStatus.init,  # 表示是可更改状态
        active=True,
    )
    new_user.set_default_rc_tag()

    sys_user = await new_user.save()
    """:type:User"""

    # 为新用户建立默认的小组
    default_org = await create_dft_organization(sys_user, is_default=True)
    """:type:Organization"""

    # 建立它们的默认关系
    await create_dft_org_rel(sys_user, default_org,
                             is_default=True, is_current=True,
                             is_activate=True, is_owner=True)

    # 建立默认的自动化应用app,属于组织
    await create_org_app(default_org)

    await create_dft_project(sys_user, default_org)  # 创建一个默认的项目

    return sys_user


async def create_dft_project(sys_user, org):
    """
    创建本组织的demo项目
    :param sys_user: 
    :param org: 
    :return: 
    """
    my_project = Project()
    my_project.set_template()
    my_project.set_user_tag(sys_user)
    my_project.set_org_tag(org)
    my_project.set_default_rc_tag()


async def create_org_app(default_org):
    """
    为组织创建应用app
    :param default_org: 
    :type org:Organization
    :return: 
    """

    default_test_app = TestDataApp()
    default_test_app.app_id = get_uuid1_key()
    default_test_app.app_key = hashlib.md5(get_uuid1_key().encode(encoding='utf-8')).hexdigest()
    default_test_app.organization = default_org  # 默认的组织
    default_test_app.o_name = default_org.name  # 冗余
    default_test_app.is_default = True  # 是默认设置的
    default_test_app.set_default_rc_tag()
    return await default_test_app.save()


async def create_dft_org_rel(user, org,
                             is_default=False,
                             is_current=False,
                             is_activate=True,
                             is_owner=True
                             ):
    """
    为组织和用户建立关联
    :param user: 
    :type user:User
    :type org:Organization
    :param org: 
    :return: 
    """
    # 建立它们的默认关系
    user_org_rel = UserOrgRelation()
    user_org_rel.organization = org
    user_org_rel.org_name = org.name  # 冗余
    user_org_rel.user = user
    user_org_rel.user_name = user.nickname  # 冗余
    user_org_rel.is_default = is_default  # 是默认建立的关联
    user_org_rel.is_current = is_current  # 默认是当前的数据
    user_org_rel.is_owner = is_owner  # 默认是有从属关系的
    user_org_rel.is_active = is_activate  # 自己和自己的组织是默认激活的
    user_org_rel.set_default_rc_tag()  # 打上默认时间标记
    return await user_org_rel.save()


async def create_dft_organization(user, is_default=False):
    """
    创建默认的组织
    :type user: User
    :parameter is_default:是否是模板组织
    :return: 
    """
    # 为新用户建立默认的小组
    default_org = Organization()
    default_org.set_template()
    default_org.set_default_rc_tag()

    default_org.owner = user
    default_org.owner_name = user.nickname  # 冗余
    default_org.is_default = is_default

    return await default_org.save()
