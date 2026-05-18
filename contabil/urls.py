from django.urls import path
from . import views

app_name = 'contabil'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]