from django.urls import path

from . import views

urlpatterns = [
    path('font/', views.FontList.as_view()),
    path('font/<int:pk>/', views.FontDetail.as_view()),
    path('font/scan/', views.scan_all_fonts),
]
