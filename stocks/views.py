from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Stock
from .serializers import StockSearchSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def stock_search(request):
    keyword = request.GET.get("keyword", "").strip()
    market = request.GET.get("market", "").strip()
    limit = request.GET.get("limit", 20)

    if not keyword:
        return Response([])

    try:
        limit = int(limit)
    except ValueError:
        limit = 20

    limit = max(1, min(limit, 50))

    stocks = (
        Stock.objects
        .filter(is_active=True)
        .select_related("quote")
    )

    stocks = stocks.filter(
        Q(stock_name__icontains=keyword)
        | Q(stock_code__icontains=keyword)
        | Q(corp_name__icontains=keyword)
    )

    if market:
        stocks = stocks.filter(market__iexact=market)

    stocks = stocks.order_by("stock_code")[:limit]

    serializer = StockSearchSerializer(stocks, many=True)
    return Response(serializer.data)