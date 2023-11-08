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
        current_user = self.context['request'].user

        if User.objects.filter(nickname=value).exclude(id=current_user.id).exists():
            raise serializers.ValidationError("이미 존재하는 닉네임입니다.")
        elif not value:
            raise serializers.ValidationError("닉네임을 입력해주세요.")
        elif len(value) < min_length or len(value) > max_length:
            raise serializers.ValidationError("닉네임은 2~10자로 입력해야 합니다.")
        
        return value
    

    class Meta:
        model = User
        fields = "id","username","nickname","profile_image"