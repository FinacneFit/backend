import json
import os
from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from stocks.models import Stock


class Command(BaseCommand):
    help = "KRX 상장종목정보 API를 호출하여 Stock 테이블을 수동 갱신합니다."

    BASE_URL = "https://apis.data.go.kr/1160100/service/GetKrxListedInfoService/getItemInfo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--bas-dt",
            type=str,
            help="조회 기준일자 YYYYMMDD. 예: 20260610",
        )
        parser.add_argument(
            "--days-back",
            type=int,
            default=10,
            help="basDt를 지정하지 않았을 때 최근 며칠 전까지 조회할지 설정합니다. 기본값 10일",
        )
        parser.add_argument(
            "--num-of-rows",
            type=int,
            default=1000,
            help="한 페이지 결과 수. 기본값 1000",
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="이번 응답에 없는 기존 종목을 is_active=False 처리합니다.",
        )

    def handle(self, *args, **options):
        service_key = os.environ.get("KRX_SERVICE_KEY")

        if not service_key:
            raise CommandError(
                "KRX_SERVICE_KEY 환경변수가 없습니다. "
                "예: export KRX_SERVICE_KEY='공공데이터포털_인증키'"
            )

        bas_dt = options.get("bas_dt")
        days_back = options["days_back"]
        num_of_rows = options["num_of_rows"]
        deactivate_missing = options["deactivate_missing"]

        target_dates = self.get_target_dates(bas_dt, days_back)

        selected_bas_dt = None
        items = []

        for target_date in target_dates:
            self.stdout.write(f"[조회 시도] basDt={target_date}")

            fetched_items = self.fetch_all_items(
                service_key=service_key,
                bas_dt=target_date,
                num_of_rows=num_of_rows,
            )

            if fetched_items:
                selected_bas_dt = target_date
                items = fetched_items
                break

            self.stdout.write(f"  데이터 없음: {target_date}")

        if not items:
            raise CommandError(f"최근 {days_back}일 이내 조회 가능한 종목 데이터가 없습니다.")

        result = self.save_items(
            items=items,
            bas_dt=selected_bas_dt,
            deactivate_missing=deactivate_missing,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"[완료] basDt={selected_bas_dt}, "
                f"created={result['created']}, "
                f"updated={result['updated']}, "
                f"deactivated={result['deactivated']}"
            )
        )

    def get_target_dates(self, bas_dt, days_back):
        if bas_dt:
            return [bas_dt]

        today = datetime.today().date()

        return [
            (today - timedelta(days=i)).strftime("%Y%m%d")
            for i in range(days_back + 1)
        ]

    def fetch_all_items(self, service_key, bas_dt, num_of_rows):
        page_no = 1
        all_items = []

        while True:
            data = self.request_page(
                service_key=service_key,
                bas_dt=bas_dt,
                page_no=page_no,
                num_of_rows=num_of_rows,
            )

            response = data.get("response", {})
            header = response.get("header", {})
            body = response.get("body", {})

            result_code = header.get("resultCode")
            result_msg = header.get("resultMsg")

            if result_code != "00":
                raise CommandError(
                    f"KRX API 오류: resultCode={result_code}, resultMsg={result_msg}"
                )

            total_count = int(body.get("totalCount", 0))

            if total_count == 0:
                return []

            items_container = body.get("items", {})

            if not isinstance(items_container, dict):
                return []

            items = items_container.get("item", [])

            if isinstance(items, dict):
                items = [items]

            if not items:
                return []

            all_items.extend(items)

            self.stdout.write(
                f"  page={page_no}, 누적={len(all_items)} / total={total_count}"
            )

            if len(all_items) >= total_count:
                break

            page_no += 1

        return all_items

    def request_page(self, service_key, bas_dt, page_no, num_of_rows):
        params = {
            "serviceKey": service_key,
            "resultType": "json",
            "numOfRows": num_of_rows,
            "pageNo": page_no,
            "basDt": bas_dt,
        }

        query_string = urlencode(params, safe="%")
        url = f"{self.BASE_URL}?{query_string}"

        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
        )

        try:
            with urlopen(request, timeout=15) as response:
                raw_body = response.read().decode("utf-8")
        except Exception as error:
            raise CommandError(f"KRX API 요청 실패: {error}")

        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            raise CommandError(
                "KRX API 응답을 JSON으로 파싱하지 못했습니다. "
                "serviceKey, resultType, 인증키 인코딩 여부를 확인하세요."
            )

    @transaction.atomic
    def save_items(self, items, bas_dt, deactivate_missing):
        created_count = 0
        updated_count = 0
        current_stock_codes = set()

        bas_date = datetime.strptime(bas_dt, "%Y%m%d").date()

        for item in items:
            raw_stock_code = item.get("srtnCd", "")
            stock_code = self.normalize_stock_code(raw_stock_code)

            if not stock_code:
                continue

            current_stock_codes.add(stock_code)

            defaults = {
                "stock_name": item.get("itmsNm", "") or "",
                "isin_code": item.get("isinCd", "") or "",
                "market": item.get("mrktCtg", "") or "",
                "corp_registration_no": item.get("crno", "") or "",
                "corp_name": item.get("corpNm", "") or "",
                "last_synced_bas_date": bas_date,
                "is_active": True,
            }

            _, created = Stock.objects.update_or_create(
                stock_code=stock_code,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        deactivated_count = 0

        if deactivate_missing:
            deactivated_count = (
                Stock.objects
                .filter(is_active=True)
                .exclude(stock_code__in=current_stock_codes)
                .update(is_active=False)
            )

        return {
            "created": created_count,
            "updated": updated_count,
            "deactivated": deactivated_count,
        }

    def normalize_stock_code(self, raw_code):
        """
        KRX API의 srtnCd는 A000020 형태로 내려올 수 있음.
        우리 DB에는 000020 형태로 저장.
        """
        code = str(raw_code).strip()

        if code.startswith("A"):
            code = code[1:]

        return code