from django.urls import path

from . import views

urlpatterns = [
    path('report/', views.ReportList.as_view()),
    path('report/<str:pk>/', views.ReportDetail.as_view()),
    path('report/<str:pk>/generate/', views.generate_report, name='generate'),
    path('report/<str:pk>/download/', views.download_report, name='download'),
]
