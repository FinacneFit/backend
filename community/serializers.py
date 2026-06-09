from rest_framework import serializers

from surveys.models import InvestmentProfile
from .models import Article, ArticleHolding, Comment


class ArticleHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleHolding
        fields = (
            'id',
            'stock_name',
            'stock_code',
            'amount',
            'average_price',
            'current_price',
            'profit_rate',
            'memo',
        )


class CommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'article',
            'user_id',
            'user_email',
            'user_nickname',
            'content',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'article',
            'user_id',
            'user_email',
            'user_nickname',
            'created_at',
            'updated_at',
        )


class ArticleListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    author_profile_type = serializers.SerializerMethodField()
    author_profile_name = serializers.SerializerMethodField()

    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    holding_count = serializers.IntegerField(source='holdings.count', read_only=True)

    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id',
            'user_id',
            'user_email',
            'user_nickname',
            'author_profile_type',
            'author_profile_name',
            'title',
            'content',
            'post_type',
            'like_count',
            'comment_count',
            'holding_count',
            'is_liked',
            'view_count',
            'created_at',
            'updated_at',
        )

    def get_author_profile_type(self, article):
        try:
            return article.user.investment_profile.profile_type
        except InvestmentProfile.DoesNotExist:
            return None

    def get_author_profile_name(self, article):
        try:
            return article.user.investment_profile.get_profile_type_display()
        except InvestmentProfile.DoesNotExist:
            return None

    def get_is_liked(self, article):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return article.like_users.filter(pk=request.user.pk).exists()


class ArticleDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)

    author_profile_type = serializers.SerializerMethodField()
    author_profile_name = serializers.SerializerMethodField()
    author_risk_score = serializers.SerializerMethodField()

    holdings = ArticleHoldingSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)

    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id',
            'user_id',
            'user_email',
            'user_nickname',
            'author_profile_type',
            'author_profile_name',
            'author_risk_score',
            'title',
            'content',
            'post_type',
            'holdings',
            'comments',
            'like_count',
            'comment_count',
            'is_liked',
            'view_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'user_id',
            'user_email',
            'user_nickname',
            'author_profile_type',
            'author_profile_name',
            'author_risk_score',
            'comments',
            'like_count',
            'comment_count',
            'is_liked',
            'view_count',
            'created_at',
            'updated_at',
        )

    def get_author_profile_type(self, article):
        try:
            return article.user.investment_profile.profile_type
        except InvestmentProfile.DoesNotExist:
            return None

    def get_author_profile_name(self, article):
        try:
            return article.user.investment_profile.get_profile_type_display()
        except InvestmentProfile.DoesNotExist:
            return None

    def get_author_risk_score(self, article):
        try:
            return article.user.investment_profile.risk_score
        except InvestmentProfile.DoesNotExist:
            return None

    def get_is_liked(self, article):
        request = self.context.get('request')

        if request is None or not request.user.is_authenticated:
            return False

        return article.like_users.filter(pk=request.user.pk).exists()

    def create(self, validated_data):
        holdings_data = validated_data.pop('holdings', [])
        article = Article.objects.create(**validated_data)

        for holding_data in holdings_data:
            ArticleHolding.objects.create(
                article=article,
                **holding_data
            )

        return article

    def update(self, article, validated_data):
        holdings_data = validated_data.pop('holdings', None)

        article.title = validated_data.get('title', article.title)
        article.content = validated_data.get('content', article.content)
        article.post_type = validated_data.get('post_type', article.post_type)
        article.save()

        if holdings_data is not None:
            article.holdings.all().delete()

            for holding_data in holdings_data:
                ArticleHolding.objects.create(
                    article=article,
                    **holding_data
                )

        return article