"""
本项目的一些基类documents
"""
from aiomotorengine import Document
from aiomotorengine import ReferenceField, StringField

from dtlib.tornado.base_docs import OrgUserDataDocument


class Project(OrgUserDataDocument):
    """
    测试项目,用于自动化的处理的
    """
    __collection__ = "test_project"
    __lazy__ = False

    project_name = StringField()  # 项目名称
    mark = StringField()  # 项目描述

    def set_template(self):
        self.project_name = 'xtest-demo'
        self.mark = 'project for first demo'



class ProjectBaseDocument(Document):
    """
    组织的数据信息
    """
    project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    p_name = StringField()  # 项目名称,冗余

    async def set_project_tag(self, project):
        """
        设置项目标记
        :type project: Project
        :return: 
        """

        self.project = project
        self.p_name = project.project_name
