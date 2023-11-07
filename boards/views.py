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
from rest_framework.views import APIView

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
        
# 좋아요 누르기
class LikeCreateView(APIView):
    def post(self, request, category, category_id, format=None):
        post = get_object_or_404(Post, category=category, category_id=category_id) # 게시글 가져오기
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:  # 좋아요를 처음 추가한 경우
            post.like_count += 1  # 좋아요 수 증가
            post.save()

        return Response({'message': '좋아요를 눌렀습니다.'}, status=status.HTTP_201_CREATED)
    
# 좋아요 삭제하기
class LikeDeleteView(APIView):
    def delete(self, request, category, category_id, format=None):
        post = get_object_or_404(Post, category=category, category_id=category_id) # 게시글 가져오기
        try:
            like = Like.objects.get(user=request.user, post=post)
        except Like.DoesNotExist:
            return Response({'message': '이미 좋아요를 삭제했습니다.'}, status=status.HTTP_200_OK)

        like.delete()  # 좋아요 삭제
        post.like_count -= 1  # 좋아요 수 감소
        post.save()

        return Response({'message': '좋아요가 삭제되었습니다.'}, status=status.HTTP_200_OK)

# 내가 작성한 글, 스크랩한 글 조회
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

# 내가 작성한 글 목록 조회
class MyPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(writer=self.request.user)

# 스크랩한 글 목록 조회
class MyScrapsView(generics.ListAPIView):
    serializer_class = ScrapSerializer

    def get_queryset(self):
        return Scrap.objects.filter(user=self.request.user)
    
# 스크랩하기
class ScrapCreateView(generics.CreateAPIView):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

# 스크랩 취소하기
class ScrapDeleteView(generics.DestroyAPIView):
    queryset = Scrap.objects.all()
    serializer_class = ScrapSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)