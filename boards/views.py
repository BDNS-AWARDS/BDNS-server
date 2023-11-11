from rest_framework import viewsets, mixins
from .models import Post, Scrap
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.authentication import AllowAnyAuthentication, CookieAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieAuthentication]
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
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like_count = post.like_count # 좋아요 개수 가져오기

        return Response({'like_count': like_count}, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, id=post_id)  # 게시글 가져오기
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        like_count = post.like_count

        if created:  # 좋아요를 처음 추가한 경우
            post.like_count += 1  # 좋아요 수 증가
            post.save()
            message = '좋아요를 눌렀습니다.'
        else:
            like.delete()  # 좋아요 삭제
            post.like_count -= 1  # 좋아요 수 감소
            post.save()
            message = '좋아요가 삭제되었습니다.'

        return Response({'message': message, 'like_count': like_count}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_like_status(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # 사용자가 해당 게시물에 좋아요를 눌렀는지 여부 확인
    is_liked = post.likes.filter(user=user).exists()
    return Response({'is_liked': is_liked})
    
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scrap_status(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # 사용자가 해당 게시물을 스크랩했는지 여부 확인
    is_scrapped = post.scraps.filter(user=user).exists()
    return Response({'is_scrapped': is_scrapped})
        
# 내가 쓴 글, 내가 스크랩한 글 목록 보기
class MypageView(APIView):
    def get(self, request):
        user = request.user
        user_posts = Post.objects.filter(writer=user)
        user_scraps = Scrap.objects.filter(user=user)
        
        user_data = UserProfileSerializer(user).data
        post_data = PostSerializer(user_posts, many=True).data
        scrap_data = ScrapSerializer(user_scraps, many=True).data

        # 좋아요 및 스크랩 정보 추가
        for post in post_data:
            post['is_liked'] = Like.objects.filter(user=user, post=post['id']).exists()
            post['is_scrapped'] = Scrap.objects.filter(user=user, post=post['id']).exists()

        data = {
            "user_info": user_data, 
            "user_posts": post_data,
            "user_scraps": scrap_data,
        }

        return Response(data, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ViewSet):
    CATEGORY_CHOICES = [
        ('select','#카테고리를_선택해주세요!'),
        ('best_all', '#all'),
        ('best_movies', '#올해의_영화'),
        ('best_dramas', '#올해의_드라마'),
        ('best_books', '#올해의_책'),
        ('best_music', '#올해의_음악'),
        ('best_moments', '#올해의_순간'),
        ('best_hobbies', '#올해의_취미'),
        ('best_discoveries', '#올해의_발견'),
        ('best_habits', '#올해의_습관'),
        ('best_sadness', '#올해의_우울'),
        ('best_thoughts', '#올해의_생각'),
        ('best_failures', '#올해의_실패'),
        ('best_regrets', '#올해의_후회'),
        ('best_humor', '#올해의_유머'),
        ('best_tears', '#올해의_눈물'),
        ('best_spending', '#올해의_소비'),
        ('best_emotions', '#올해의_감동'),
        ('best_travels', '#올해의_여행'),
        ('best_food', '#올해의_음식'),
        ('best_gifts', '#올해의_선물'),
        ('best_photos', '#올해의_사진'),
        ('next_year_me', '#내년의_나')
    ]

    def list(self, request):
        category_data = [{'id': idx , 'value': value, 'tagname': label} for idx, (value, label) in enumerate(self.CATEGORY_CHOICES)]
        serializer = CategorySerializer(data={'categories': category_data})
        serializer.is_valid()
        return Response(serializer.data)