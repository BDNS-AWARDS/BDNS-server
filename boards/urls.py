from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'board', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mypage', MypageView.as_view(), name='mypage'),
]