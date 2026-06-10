from django.contrib import admin
from .models import (
    Stock,
    StockPriceDaily,
    StockQuote,
    FinancialStatement,
    StockMetric,
)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "stock_code",
        "stock_name",
        "market",
        "sector",
        "industry",
        "market_cap",
        "is_active",
        "is_recommendable",
        "last_synced_bas_date",
    )
    list_filter = ("market", "sector", "is_active", "is_recommendable")
    search_fields = ("stock_code", "stock_name", "corp_name")


@admin.register(StockPriceDaily)
class StockPriceDailyAdmin(admin.ModelAdmin):
    list_display = (
        "stock",
        "trade_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "change_rate",
    )
    list_filter = ("trade_date",)
    search_fields = ("stock__stock_code", "stock__stock_name")


@admin.register(StockQuote)
class StockQuoteAdmin(admin.ModelAdmin):
    list_display = (
        "stock",
        "current_price",
        "change_rate",
        "quote_time",
        "delay_minutes",
        "source",
        "updated_at",
    )
    search_fields = ("stock__stock_code", "stock__stock_name")


@admin.register(FinancialStatement)
class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = (
        "stock",
        "year",
        "revenue",
        "operating_profit",
        "net_income",
        "roe",
        "roa",
        "per",
        "pbr",
    )
    list_filter = ("year",)
    search_fields = ("stock__stock_code", "stock__stock_name")


@admin.register(StockMetric)
class StockMetricAdmin(admin.ModelAdmin):
    list_display = (
        "stock",
        "return_1m",
        "return_3m",
        "return_1y",
        "volatility_1y",
        "financial_score",
        "momentum_score",
        "risk_score",
        "total_score",
        "updated_at",
    )
    search_fields = ("stock__stock_code", "stock__stock_name")