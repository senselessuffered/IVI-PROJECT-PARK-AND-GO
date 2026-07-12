from django.test import TestCase
from django.urls import reverse

from spots.models import ParkingSpot


class ParkingSpotUrlTests(TestCase):
    def setUp(self):
        self.spot = ParkingSpot.objects.create(number='A1')

    def test_root_redirects_to_spot_list(self):
        response = self.client.get('/')

        self.assertRedirects(response, reverse('spots:list'), fetch_redirect_response=False)

    def test_spot_list_is_available_at_spots_url(self):
        response = self.client.get(reverse('spots:list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spots/parkingspot_list.html')

    def test_spot_detail_is_available_at_spots_url(self):
        response = self.client.get(reverse('spots:detail', kwargs={'pk': self.spot.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'spots/parkingspot_detail.html')
