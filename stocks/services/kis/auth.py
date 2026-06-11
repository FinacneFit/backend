# stocks/services/kis/auth.py

import requests
from django.conf import settings
from django.core.cache import cache


class KisAuthError(Exception):
    pass


def get_access_token():
    cached_token = cache.get("kis_access_token")

    if cached_token:
        return cached_token

    if not settings.KIS_APP_KEY:
        raise KisAuthError("KIS_APP_KEY가 설정되지 않았습니다. settings.py와 .env를 확인하세요.")

    if not settings.KIS_APP_SECRET:
        raise KisAuthError("KIS_APP_SECRET이 설정되지 않았습니다. settings.py와 .env를 확인하세요.")

    url = f"{settings.KIS_BASE_URL}/oauth2/tokenP"

    body = {
        "grant_type": "client_credentials",
        "appkey": settings.KIS_APP_KEY,
        "appsecret": settings.KIS_APP_SECRET,
    }

    res = requests.post(
        url,
        headers={"content-type": "application/json; charset=utf-8"},
        json=body,
    )

    if not res.ok:
        raise KisAuthError(
            f"\n[KIS TOKEN ERROR]\n"
            f"status_code: {res.status_code}\n"
            f"url: {url}\n"
            f"response_text: {res.text}\n"
        )

    data = res.json()

    access_token = data.get("access_token")

    if not access_token:
        raise KisAuthError(
            f"\n[KIS TOKEN RESPONSE ERROR]\n"
            f"response: {data}\n"
        )

    cache.set("kis_access_token", access_token, timeout=60 * 60 * 23)

    return access_token