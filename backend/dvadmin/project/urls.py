from django.urls import path, re_path
from rest_framework import routers

from dvadmin.project.views import get_domain, AppViewSet, AppGroupViewSet, DomainViewSet

project_url = routers.SimpleRouter()
project_url.register(r'app', AppViewSet)
project_url.register(r'appgroup', AppGroupViewSet)
project_url.register(r'domain', DomainViewSet)

urlpatterns = [
    re_path('^get_domain/', get_domain),
]
urlpatterns += project_url.urls
