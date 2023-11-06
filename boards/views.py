from rest_framework import generics, viewsets
from .models import Post
from .serializers import PostSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def filter_by_category(self, queryset, category):
        return queryset.filter(category=category) # 카테고리에 해당하는 게시글만 필터링하기

    def list(self, request, *args, **kwargs):
        category = self.kwargs.get('category')
        queryset = self.get_queryset()
        queryset = self.filter_by_category(queryset, category)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # 게시글 조회
    def retrieve(self, request, *args, **kwargs):
        category = kwargs['category'] # 카테고리에 해당하는 게시글 찾기
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, category=category, id=post_id)
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    # 게시글 수정
    def update(self, request, *args, **kwargs):
        category = kwargs['category']
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, category=category, id=post_id) # 카테고리와 게시글 id로 게시글 찾기
        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시글 삭제
    def destroy(self, request, *args, **kwargs):
        category = kwargs['category']
        post_id = kwargs['post_id']
        post = get_object_or_404(Post, category=category, id=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
