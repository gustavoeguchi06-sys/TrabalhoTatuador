"""Envio de notificações Web Push com chaves VAPID geradas automaticamente.

As chaves ficam em BASE_DIR/vapid_private_key.pem (criadas no primeiro uso).
"""
import json

from cryptography.hazmat.primitives import serialization
from django.conf import settings
from py_vapid import Vapid, b64urlencode
from pywebpush import webpush, WebPushException

VAPID_KEY_PATH = settings.BASE_DIR / 'vapid_private_key.pem'
VAPID_CLAIMS = {'sub': 'mailto:gustavoeguchi06@gmail.com'}

_vapid = None


def get_vapid():
    global _vapid
    if _vapid is None:
        if not VAPID_KEY_PATH.exists():
            v = Vapid()
            v.generate_keys()
            v.save_key(str(VAPID_KEY_PATH))
        _vapid = Vapid.from_file(str(VAPID_KEY_PATH))
    return _vapid


def get_public_key():
    """Chave pública no formato base64url aceito pelo PushManager.subscribe."""
    v = get_vapid()
    raw = v.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    return b64urlencode(raw)


def send_push_to_all(title, body):
    """Envia a notificação para todas as inscrições; remove as expiradas."""
    from .models import PushSubscription

    get_vapid()  # garante que as chaves existem
    payload = json.dumps({'title': title, 'body': body})
    sent = 0
    for sub in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info=json.loads(sub.subscription_json),
                data=payload,
                vapid_private_key=str(VAPID_KEY_PATH),
                vapid_claims=dict(VAPID_CLAIMS),
            )
            sent += 1
        except WebPushException as exc:
            status = getattr(exc.response, 'status_code', None)
            if status in (404, 410):
                sub.delete()
        except Exception:
            pass
    return sent
