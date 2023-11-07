from rest_framework import viewsets
from .models import Post
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.authentication import AllowAnyAuthentication, CookieAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

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