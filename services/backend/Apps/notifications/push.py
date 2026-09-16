"""Firebase Cloud Messaging delivery for inbox notifications.

Uses the FCM HTTP v1 API directly (google-auth only) instead of the
firebase-admin SDK, which would pull gRPC into every image build.
Set FIREBASE_CREDENTIALS to the service account JSON (raw or base64);
without it, notifications stay inbox-only.
"""

import base64
import json
import logging

from django.conf import settings

from Apps.accounts.models import DeviceToken, User
from Apps.notifications.models import UserNotification

log = logging.getLogger(__name__)
SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
# Inbox category -> the customer's Preference Center toggle.
PREFERENCE = {
    UserNotification.Category.OFFERS: "notify_collections",
    UserNotification.Category.REWARDS: "notify_rewards",
    UserNotification.Category.ORDERS: "notify_orders",
}
_session = None
_project_id = None


def _session_for_project():
    """(AuthorizedSession, project_id), or (None, None) when FCM isn't configured."""
    global _session, _project_id
    if not settings.FIREBASE_CREDENTIALS:
        return None, None
    if _session is None:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account

        raw = settings.FIREBASE_CREDENTIALS.strip()
        # The service account JSON, either inline or base64 (base64 survives .env parsing).
        info = json.loads(raw if raw.startswith("{") else base64.b64decode(raw))
        _session = AuthorizedSession(service_account.Credentials.from_service_account_info(info, scopes=[SCOPE]))
        _project_id = info["project_id"]
    return _session, _project_id


def send(notifications):
    """Pushes already-saved inbox rows to their owners' devices. Returns the number delivered."""
    session, project_id = _session_for_project()
    if not session or not notifications:
        return 0

    wanted = {n.user_id: n for n in notifications}
    allowed = {
        user.pk for user in User.objects.filter(pk__in=wanted, push_enabled=True).only(
            "pk", "notify_collections", "notify_rewards", "notify_orders")
        if getattr(user, PREFERENCE[wanted[user.pk].category], True)
    }
    tokens = DeviceToken.objects.filter(user_id__in=allowed).values_list("token", "user_id")

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    sent, stale = 0, []
    for token, user_id in tokens:
        note = wanted[user_id]
        payload = {"message": {
            "token": token,
            "notification": {"title": note.title, "body": note.body},
            "data": {"notification_id": str(note.pk), "category": note.category,
                     "order_id": str(note.order_id or "")},
        }}
        try:
            response = session.post(url, json=payload, timeout=10)
        except Exception:  # a push must never break the request that triggered it
            log.exception("FCM request failed")
            continue
        if response.status_code == 200:
            sent += 1
        elif response.status_code in (400, 403, 404):  # unregistered / invalid token
            stale.append(token)
        else:
            log.warning("FCM %s: %s", response.status_code, response.text[:200])
    if stale:
        DeviceToken.objects.filter(token__in=stale).delete()
    return sent
