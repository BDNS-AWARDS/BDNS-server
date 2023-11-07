from rest_framework import serializers
from .models import Post, PostImage

class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = PostImage
        fields = ['image']

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)  # 다중 이미지 필드 허용
    category = serializers.CharField(source='category')

    class Meta:
        model = Post
        fields = '__all__'

    def validate_images(self, value):
        max_images = 2  # 이미지 수 2개로 제한
        if len(value) > max_images:
            raise serializers.ValidationError(f'최대 {max_images}개의 이미지를 업로드할 수 있습니다.')
        return value

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('image'):
            PostImage.objects.create(post=post, image=image_data)
        return post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostCreateSeraizlier(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = 'title', 'content', 'category'  

class PostUpdateSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = 'title', 'content', 'category'

class PostRetrieveSeraizlier(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        depth = 1