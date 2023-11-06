from django.urls import path, include
from .models import Post
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import *

router = routers.DefaultRouter()
router.register(r'board', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('board', PostListView.as_view()),  # 게시판 목록 조회, 게시글 생성
    path('board/<str:category>', PostListView.as_view()),  # 카테고리별 게시판의 게시글 조회
    path('board/<str:category>/<int:post_id>', PostDetailView.as_view()),  # 게시글 조회, 수정, 삭제
]