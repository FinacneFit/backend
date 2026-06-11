import time

from django.core.management.base import BaseCommand
from stocks.models import Stock
from stocks.services.kis.quote import sync_stock_quote


class Command(BaseCommand):
    help = "Stock 테이블에 저장된 전체 종목의 현재가를 한국투자증권 API로 동기화합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="테스트용으로 동기화할 종목 수를 제한합니다.",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=0.5,
            help="API 호출 사이 대기 시간입니다. 기본값은 0.5초입니다.",
        )
        parser.add_argument(
            "--start",
            type=int,
            default=0,
            help="몇 번째 종목부터 시작할지 지정합니다.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        sleep_seconds = options["sleep"]
        start = options["start"]

        stocks = Stock.objects.filter(is_active=True).order_by("stock_code")

        total_count = stocks.count()

        if start:
            stocks = stocks[start:]

        if limit:
            stocks = stocks[:limit]

        success_count = 0
        fail_count = 0

        self.stdout.write(f"전체 활성 종목 수: {total_count}")
        self.stdout.write(f"이번 실행 대상 종목 수: {stocks.count()}")
        self.stdout.write(f"호출 간 대기 시간: {sleep_seconds}초")
        self.stdout.write("-" * 50)

        for index, stock in enumerate(stocks, start=start + 1):
            try:
                quote = sync_stock_quote(stock.stock_code)
                success_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{index}/{total_count}] "
                        f"{stock.stock_name}({stock.stock_code}) "
                        f"현재가 저장 완료: {quote.current_price}"
                    )
                )

            except Exception as e:
                fail_count += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"[{index}/{total_count}] "
                        f"{stock.stock_name}({stock.stock_code}) "
                        f"실패: {e}"
                    )
                )

            time.sleep(sleep_seconds)

        self.stdout.write("-" * 50)
        self.stdout.write(self.style.SUCCESS(f"성공: {success_count}개"))
        self.stdout.write(self.style.ERROR(f"실패: {fail_count}개"))