from django.urls import path

from . import views

urlpatterns = [
    path('user/', views.UserList.as_view()),
    path('user/<str:pk>/', views.UserDetail.as_view()),
]
