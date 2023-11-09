from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'board', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('board/<int:post_id>/like', LikeView.as_view(), name='like'),
    path('board/<int:post_id>/scrap', ScrapView.as_view(), name='scrap'),
    path('mypage', MypageView.as_view(), name='mypage'),
]