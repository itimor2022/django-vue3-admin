# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 序列化管理
"""
from rest_framework import serializers

from dvadmin.asset.models import Isp, Account, Host
from dvadmin.utils.serializers import CustomModelSerializer


class IspSerializer(CustomModelSerializer):
    """
    云账号-序列化器
    """

    class Meta:
        model = Isp
        fields = '__all__'
        read_only_fields = ["id"]


class AccountSerializer(CustomModelSerializer):
    """
    云账号-序列化器
    """

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ["id"]


class HostSerializer(CustomModelSerializer):
    """
    主机-序列化器
    """

    class Meta:
        model = Host
        fields = '__all__'
        read_only_fields = ["id"]
