from django.urls import path
from . import views

app_name = 'contabil'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('partidas/', views.PartidaListView.as_view(), name='partida-list'),
    path('partidas/<int:pk>/', views.PartidaDetailView.as_view(), name='partida-detail'),
    path('partidas/nova/', views.PartidaCreateView.as_view(), name='partida-create'),
    path('partidas/<int:pk>/editar/', views.PartidaUpdateView.as_view(), name='partida-update'),
    path('partidas/<int:pk>/excluir/', views.PartidaDeleteView.as_view(), name='partida-delete'),
]
