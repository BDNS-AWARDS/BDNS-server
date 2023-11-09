from rest_framework import viewsets
from .models import Post, Scrap
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.authentication import AllowAnyAuthentication, CookieAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    authentication_classes = [AllowAnyAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category"]

    # def get_serializer_class(self):
    #     if self.action == 'update' or self.action == 'partial_update':
    #         return PostUpdateSerializer
    #     # elif self.action == 'retrieve':
    #     #     return PostRetrieveSerializer
    #     else:
    #         return PostSerializer

    
        
    # def list(self, request):
    #     category = request.query_params.get('category', None)
    #     post_id = request.query_params.get('post_id', None)

    #     if category:
    #         queryset = Post.objects.filter(category=category)
    #     else:
    #         queryset = Post.objects.all()

    #     if post_id:
    #         queryset = queryset.filter(id=post_id)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data) 

    # # 게시글 조회
    # def retrieve(self, request, *args, **kwargs):
    #     post_id = kwargs.get('pk')
    #     try:
    #         # 해당 게시글 ID를 사용하여 게시글을 조회합니다.
    #         post = self.queryset.get(id=post_id)
    #         serializer = self.get_serializer(post)
    #         return Response(serializer.data)
    #     except Post.DoesNotExist:
    #         return Response({'detail': '게시글을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    # # 게시글 수정
    # def update(self, request, *args, **kwargs):
    #     post_id = kwargs.get('pk')
    #     post = get_object_or_404(self.queryset, id=post_id)
    #     serializer = self.get_serializer(post, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # 게시글 삭제
    # def destroy(self, request, *args, **kwargs):
    #     post_id = kwargs.get('pk')
    #     post = get_object_or_404(self.queryset, id=post_id)
    #     post.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
        
# 좋아요 기능 (좋아요 누르기 및 삭제하기)
class LikeView(APIView):
    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)  # 게시글 가져오기
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if created:  # 좋아요를 처음 추가한 경우
            post.like_count += 1  # 좋아요 수 증가
            post.save()
            message = '좋아요를 눌렀습니다.'
        else:
            like.delete()  # 좋아요 삭제
            post.like_count -= 1  # 좋아요 수 감소
            post.save()
            message = '좋아요가 삭제되었습니다.'

        return Response({'message': message}, status=status.HTTP_201_CREATED)
    
# 스크랩 기능
class ScrapView(APIView):
    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)
        scrap, created = Scrap.objects.get_or_create(user=request.user, post=post)

        if created:
            return Response({'message': '스크랩을 추가했습니다.'}, status=status.HTTP_201_CREATED)
        else:
            scrap.delete()
            return Response({'message': '스크랩을 삭제했습니다.'}, status=status.HTTP_200_OK)
        
# 내가 쓴 글, 내가 스크랩한 글 목록 보기
class MypageView(APIView):
    def get(self, request):
        user = request.user
        user_posts = Post.objects.filter(writer=user)
        user_scraps = Scrap.objects.filter(user=user)

        post_serializer = PostSerializer(user_posts, many=True, context={'request': request})
        scrap_serializer = ScrapSerializer(user_scraps, many=True, context={'request': request})

        data = {
            "user_posts": post_serializer.data,
            "user_scraps": scrap_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
