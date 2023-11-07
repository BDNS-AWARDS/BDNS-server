from rest_framework import viewsets
from .models import Post, Scrap
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.authentication import AllowAnyAuthentication, CookieAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from itertools import chain
from django.db.models import Value, CharField

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]

    @action(detail=False, methods=['get'])
    def list_by_category(self, request, category):
        queryset = self.queryset.filter(category=category)
        print(category)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'put'])
    def retrieve_by_category(self, request, category, category_id):
        if request.method == 'GET':
            # 게시글 조회
            queryset = self.queryset.filter(category=category, category_id=category_id)
            post = get_object_or_404(queryset)
            serializer = self.get_serializer(post)
            return Response(serializer.data)
        elif request.method == 'PUT':
            # 게시글 수정
            queryset = self.queryset.filter(category=category, category_id=category_id)
            post = get_object_or_404(queryset)
            serializer = self.get_serializer(post, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action == 'create':
            return PostCreateSeraizlier
        elif self.action == 'update' or self.action == 'partial_update':
            return PostUpdateSerailizer
        elif self.action == 'retrieve':
            return PostRetrieveSeraizlier
        else:
            return PostSerializer


class MypageView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        user_posts = Post.objects.filter(writer=user)
        user_scraps = Scrap.objects.filter(user=user)

        return user_posts, user_scraps  # 두 쿼리셋을 튜플로 반환

    def list(self, request, *args, **kwargs):
        user_posts, user_scraps = self.get_queryset()
        post_serializer = PostSerializer(user_posts, many=True)
        scrap_serializer = ScrapSerializer(user_scraps, many=True)

        combined_data = post_serializer.data + scrap_serializer.data  # 직렬화된 데이터 합치기

        return Response(combined_data)

class MyPostsView(generics.ListAPIView):
    # 내가 작성한 글 목록 조회
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(writer=self.request.user)

class MyScrapsView(generics.ListAPIView):
    # 스크랩한 글 목록 조회
    serializer_class = ScrapSerializer

    def get_queryset(self):
        return Scrap.objects.filter(user=self.request.user)
    
class ScrapCreateView(generics.CreateAPIView):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

class ScrapDeleteView(generics.DestroyAPIView):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)