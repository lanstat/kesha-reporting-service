from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('report', views.ReportViewSet, 'report')

urlpatterns = []

urlpatterns += router.urls
