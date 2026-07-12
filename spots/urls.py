from django.urls import path

from spots import views

app_name = 'spots'

urlpatterns = [
    path('', views.ParkingSpotListView.as_view(), name='list'),
    path('<int:pk>/', views.ParkingSpotDetailView.as_view(), name='detail'),
]
