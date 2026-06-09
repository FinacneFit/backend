from django.contrib import admin

from .models import Article, ArticleHolding, Comment


class ArticleHoldingInline(admin.TabularInline):
    model = ArticleHolding
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'user',
        'post_type',
        'view_count',
        'created_at',
        'updated_at',
    )
    list_filter = ('post_type', 'created_at')
    search_fields = ('title', 'content', 'user__email', 'user__nickname')
    inlines = [ArticleHoldingInline]


@admin.register(ArticleHolding)
class ArticleHoldingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'article',
        'stock_name',
        'stock_code',
        'amount',
        'average_price',
        'current_price',
        'profit_rate',
    )
    search_fields = ('stock_name', 'stock_code')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'article',
        'user',
        'content',
        'created_at',
        'updated_at',
    )
    search_fields = ('content', 'user__email', 'user__nickname')