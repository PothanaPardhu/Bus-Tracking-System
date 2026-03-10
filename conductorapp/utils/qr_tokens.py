import base64
import json
import hmac
import hashlib
import time
from typing import Optional, Tuple, Dict
from django.conf import settings


class TokenValidationError(Exception):
    pass


def _add_padding(b64: str) -> str:
    return b64 + '=' * (-len(b64) % 4)


def decode_token(token: str) -> Tuple[Dict, str]:
    """Decode a token into (payload_dict, signature_hex).

    Token format produced by the generator: <base64url(payload)>.<hex_signature>
    """
    try:
        payload_b64, sig = token.rsplit('.', 1)
    except ValueError:
        raise TokenValidationError('token format invalid')

    try:
        payload_json = base64.urlsafe_b64decode(_add_padding(payload_b64).encode('utf-8'))
        payload = json.loads(payload_json.decode('utf-8'))
    except Exception as e:
        raise TokenValidationError(f'payload decode error: {e}')

    return payload, sig


def verify_token(token: str, secret: Optional[str] = None, max_age: Optional[int] = None) -> Dict:
    """Verify HMAC signature and optional max_age (seconds).

    Returns the decoded payload dict on success, raises TokenValidationError on failure.
    """
    secret = secret or getattr(settings, 'SECRET_KEY', None)
    if not secret:
        raise TokenValidationError('no secret available for verification')

    payload, sig = decode_token(token)
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).decode('utf-8').rstrip('=')

    expected_sig = hmac.new(secret.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        raise TokenValidationError('signature mismatch')

    if max_age is not None:
        ts = payload.get('ts')
        if ts is None:
            raise TokenValidationError('token missing timestamp')
        if int(time.time()) - int(ts) > int(max_age):
            raise TokenValidationError('token expired')

    return payload


def example_usage():
    """Example helper that shows how to call verify_token from views.

    Not executed automatically; import and call `verify_token` inside your view logic.
    """
    sample = '...'  # replace with actual token
    try:
        payload = verify_token(sample, max_age=60 * 60 * 24)  # 1 day
        print('valid:', payload)
    except TokenValidationError as e:
        print('invalid token:', e)
