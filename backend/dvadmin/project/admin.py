from django.contrib import admin
from dvadmin.project.models import AppGroup, App, Domain


@admin.register(AppGroup)
class AppGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    pass


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass
