from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from surveys.models import InvestmentProfile
from .models import Article, Comment
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    CommentSerializer,
)


class ArticleListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        articles = Article.objects.select_related('user').prefetch_related(
            'like_users',
            'comments',
            'holdings',
        ).annotate(
            total_likes=Count('like_users', distinct=True),
            total_comments=Count('comments', distinct=True),
        )

        profile_filter = request.query_params.get('profile')
        post_type = request.query_params.get('post_type')
        keyword = request.query_params.get('keyword')

        if post_type:
            articles = articles.filter(post_type=post_type)

        if keyword:
            articles = articles.filter(title__icontains=keyword) | articles.filter(content__icontains=keyword)

        if profile_filter:
            articles = self.filter_by_profile(request, articles, profile_filter)

        serializer = ArticleListSerializer(
            articles,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleDetailSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                {
                    'message': '게시글이 작성되었습니다.',
                    'article': serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                'message': '게시글 작성에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def filter_by_profile(self, request, articles, profile_filter):
        if profile_filter == 'same':
            if not request.user.is_authenticated:
                return articles.none()

            try:
                my_profile_type = request.user.investment_profile.profile_type
            except InvestmentProfile.DoesNotExist:
                return articles.none()

            return articles.filter(user__investment_profile__profile_type=my_profile_type)

        if profile_filter == 'different':
            if not request.user.is_authenticated:
                return articles.none()

            try:
                my_profile_type = request.user.investment_profile.profile_type
            except InvestmentProfile.DoesNotExist:
                return articles.none()

            return articles.exclude(user__investment_profile__profile_type=my_profile_type)

        return articles.filter(user__investment_profile__profile_type=profile_filter)


class ArticleDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_pk):
        return get_object_or_404(
            Article.objects.select_related('user').prefetch_related(
                'holdings',
                'comments',
                'like_users',
            ),
            pk=article_pk
        )

    def get(self, request, article_pk):
        article = self.get_object(article_pk)
        article.view_count += 1
        article.save(update_fields=['view_count'])

        serializer = ArticleDetailSerializer(
            article,
            context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, article_pk):
        article = self.get_object(article_pk)

        if article.user != request.user:
            return Response(
                {'message': '본인이 작성한 게시글만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ArticleDetailSerializer(
            article,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    'message': '게시글이 수정되었습니다.',
                    'article': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'message': '게시글 수정에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, article_pk):
        article = self.get_object(article_pk)

        if article.user != request.user:
            return Response(
                {'message': '본인이 작성한 게시글만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ArticleDetailSerializer(
            article,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    'message': '게시글이 수정되었습니다.',
                    'article': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'message': '게시글 수정에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, article_pk):
        article = self.get_object(article_pk)

        if article.user != request.user:
            return Response(
                {'message': '본인이 작성한 게시글만 삭제할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        article.delete()

        return Response(
            {'message': '게시글이 삭제되었습니다.'},
            status=status.HTTP_204_NO_CONTENT
        )


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                article=article,
                user=request.user
            )

            return Response(
                {
                    'message': '댓글이 작성되었습니다.',
                    'comment': serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                'message': '댓글 작성에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, comment_pk):
        return get_object_or_404(Comment, pk=comment_pk)

    def put(self, request, comment_pk):
        comment = self.get_object(comment_pk)

        if comment.user != request.user:
            return Response(
                {'message': '본인이 작성한 댓글만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(comment, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    'message': '댓글이 수정되었습니다.',
                    'comment': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'message': '댓글 수정에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, comment_pk):
        comment = self.get_object(comment_pk)

        if comment.user != request.user:
            return Response(
                {'message': '본인이 작성한 댓글만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    'message': '댓글이 수정되었습니다.',
                    'comment': serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'message': '댓글 수정에 실패했습니다.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, comment_pk):
        comment = self.get_object(comment_pk)

        if comment.user != request.user:
            return Response(
                {'message': '본인이 작성한 댓글만 삭제할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()

        return Response(
            {'message': '댓글이 삭제되었습니다.'},
            status=status.HTTP_204_NO_CONTENT
        )


class ArticleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_pk):
        article = get_object_or_404(Article, pk=article_pk)

        if article.like_users.filter(pk=request.user.pk).exists():
            article.like_users.remove(request.user)
            is_liked = False
            message = '좋아요가 취소되었습니다.'
        else:
            article.like_users.add(request.user)
            is_liked = True
            message = '좋아요를 눌렀습니다.'

        return Response(
            {
                'message': message,
                'is_liked': is_liked,
                'like_count': article.like_users.count(),
            },
            status=status.HTTP_200_OK
        )