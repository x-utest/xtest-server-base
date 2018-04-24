"""
- 账号系统的功能
"""
from bson import ObjectId
from pymongo import DESCENDING

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
