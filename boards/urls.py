from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'board', PostViewSet)

post_list_view = PostViewSet.as_view({'get': 'list', 'post': 'create'})
post_category_view = PostViewSet.as_view({'get': 'list_by_category'})
post_detail_view = PostViewSet.as_view({'get': 'retrieve_by_category', 'put': 'retrieve_by_category', 
                                        'patch': 'retrieve_by_category', 'delete': 'retrieve_by_category'})

urlpatterns = [
    path('', include(router.urls)),
    path('board', post_list_view, name="post_list"),
    path('board/<str:category>', post_category_view, name='post-category-list'), # 카테고리별 게시판의 게시글 조회
    path('board/<str:category>/<int:post_id>', post_detail_view, name="post-detail"), # 게시글 조회, 수정, 삭제
    path('board/<str:category>/<int:post_id>/like', LikeView.as_view(), name='like'),
    path('board/<str:category>/<int:post_id>/scrap', ScrapView.as_view(), name='scrap'),
    path('mypage', MypageView.as_view(), name='mypage'),
]