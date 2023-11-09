from rest_framework import serializers
from .models import *

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = ['image']

    def to_representation(self, instance):
        return instance.image.url

class PostSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    #게시글에 등록된 이미지 가져오기
    def get_images(self, obj):
        image = obj.image.all() 
        return PostImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = Post
        fields = '__all__'

    def create(self, validated_data):
        image_set = self.context['request'].FILES.getlist('image')
        max_images = 2  # 이미지 수 2개로 제한

        if len(image_set) > max_images:
            raise serializers.ValidationError(f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.')

        instance = Post.objects.create(**validated_data)

        for image_data in image_set:
            PostImage.objects.create(post=instance, image=image_data)
        return instance
    
class PostUpdateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)

    class Meta:
        model = Post
        fields = 'title', 'content', 'category', 'images'

    def update(self, instance, validated_data):
        images_data = self.context['request'].FILES.getlist('image')
        max_images = 2  # 이미지 수 2개로 제한

        if len(images_data) > max_images:
            raise serializers.ValidationError(f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.')
        
        # 기존 이미지 삭제
        instance.image.all().delete()

        # 새로운 이미지 추가
        for image_data in images_data:
            PostImage.objects.create(post=instance, image=image_data)

        return super().update(instance, validated_data)
    
class PostRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
        depth = 1

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class ScrapSerializer(serializers.ModelSerializer):
    post_title = serializers.SerializerMethodField()
    post_writer = serializers.SerializerMethodField()
    class Meta:
        model = Scrap
        fields = '__all__'

    def get_post_title(self, scrap):
        return scrap.post.title

    def get_post_writer(self, scrap):
        return scrap.post.writer.username