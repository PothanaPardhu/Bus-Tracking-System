from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
import json
import base64
import hmac
import hashlib
import csv
from pathlib import Path

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_Q
except Exception:
    qrcode = None


class Command(BaseCommand):
    help = 'Generate signed QR tokens and PNG files for students and buses'

    def add_arguments(self, parser):
        parser.add_argument('--output-dir', type=str, default='media/qrcodes', help='Output directory for PNGs and manifest')
        parser.add_argument('--include-students', action='store_true', help='Generate QR for students')
        parser.add_argument('--include-buses', action='store_true', help='Generate QR for buses')
        parser.add_argument('--secret', type=str, default=None, help='Optional signing secret (defaults to settings.SECRET_KEY)')

    def handle(self, *args, **options):
        if qrcode is None:
            self.stderr.write('Missing dependency: please `pip install qrcode[pil] pillow`')
            return

        out_dir = Path(options['output_dir'])
        out_dir.mkdir(parents=True, exist_ok=True)

        secret = options['secret'] or getattr(settings, 'SECRET_KEY', None)
        if not secret:
            self.stderr.write('No signing secret available (set --secret or configure SECRET_KEY)')
            return

        include_students = options['include_students']
        include_buses = options['include_buses']
        if not include_students and not include_buses:
            self.stdout.write('Nothing selected. Use --include-students and/or --include-buses')
            return

        # import models lazily
        from adminapp.models import ChildModels
        from conductorapp.models import BusModels

        manifest_path = out_dir / 'qr_manifest.csv'
        with open(manifest_path, 'w', newline='', encoding='utf-8') as mf:
            writer = csv.DictWriter(mf, fieldnames=['model', 'id', 'name', 'token', 'filename'])
            writer.writeheader()

            if include_students:
                qs = ChildModels.objects.all()
                for child in qs:
                    token = make_token('student', child.c_id, secret)
                    filename = f"student_{child.c_id}.png"
                    filepath = out_dir / filename
                    make_qr_image(token, filepath)
                    writer.writerow({'model': 'student', 'id': child.c_id, 'name': getattr(child, 'children_name', ''), 'token': token, 'filename': str(filepath)})

            if include_buses:
                qs = BusModels.objects.all()
                for bus in qs:
                    token = make_token('bus', bus.bus_number, secret)
                    # sanitize bus number for filename
                    safe_bus = ''.join(c if c.isalnum() else '_' for c in bus.bus_number)
                    filename = f"bus_{safe_bus}.png"
                    filepath = out_dir / filename
                    make_qr_image(token, filepath)
                    writer.writerow({'model': 'bus', 'id': bus.bus_id, 'name': getattr(bus, 'bus_number', ''), 'token': token, 'filename': str(filepath)})

        self.stdout.write(self.style.SUCCESS(f'QR generation complete. Manifest: {manifest_path}'))


def make_token(obj_type: str, obj_id: str, secret: str) -> str:
    payload = {"t": obj_type, "id": str(obj_id), "ts": int(time.time())}
    payload_json = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
    sig = hmac.new(secret.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def make_qr_image(data: str, out_path: Path):
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_Q, box_size=8, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(out_path)
