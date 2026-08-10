from __future__ import annotations

import json
import os
from typing import Any

_subscriptions: dict[str, dict[str, Any]] = {}


def public_key() -> str:
    return os.getenv("TA_VAPID_PUBLIC_KEY", "")


def subscribe(value: dict[str, Any]) -> None:
    endpoint = value.get("endpoint")
    if not endpoint:
        raise ValueError("push subscription has no endpoint")
    _subscriptions[endpoint] = value


def send_all(payload: dict[str, Any]) -> int:
    private_key = os.getenv("TA_VAPID_PRIVATE_KEY")
    subject = os.getenv("TA_VAPID_SUBJECT", "mailto:total-awareness@localhost")
    if not private_key or not public_key():
        raise RuntimeError("TA_VAPID_PUBLIC_KEY and TA_VAPID_PRIVATE_KEY must be configured")

    from pywebpush import WebPushException, webpush

    sent = 0
    expired = []
    for endpoint, subscription in list(_subscriptions.items()):
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=private_key,
                vapid_claims={"sub": subject},
            )
            sent += 1
        except WebPushException as exc:
            if exc.response is not None and exc.response.status_code in (404, 410):
                expired.append(endpoint)
            else:
                raise
    for endpoint in expired:
        _subscriptions.pop(endpoint, None)
    return sent
