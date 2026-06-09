from django.conf import settings
from django.db import models


class Article(models.Model):
    POST_TYPE_CHOICES = [
        ('STORY', '투자 이야기'),
        ('PORTFOLIO', '포트폴리오 공유'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_articles'
    )
    title = models.CharField(max_length=100)
    content = models.TextField()

    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='STORY'
    )

    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_community_articles',
        blank=True
    )

    view_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ArticleHolding(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='holdings'
    )

    stock_name = models.CharField(max_length=100)
    stock_code = models.CharField(max_length=30, blank=True)

    amount = models.PositiveIntegerField(
        default=0,
        help_text='보유 수량'
    )

    average_price = models.PositiveIntegerField(
        default=0,
        help_text='평균 매수가'
    )

    current_price = models.PositiveIntegerField(
        default=0,
        help_text='현재가'
    )

    profit_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text='수익률'
    )

    memo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.article.title} - {self.stock_name}'


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_comments'
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.content[:20]