from django.test import TestCase
from django.conf import settings
from conductorapp.utils.qr_tokens import verify_token, TokenValidationError
from conductorapp.management.commands.generate_qr_codes import make_token
import time


class QRTokenTests(TestCase):
    def test_verify_valid_token(self):
        secret = getattr(settings, 'SECRET_KEY')
        tok = make_token('student', '12345', secret)
        payload = verify_token(tok, secret=secret)
        self.assertEqual(payload['t'], 'student')
        self.assertEqual(payload['id'], '12345')


class BusAPITests(TestCase):
    def setUp(self):
        # create a couple of buses with classes
        from conductorapp.models import BusModels
        BusModels.objects.create(bus_number='BUSX', bus_route='R', bus_class='1')
        BusModels.objects.create(bus_number='BUSY', bus_route='R', bus_class='2')

    def test_bus_class_filter(self):
        client = self.client
        resp = client.get('/api/v1/tracking/buses/?bus_class=1')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data.get('results', data)
        self.assertTrue(any(b['bus_class']=='1' for b in results))
        self.assertFalse(any(b['bus_class']=='2' for b in results))

    def test_verify_invalid_signature(self):
        secret = getattr(settings, 'SECRET_KEY')
        tok = make_token('student', '1', secret)
        # tamper token
        tampered = tok.rsplit('.', 1)[0] + '.deadbeef'
        with self.assertRaises(TokenValidationError):
            verify_token(tampered, secret=secret)

    def test_verify_expired_token(self):
        secret = getattr(settings, 'SECRET_KEY')
        tok = make_token('student', '2', secret)
        # set max_age small so it expires
        time.sleep(1)
        with self.assertRaises(TokenValidationError):
            verify_token(tok, secret=secret, max_age=0)
