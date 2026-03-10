from django.test import TestCase, Client
from adminapp.models import ChildModels
from conductorapp.models import BusModels, PickupDropEvent

class UserViewTests(TestCase):
    def setUp(self):
        # create child and bus, then event
        self.child = ChildModels.objects.create(
            children_name='TestUser',
            children_mothername='M',
            children_fathername='F',
            children_contact='123',
            children_email='user@example.com',
            children_password='pass',
            children_address='addr',
            children_class='1'
        )
        self.bus = BusModels.objects.create(bus_number='BUS100', bus_route='R', bus_class='1')
        PickupDropEvent.objects.create(child=self.child, bus=self.bus, event_type='pickup', location_latitude=0, location_longitude=0)
        self.client = Client()
        session = self.client.session
        session['c_id'] = self.child.c_id
        session.save()

    def test_view_status_shows_busid(self):
        resp = self.client.get('/user-view-status/')
        self.assertEqual(resp.status_code, 200)
        # page should include busId variable with the correct id
        self.assertIn(f'busId = {self.bus.bus_id}', resp.content.decode())
