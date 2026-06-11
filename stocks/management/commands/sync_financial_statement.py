# stocks/management/commands/sync_financial_statement.py

from django.core.management.base import BaseCommand
from stocks.services.kis.financial import sync_financial_statement


class Command(BaseCommand):
    help = "한국투자증권 API로 특정 종목의 재무제표 정보를 동기화합니다."

    def add_arguments(self, parser):
        parser.add_argument("stock_code", type=str)

    def handle(self, *args, **options):
        stock_code = options["stock_code"]

        try:
            financial = sync_financial_statement(stock_code)

            self.stdout.write(
                self.style.SUCCESS(
                    f"{financial.stock.stock_name} {financial.year}년 재무정보 저장 완료"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"{stock_code} 재무정보 저장 실패\n{e}"
                )
            )
            raise e