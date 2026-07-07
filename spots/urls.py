from django.urls import path

from spots import views

app_name = 'spots'

urlpatterns = [
    path('', views.ParkingSpotListView.as_view(), name='list'),
]
