from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh_token'])
        data = {'access_token': str(refresh.access_token)}

        return data
    
class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True, required=False)
    
    def validate_nickname(self, value):
        min_length = 2
        max_length = 10
        user = self.context['request'].user
        # user nickname이 이미 존재하는 경우 : User.objects.filter(nickname=value).exclude(id=user.id)
        # 회원가입 된 것이므로 본인 닉네임 제외하고 중복 검사
        # user nickname이 none인 경우 : User.objects.filter(nickname=value)
        # 회원가입 전이므로 모든 nickname 대해 중복 검사
        existing_users = User.objects.filter(nickname=value).exclude(id=user.id)if user.nickname is not None else User.objects.filter(nickname=value)
        
        if existing_users.exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        if not value:
            raise serializers.ValidationError("닉네임을 입력해주세요.")
        if len(value) < min_length or len(value) > max_length:
            raise serializers.ValidationError("닉네임은 2~10자로 입력해야 합니다.")
        
        return value
    class Meta:
        model = User
        fields = "id","username","nickname","profile_image"

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(use_url=True, required=False)
    
    def get_profile_image(self, obj):
        if obj.profile_image is not None:
            return obj.profile_image.url
        
        return None
    class Meta:
        model = User
        fields = "nickname", "profile_image"

        