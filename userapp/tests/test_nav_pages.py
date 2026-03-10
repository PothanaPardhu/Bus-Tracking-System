from django.test import TestCase, Client
from adminapp.models import ChildModels
from conductorapp.models import BusModels, PickupDropEvent

class UserNavTests(TestCase):
    def setUp(self):
        self.client = Client()
        # create child and session
        self.child = ChildModels.objects.create(
            children_name='NavUser',
            children_mothername='M',
            children_fathername='F',
            children_contact='123',
            children_email='nav@example.com',
            children_password='pass',
            children_address='addr',
            children_class='1'
        )
        session = self.client.session
        session['c_id'] = self.child.c_id
        session.save()
        # create a bus & event so tracking page has something
        self.bus = BusModels.objects.create(bus_number='BUSNAV', bus_route='R', bus_class='1')
        PickupDropEvent.objects.create(child=self.child, bus=self.bus, event_type='pickup', location_latitude=0, location_longitude=0)

    def test_all_nav_pages_load(self):
        urls = [
            '/user-index/',
            '/user-about/',
            '/user-feedback/',
            '/user-myprofile/',
            '/user-view-status/',
            '/user-changepassword/',
            '/user-boarding-status/',
            '/user-dropping-status/',
            '/user-notification/',
        ]
        for url in urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"{url} failed")
