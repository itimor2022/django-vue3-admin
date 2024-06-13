# -*- coding: utf-8 -*-

"""
@author: H0nGzA1
@contact: QQ:2505811377
@Remark: 序列化管理
"""
from rest_framework import serializers

from dvadmin.project.models import App, AppGroup, Domain
from dvadmin.utils.serializers import CustomModelSerializer


class AppGroupSerializer(CustomModelSerializer):
    """
    应用分组-序列化器
    """
    parent_name = serializers.CharField(read_only=True, source='parent.name')
    status_label = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()
    hasChild = serializers.SerializerMethodField()

    def get_hasChild(self, instance):
        hasChild = AppGroup.objects.filter(parent=instance.id)
        if hasChild:
            return True
        return False

    def get_status_label(self, obj: AppGroup):
        if obj.status:
            return "启用"
        return "禁用"

    def get_has_children(self, obj: AppGroup):
        return AppGroup.objects.filter(parent_id=obj.id).count()

    class Meta:
        model = AppGroup
        fields = '__all__'
        read_only_fields = ["id"]


class AppSerializer(CustomModelSerializer):
    """
    应用-序列化器
    """

    class Meta:
        model = App
        fields = '__all__'
        read_only_fields = ["id"]


class DomainSerializer(CustomModelSerializer):
    """
    域名-序列化器
    """

    class Meta:
        model = Domain
        fields = '__all__'
        read_only_fields = ["id"]
