from django.db import models

# 종목 기본 정보
class Stock(models.Model):
    stock_code = models.CharField(max_length=20, unique=True)
    stock_name = models.CharField(max_length=100)

    # KRX API 제공 정보
    isin_code = models.CharField(max_length=20, blank=True)
    corp_name = models.CharField(max_length=150, blank=True)
    corp_registration_no = models.CharField(max_length=30, blank=True)

    market = models.CharField(max_length=20)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)

    market_cap = models.BigIntegerField(null=True, blank=True)

    # 서비스 관리용
    is_active = models.BooleanField(default=True)
    is_recommendable = models.BooleanField(default=True)
    last_synced_bas_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["stock_code"]

    def __str__(self):
        return f"{self.stock_name}({self.stock_code})"

# 일별 주가 데이터
class StockPriceDaily(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="daily_prices",
    )
    trade_date = models.DateField()

    open_price = models.PositiveIntegerField()
    high_price = models.PositiveIntegerField()
    low_price = models.PositiveIntegerField()
    close_price = models.PositiveIntegerField()
    volume = models.BigIntegerField(default=0)

    change_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stock", "trade_date"],
                name="unique_stock_daily_price",
            )
        ]
        ordering = ["-trade_date"]

    def __str__(self):
        return f"{self.stock.stock_name} - {self.trade_date}"

# 최신 현재가 -> 1분 갱신
class StockQuote(models.Model):
    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name="quote",
    )

    current_price = models.PositiveIntegerField()
    change_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    quote_time = models.DateTimeField()
    delay_minutes = models.PositiveSmallIntegerField(default=20)
    source = models.CharField(max_length=50, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.stock_name} 현재가 {self.current_price}"

# 재무제표 데이터 -> 추천 시스템 알고리즘에 필요
class FinancialStatement(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="financials",
    )

    year = models.IntegerField()

    revenue = models.BigIntegerField(null=True, blank=True)
    operating_profit = models.BigIntegerField(null=True, blank=True)
    net_income = models.BigIntegerField(null=True, blank=True)

    total_assets = models.BigIntegerField(null=True, blank=True)
    total_liabilities = models.BigIntegerField(null=True, blank=True)
    total_equity = models.BigIntegerField(null=True, blank=True)

    debt_ratio = models.FloatField(null=True, blank=True)
    roe = models.FloatField(null=True, blank=True)
    roa = models.FloatField(null=True, blank=True)
    eps = models.FloatField(null=True, blank=True)
    bps = models.FloatField(null=True, blank=True)
    per = models.FloatField(null=True, blank=True)
    pbr = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stock", "year"],
                name="unique_stock_financial_year",
            )
        ]
        ordering = ["-year"]

    def __str__(self):
        return f"{self.stock.stock_name} - {self.year} 재무제표"

# 수익률, 변동성, 추천 점수 등 계산 결과 -> 추천 시스템
class StockMetric(models.Model):
    stock = models.OneToOneField(
        Stock,
        on_delete=models.CASCADE,
        related_name="metric",
    )

    return_1m = models.FloatField(null=True, blank=True)
    return_3m = models.FloatField(null=True, blank=True)
    return_1y = models.FloatField(null=True, blank=True)
    return_3y = models.FloatField(null=True, blank=True)

    volatility_1y = models.FloatField(null=True, blank=True)
    max_drawdown_1y = models.FloatField(null=True, blank=True)
    avg_volume_3m = models.BigIntegerField(null=True, blank=True)

    financial_score = models.FloatField(null=True, blank=True)
    momentum_score = models.FloatField(null=True, blank=True)
    risk_score = models.FloatField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.stock_name} 지표"