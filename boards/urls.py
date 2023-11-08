from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'board', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('board', PostViewSet.as_view({'get': 'list'}), name="post"),
    # path('board/like', LikeView.as_view(), name='like'),
    # path('board/scrap', ScrapView.as_view(), name='scrap'),
    path('mypage', MypageView.as_view(), name='mypage'),
]