from aiomotorengine import StringField, IntField, ReferenceField, BooleanField

from dtlib.aio.base_mongo import MyDocument
from dtlib.tornado.account_docs import User


class AclGroups(MyDocument):
    """
    权限相关分组
    """
    __collection__ = "acl_groups"

    code = StringField(unique=True, required=True)  # 英文代号
    name = StringField()


class Permissions(MyDocument):
    """
    ACL的权限表
    """
    __collection__ = "acl_perm"
    __lazy__ = False

    control = StringField()  # 控制器的名称
    group = ReferenceField(reference_document_type=AclGroups)
    g_name = StringField()  # 冗余
    # u_acc = IntField()  # 用户访问
    g_acc = BooleanField()  # 小组访问
    o_acc = IntField()  # 其它用户


class UserGrpRel(User):
    """
    用户和组的关系,用户:组,N:1
    """

    __collection__ = "user_grp_rel"

    __lazy__ = False

    # group = ReferenceField(reference_document_type=AclGroups)
    g_code = StringField()
    g_name = StringField()  # 冗余
    user = ReferenceField(reference_document_type=User)
    u_name = StringField()  # 冗余
