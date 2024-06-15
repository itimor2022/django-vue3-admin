import hashlib
import os

from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix
from dvadmin.project.models import AppGroup


class Isp(CoreModel):
    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    key = models.CharField(max_length=64, unique=True, verbose_name="关键字符", help_text="关键字符")
    sort = models.IntegerField(default=1, verbose_name="顺序", help_text="顺序")

    class Meta:
        db_table = table_prefix + "asset_cloud"
        verbose_name = "服务器厂家"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class Account(CoreModel):
    username = models.CharField(max_length=150, db_index=True, verbose_name="账号",
                                help_text="账号")
    password = models.CharField(max_length=150, verbose_name="密码", help_text="密码")
    isp = models.ForeignKey(
        to="Isp",
        verbose_name="ISP",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="ISP",
    )
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    use = models.CharField(max_length=50, verbose_name="用处", null=True, blank=True, help_text="用处")

    class Meta:
        db_table = table_prefix + "asset_account"
        verbose_name = "服务商账号"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class Host(CoreModel):
    OS_TYPES = (
        (0, 'centos'),
        (1, 'windows'),
    )
    SERVER_TYPES = (
        (0, '物理机'),
        (1, '虚拟机'),
        (2, '云主机'),
    )
    REGION_CHOICES = (
        (0, "香港"),
        (1, "首尔"),
        (2, "新加坡"),
        (3, "东京"),
    )

    ASSET_STATUS = (
        (0, '已上线'),
        (1, '已停止'),
        (2, '已下线'),
        (3, '未使用'),
    )

    hostname = models.CharField(max_length=64, verbose_name="主机名称", help_text="主机名称")
    ip = models.GenericIPAddressField(verbose_name='外网IP', default='127.0.0.1', null=True, blank=True,
                                      help_text="外网IP")
    int_ip = models.GenericIPAddressField(verbose_name='内网IP', null=True, blank=True, help_text="内网IP")
    os = models.SmallIntegerField(choices=OS_TYPES, default=0, verbose_name='系统类型', null=True, blank=True,
                                  help_text="系统类型")
    group = models.ForeignKey(
        to=AppGroup,
        verbose_name="所属分组",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属分组",
    )
    server_type = models.SmallIntegerField(choices=SERVER_TYPES, default=2, verbose_name='服务器类型', null=True,
                                           blank=True, help_text="服务器类型")
    account = models.ForeignKey(
        to="Account",
        verbose_name="所属账号",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属账号",
    )
    region = models.IntegerField(
        choices=REGION_CHOICES, default=1, verbose_name="区域", null=True, blank=True, help_text="区域"
    )
    instance_type = models.SmallIntegerField(default=1, verbose_name="配置", null=True, blank=True, help_text="配置")
    status = models.IntegerField(
        choices=REGION_CHOICES, default=1, verbose_name="状态", null=True, blank=True, help_text="状态"
    )
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    use = models.CharField(max_length=50, verbose_name="用处", null=True, blank=True, help_text="用处")

    class Meta:
        db_table = table_prefix + "asset_host"
        verbose_name = "主机表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)
