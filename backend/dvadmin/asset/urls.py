from django.urls import path
from rest_framework import routers

from dvadmin.asset.views import IspViewSet, AccountViewSet, HostViewSet

asset_url = routers.SimpleRouter()
asset_url.register(r'isp', IspViewSet)
asset_url.register(r'account', AccountViewSet)
asset_url.register(r'host', HostViewSet)

urlpatterns = [
]
urlpatterns += asset_url.urls
