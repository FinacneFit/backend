# stocks/services/kis/quote.py

from decimal import Decimal
from django.utils import timezone
from stocks.models import Stock, StockQuote
from .client import kis_get


def fetch_current_quote(stock_code):
    path = "/uapi/domestic-stock/v1/quotations/inquire-price"
    tr_id = "FHKST01010100"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
    }

    data = kis_get(path=path, tr_id=tr_id, params=params)
    return data["output"]


def sync_stock_quote(stock_code):
    stock = Stock.objects.get(stock_code=stock_code)

    output = fetch_current_quote(stock_code)

    quote, created = StockQuote.objects.update_or_create(
        stock=stock,
        defaults={
            "current_price": int(output["stck_prpr"]),
            "change_rate": Decimal(output["prdy_ctrt"]),
            "quote_time": timezone.now(),
            "delay_minutes": 0,
            "source": "KIS",
        },
    )

    return quote