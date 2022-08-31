from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('font', views.FontViewSet, 'font')

urlpatterns = []

urlpatterns += router.urls
