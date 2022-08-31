from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('user', views.UserViewset, 'user')

urlpatterns = []

urlpatterns += router.urls
