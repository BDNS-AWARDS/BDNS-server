from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework import serializers, status
from .models import *
from accounts.serializers import UserSerializer, UserProfileSerializer

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = ['image']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')  # 'request' 키를 가져오고, 없으면 None을 반환
        if request:
            data['image'] = request.build_absolute_uri(instance.image.url) # 이미지 URL을 절대 경로로 가져오기
        return data
    
class CategorySerializer(serializers.Serializer):
    categories = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

class PostSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        serializers = UserProfileSerializer(instance=obj.writer, context=self.context)
        return serializers.data

    # profile_image = serializers.SerializerMethodField()

    # def get_profile_image(self, obj):
    #     if obj.writer.profile_image:
    #         request = self.context.get('request')
    #         return request.build_absolute_uri(obj.writer.profile_image.url)
    #     else:
    #         return None

    def get_nickname(self, obj):
        return obj.writer.nickname
    # writer = serializers.SerializerMethodField()

    # def get_writer(self, obj):
    #     user_serializers = UserSerializer(instance=obj.writer, context=self.context)
    #     return user_serializers.data
        
    #게시글에 등록된 이미지 가져오기
    def get_images(self, obj):
        images = obj.images()
        return PostImageSerializer(instance=images, many=True, context=self.context).data

    def create(self, validated_data):
        image_set = self.context['request'].FILES.getlist('images')
        max_images = 2  # 이미지 수 2개로 제한

        if len(image_set) > max_images:
            response = {'error': f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        instance = Post.objects.create(**validated_data)

        for image_data in image_set:
            PostImage.objects.create(post=instance, image=image_data)
        return instance

    
    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('image')
        max_images = 2  # 이미지 수 2개로 제한

        if len(images_data) > max_images:
            response = {'error': f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
        # 기존 이미지가 있는 경우 삭제
        if images_data:
            instance.image.all().delete()
        
        # 새로운 이미지 추가
        for image_data in images_data:
            PostImage.objects.create(post=instance, image=image_data)

        return super().update(instance, validated_data)

    
    class Meta:
        model = Post
        fields = '__all__'
    
# class PostUpdateSerializer(serializers.ModelSerializer):
#     images = serializers.ListField(child=serializers.ImageField(), required=False)
#     writer = serializers.SerializerMethodField()

#     def get_writer(self, obj):
#         serializers = UserSerializer(instance=obj.writer, context=self.context)
#         return serializers.data

#     class Meta:
#         model = Post
#         fields = 'title','writer', 'content', 'category', 'images', 

#     def update(self, instance, validated_data):
#         images_data = self.context['request'].FILES.getlist('image')
#         max_images = 2  # 이미지 수 2개로 제한

#         if len(images_data) > max_images:
#             raise serializers.ValidationError(f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.')
        
#         # 기존 이미지 삭제
#         if images_data:
#             instance.image.all().delete()
#             # 새로운 이미지 추가
#             for image_data in images_data:
#                 PostImage.objects.create(post=instance, image=image_data)

#         return super().update(instance, validated_data)
    
# class PostRetrieveSerializer(serializers.ModelSerializer):
#     writer = serializers.SerializerMethodField()
#     images = serializers.SerializerMethodField()

#     #게시글에 등록된 이미지 가져오기
#     def get_images(self, obj):
#         image = obj.image.all() 
#         return PostImageSerializer(instance=image, many=True, context=self.context).data

#     def get_writer(self, obj):
#         serializers = UserSerializer(instance=obj.writer, context=self.context)
#         return serializers.data

#     class Meta:
#         model = Post
#         fields = '__all__'
#         depth = 1


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ScrapSerializer(serializers.ModelSerializer):
    post_title = serializers.SerializerMethodField()
    post_writer = serializers.SerializerMethodField()

    category = serializers.SerializerMethodField()

    class Meta:
        model = Scrap
        fields = '__all__'

    def get_post_title(self, scrap):
        return scrap.post.title

    def get_post_writer(self, scrap):
        return scrap.post.writer.username
    
    def get_category(self, scrap):
        return scrap.post.category