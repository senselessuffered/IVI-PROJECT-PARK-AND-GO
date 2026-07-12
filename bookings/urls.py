from django.urls import path

from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='list'),
    path('new/', views.BookingCreateView.as_view(), name='create'),
    path('busy-hours/', views.BusyHoursView.as_view(), name='busy_hours'),
    path('free-spots/', views.FreeSpotsView.as_view(), name='free_spots'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.BookingUpdateView.as_view(), name='edit'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('<int:pk>/delete/', views.BookingDeleteView.as_view(), name='delete'),
]
