from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('receive-email/', views.receive_email, name='receive_email'),
]