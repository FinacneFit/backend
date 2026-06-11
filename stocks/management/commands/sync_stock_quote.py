# stocks/management/commands/sync_stock_quote.py

from django.core.management.base import BaseCommand
from stocks.services.kis.quote import sync_stock_quote


class Command(BaseCommand):
    help = "한국투자증권 API로 특정 종목 현재가를 동기화합니다."

    def add_arguments(self, parser):
        parser.add_argument("stock_code", type=str)

    def handle(self, *args, **options):
        stock_code = options["stock_code"]
        quote = sync_stock_quote(stock_code)

        self.stdout.write(
            self.style.SUCCESS(
                f"{quote.stock.stock_name} 현재가 저장 완료: {quote.current_price}"
            )
        )