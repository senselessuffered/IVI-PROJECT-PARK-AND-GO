from django.urls import path

from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='list'),
    path('booking/new/', views.BookingCreateView.as_view(), name='create'),
    path('booking/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='edit'),
    path('booking/<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('booking/<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('booking/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='delete'),
]
