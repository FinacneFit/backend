import time

from stocks.models import Stock, FinancialStatement
from stocks.services.kis.client import kis_get
from stocks.services.kis.quote import fetch_current_quote


def to_int(value):
    if value in (None, ""):
        return None

    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return None


def to_float(value):
    if value in (None, ""):
        return None

    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return None


def get_latest_row(rows):
    """
    rows가 list면 stac_yymm 기준 최신 row 선택.
    rows가 dict면 그대로 반환.
    rows가 비어 있으면 빈 dict 반환.
    """
    if not rows:
        return {}

    if isinstance(rows, dict):
        return rows

    if isinstance(rows, list):
        return max(rows, key=lambda row: row.get("stac_yymm", ""))

    return {}


def fetch_balance_sheet(stock_code):
    path = "/uapi/domestic-stock/v1/finance/balance-sheet"
    tr_id = "FHKST66430100"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_DIV_CLS_CODE": "0",
    }

    data = kis_get(path=path, tr_id=tr_id, params=params)
    return data.get("output", [])


def fetch_income_statement(stock_code):
    path = "/uapi/domestic-stock/v1/finance/income-statement"
    tr_id = "FHKST66430200"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_DIV_CLS_CODE": "0",
    }

    data = kis_get(path=path, tr_id=tr_id, params=params)
    return data.get("output", [])


def fetch_financial_ratio(stock_code):
    path = "/uapi/domestic-stock/v1/finance/financial-ratio"
    tr_id = "FHKST66430300"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": stock_code,
        "FID_DIV_CLS_CODE": "0",
    }

    data = kis_get(path=path, tr_id=tr_id, params=params)
    return data.get("output", [])


def sync_financial_statement(stock_code):
    stock = Stock.objects.get(stock_code=stock_code)

    balance_rows = fetch_balance_sheet(stock_code)
    time.sleep(1.2)

    income_rows = fetch_income_statement(stock_code)
    time.sleep(1.2)

    ratio_rows = fetch_financial_ratio(stock_code)
    time.sleep(1.2)

    quote_output = fetch_current_quote(stock_code)

    balance = get_latest_row(balance_rows)
    income = get_latest_row(income_rows)
    ratio = get_latest_row(ratio_rows)

    stac_yymm = (
        balance.get("stac_yymm")
        or income.get("stac_yymm")
        or ratio.get("stac_yymm")
    )

    if not stac_yymm:
        raise ValueError(f"{stock_code} 재무정보의 결산년월 stac_yymm이 없습니다.")

    year = int(stac_yymm[:4])

    financial, created = FinancialStatement.objects.update_or_create(
        stock=stock,
        year=year,
        defaults={
            "revenue": to_int(income.get("sale_account")),
            "operating_profit": to_int(income.get("bsop_prti")),
            "net_income": to_int(income.get("thtr_ntin")),

            "total_assets": to_int(balance.get("total_aset")),
            "total_liabilities": to_int(balance.get("total_lblt")),
            "total_equity": to_int(balance.get("total_cptl")),

            "debt_ratio": to_float(ratio.get("lblt_rate")),
            "roe": to_float(ratio.get("roe_val")),
            "roa": None,

            "eps": to_float(ratio.get("eps") or quote_output.get("eps")),
            "bps": to_float(ratio.get("bps") or quote_output.get("bps")),
            "per": to_float(quote_output.get("per")),
            "pbr": to_float(quote_output.get("pbr")),
        },
    )

    return financial