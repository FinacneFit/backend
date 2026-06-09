from django.urls import path

from .views import (
    ArticleListCreateView,
    ArticleDetailView,
    CommentCreateView,
    CommentDetailView,
    ArticleLikeView,
)

app_name = 'community'

urlpatterns = [
    path('articles/', ArticleListCreateView.as_view(), name='article_list_create'),
    path('articles/<int:article_pk>/', ArticleDetailView.as_view(), name='article_detail'),

    path('articles/<int:article_pk>/comments/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:comment_pk>/', CommentDetailView.as_view(), name='comment_detail'),

    path('articles/<int:article_pk>/like/', ArticleLikeView.as_view(), name='article_like'),
]