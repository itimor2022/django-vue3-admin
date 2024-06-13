from django.contrib import admin
from dvadmin.system.models import Users, Role, Dept


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Dept)
class DeptAdmin(admin.ModelAdmin):
    pass
