import json
import time
import requests

from django.conf import settings
from .auth import get_access_token


class KisApiError(Exception):
    pass


_last_request_time = 0


def _wait_for_rate_limit():
    """
    한국투자 API 초당 호출 제한을 피하기 위해
    모든 요청 사이에 일정 간격을 둔다.
    """
    global _last_request_time

    interval = getattr(settings, "KIS_API_INTERVAL_SECONDS", 0.7)

    now = time.time()
    elapsed = now - _last_request_time

    if elapsed < interval:
        time.sleep(interval - elapsed)

    _last_request_time = time.time()


def _parse_response_json(res):
    try:
        return res.json()
    except json.JSONDecodeError:
        return None


def kis_get(path, tr_id, params, max_retries=3):
    access_token = get_access_token()

    url = f"{settings.KIS_BASE_URL}{path}"

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": settings.KIS_APP_KEY,
        "appsecret": settings.KIS_APP_SECRET,
        "tr_id": tr_id,
        "custtype": "P",
    }

    for attempt in range(1, max_retries + 1):
        _wait_for_rate_limit()

        res = requests.get(url, headers=headers, params=params)
        data = _parse_response_json(res)

        # 초당 거래건수 초과면 잠깐 기다렸다가 재시도
        if data and data.get("msg_cd") == "EGW00201":
            wait_seconds = attempt * 1.5
            time.sleep(wait_seconds)
            continue

        if not res.ok:
            raise KisApiError(
                f"\n[KIS HTTP ERROR]\n"
                f"status_code: {res.status_code}\n"
                f"url: {res.url}\n"
                f"response_text: {res.text}\n"
            )

        if data is None:
            raise KisApiError(
                f"\n[KIS RESPONSE PARSE ERROR]\n"
                f"status_code: {res.status_code}\n"
                f"url: {res.url}\n"
                f"response_text: {res.text}\n"
            )

        if data.get("rt_cd") != "0":
            raise KisApiError(
                f"\n[KIS API ERROR]\n"
                f"rt_cd: {data.get('rt_cd')}\n"
                f"msg_cd: {data.get('msg_cd')}\n"
                f"msg1: {data.get('msg1')}\n"
                f"full_response: {data}\n"
            )

        return data

    raise KisApiError(
        f"\n[KIS API RETRY FAILED]\n"
        f"tr_id: {tr_id}\n"
        f"path: {path}\n"
        f"params: {params}\n"
        f"reason: 초당 거래건수 초과로 {max_retries}회 재시도 후 실패"
    )