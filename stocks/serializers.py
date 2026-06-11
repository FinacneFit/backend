from rest_framework import serializers
from .models import Stock


class StockSearchSerializer(serializers.ModelSerializer):
    stock_id = serializers.IntegerField(source="id", read_only=True)

    current_price = serializers.IntegerField(
        source="quote.current_price",
        read_only=True,
        allow_null=True,
    )
    change_rate = serializers.FloatField(
        source="quote.change_rate",
        read_only=True,
        allow_null=True,
    )
    quote_time = serializers.DateTimeField(
        source="quote.quote_time",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Stock
        fields = (
            "stock_id",
            "stock_code",
            "stock_name",
            "market",
            "sector",
            "current_price",
            "change_rate",
            "quote_time",
        )