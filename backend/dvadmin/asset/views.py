# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 视图管理
"""

from dvadmin.asset.models import Isp, Account, Host
from dvadmin.asset.serializers import IspSerializer, AccountSerializer, HostSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class IspViewSet(CustomModelViewSet):
    """
    ISP管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Isp.objects.all()
    serializer_class = IspSerializer
    filter_fields = []
    search_fields = ['name', 'key']


class AccountViewSet(CustomModelViewSet):
    """
    账号管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    search_fields = ['username', 'use']


class HostViewSet(CustomModelViewSet):
    """
    主机管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    filter_fields = ['group', 'region']
    search_fields = ['hostname', 'ip', 'int_ip']
