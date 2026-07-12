from django.test import TestCase
from django.urls import reverse

from spots.models import ParkingSpot
from spots.templatetags.pagination import pagination_window


class PageStub:
    def __init__(self, number):
        self.number = number


class PaginatorStub:
    def __init__(self, num_pages):
        self.num_pages = num_pages


class PaginationWindowTests(TestCase):
    def test_window_has_no_more_than_five_pages(self):
        pages = list(pagination_window(PageStub(10), PaginatorStub(20)))

        self.assertEqual(pages, [8, 9, 10, 11, 12])

    def test_window_sticks_to_start(self):
        pages = list(pagination_window(PageStub(1), PaginatorStub(20)))

        self.assertEqual(pages, [1, 2, 3, 4, 5])

    def test_window_sticks_to_end(self):
        pages = list(pagination_window(PageStub(20), PaginatorStub(20)))

        self.assertEqual(pages, [16, 17, 18, 19, 20])


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
