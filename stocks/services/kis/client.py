# stocks/services/kis/client.py

import requests
from django.conf import settings
from .auth import get_access_token


class KisApiError(Exception):
    pass


def kis_get(path, tr_id, params):
    access_token = get_access_token()

    url = f"{settings.KIS_BASE_URL}{path}"

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": settings.KIS_APP_KEY,
        "appsecret": settings.KIS_APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P",  # 개인 고객이면 P
    }

    res = requests.get(url, headers=headers, params=params)

    # 한국투자 서버가 400/401/500을 줄 때 body를 확인하기 위해 추가
    if not res.ok:
        raise KisApiError(
            f"\n[KIS HTTP ERROR]\n"
            f"status_code: {res.status_code}\n"
            f"url: {res.url}\n"
            f"response_text: {res.text}\n"
        )

    data = res.json()

    if data.get("rt_cd") != "0":
        raise KisApiError(
            f"\n[KIS API ERROR]\n"
            f"rt_cd: {data.get('rt_cd')}\n"
            f"msg_cd: {data.get('msg_cd')}\n"
            f"msg1: {data.get('msg1')}\n"
            f"full_response: {data}\n"
        )

    return data