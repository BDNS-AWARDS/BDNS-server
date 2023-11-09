from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'board', PostViewSet, basename='board')

Crouter = routers.DefaultRouter(trailing_slash=False)
Crouter.register(r'hashtag', CategoryViewSet, basename='hashtag')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(Crouter.urls)),
    path('board/<int:post_id>/like', LikeView.as_view(), name='like'),
    path('board/<int:post_id>/scrap', ScrapView.as_view(), name='scrap'),
    path('mypage', MypageView.as_view(), name='mypage'),
]