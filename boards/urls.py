from django.urls import path, include
from .models import Post
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import *

router = routers.DefaultRouter()
router.register(r'board', PostViewSet, basename="board")

urlpatterns = [
    path('board/', PostViewSet.as_view({'get': 'list', 'post': 'create'}), name="post_list"),
    path('board/<str:category>/', PostViewSet.as_view({'get': 'list_by_category'}), name='post-category-list'), # 카테고리별 게시판의 게시글 조회
    path('board/<str:category>/<int:category_id>/', PostViewSet.as_view({'get': 'retrieve_by_category', 'put': 'retrieve_by_category'}), name="post-detail"), # 게시글 조회, 수정, 삭제
    path('mypage/', MypageView.as_view(), name='mypage'),
    path('mypage/posts/', MyPostsView.as_view(), name='my-post'),
    path('mypage/scraps/', MyScrapsView.as_view(), name='my-scrap'),
]