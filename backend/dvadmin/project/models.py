import hashlib
import os

from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix


class AppGroup(CoreModel):
    name = models.CharField(max_length=64, verbose_name="分组名称", help_text="分组名称")
    key = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="关联字符",
                           help_text="关联字符")
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    owner = models.CharField(max_length=32, verbose_name="负责人", null=True, blank=True, help_text="负责人")
    phone = models.CharField(max_length=32, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")
    email = models.EmailField(max_length=32, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    status = models.BooleanField(default=True, verbose_name="分组状态", null=True, blank=True, help_text="分组状态")
    parent = models.ForeignKey(
        to="AppGroup",
        on_delete=models.CASCADE,
        default=None,
        verbose_name="上级分组",
        db_constraint=False,
        null=True,
        blank=True,
        help_text="上级分组",
    )

    @classmethod
    def recursion_all_group(cls, group_id: int, group_all_list=None, group_list=None):
        """
        递归获取分组的所有下级分组
        :param group_id: 需要获取的id
        :param group_all_list: 所有列表
        :param group_list: 递归list
        :return:
        """
        if not group_all_list:
            group_all_list = AppGroup.objects.values("id", "parent")
        if group_list is None:
            group_list = [group_id]
        for ele in group_all_list:
            if ele.get("parent") == group_id:
                group_list.append(ele.get("id"))
                cls.recursion_all_group(ele.get("id"), group_all_list, group_list)
        return list(set(group_list))

    class Meta:
        db_table = table_prefix + "project_group"
        verbose_name = "分组表"
        verbose_name_plural = verbose_name


class App(CoreModel):
    name = models.CharField(max_length=64, db_index=True, verbose_name="名称", help_text="名称")
    use = models.CharField(max_length=50, verbose_name="用处", null=True, blank=True, help_text="用处")
    group = models.ForeignKey(
        to="AppGroup",
        verbose_name="所属分组",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属分组",
    )
    sort = models.IntegerField(default=1, verbose_name="显示排序", help_text="显示排序")
    user = models.CharField(max_length=32, null=True, blank=True, verbose_name="负责人", help_text="负责人")
    contact = models.CharField(max_length=32, null=True, blank=True, verbose_name="联系方式", help_text="联系方式")
    bt_domain = models.CharField(max_length=150, null=True, blank=True, verbose_name="宝塔域名", help_text="宝塔域名")
    bt_user = models.CharField(max_length=150, null=True, blank=True, verbose_name="宝塔账号", help_text="宝塔账号")
    bt_password = models.CharField(max_length=150, null=True, blank=True, verbose_name="宝塔密码", help_text="宝塔密码")

    class Meta:
        db_table = table_prefix + "project_app"
        verbose_name = "应用表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)


class Domain(CoreModel):
    DOMAIN_TYPES = (
        (0, 'admin域名'),
        (1, 'h5域名'),
        (2, 'www域名'),
        (3, 'download域名'),
        (4, 'landing域名'),
        (5, 'agent域名'),
    )
    type = models.SmallIntegerField(choices=DOMAIN_TYPES, default=1, verbose_name='域名类型', null=True,
                                    blank=True, help_text="域名类型")
    group = models.ForeignKey(
        to="AppGroup",
        verbose_name="所属分组",
        on_delete=models.PROTECT,
        db_constraint=False,
        null=True,
        blank=True,
        help_text="所属分组",
    )
    domain = models.CharField(max_length=150, null=True, blank=True, verbose_name="域名", help_text="域名")
    username = models.CharField(max_length=150, null=True, blank=True, verbose_name="域名账号", help_text="域名账号")
    password = models.CharField(max_length=150, null=True, blank=True, verbose_name="域名密码", help_text="域名密码")
    status = models.BooleanField(default=True, verbose_name="域名状态", null=True, blank=True, help_text="域名状态")

    class Meta:
        db_table = table_prefix + "domains"
        verbose_name = "域名表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
