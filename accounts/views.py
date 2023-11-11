from django.forms import ValidationError
import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView


from rest_framework import viewsets

from .serializers import UserSerializer

from django.views.decorators.csrf import csrf_exempt

from .authentication import CookieAuthentication

# BASE_URL = 서버 도메인 
# BASE_URL = 'http://15.164.160.92'
BASE_URL = 'http://127.0.0.1:8000'
KAKAO_CALLBACK_URI = BASE_URL + '/api/kakao/callback'
# KAKAO_CALLBACK_URI = 'http://localhost:3000/api/kakao/callback'

class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

@csrf_exempt
def kakao_login(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    print("toLogin")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )

def kakao_callback(request):
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    print("before token req")

    # Access Token Request
    token_req = requests.post(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}"
    )
    token_req_json = token_req.json()

    error = token_req_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    access_token = token_req_json.get('access_token')
    
    print("before profile req")
    # Get User Profile
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_json = profile_request.json()
    print("after profile req")
    print(profile_json)
    error = profile_json.get("error")
    if error is not None:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    kakao_account = profile_json.get('kakao_account')
    
    profile = kakao_account.get('profile')

    nickname = profile.get('nickname')

    user_id = nickname + "_" + str(profile_json.get('id'))

    # Signup or Signin
    try:
        user = User.objects.get(username=user_id)
        # 기존 사용자의 경우
        social_user = SocialAccount.objects.get(user=user)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

    except User.DoesNotExist:
        # 새로운 사용자의 경우
        user = User.objects.create_user(username=user_id, password=None)

        user.save()

        social_user = SocialAccount.objects.create(user=user, provider='kakao', uid=str(profile_json.get('id')), extra_data=profile_json)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}/api/kakao/login/finish", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
    
    refresh_token = RefreshToken.for_user(user)
    access_token = str(refresh_token.access_token)
    
    # 로그인 과정 및 토큰 발급을 거치고 난 후 redirect할 주소
    # frontend_redirect_uri = 'http://15.164.160.92'
    # frontend_redirect_uri = 'http://3.39.94.87'
    frontend_redirect_uri = 'http://127.0.0.1:3000'
    # print("check nickname")
    # print(request.user.nickname)
    

    if user.nickname != '' and user.nickname != None: 

        frontend_redirect_uri += '/mainpage'
    else:
        frontend_redirect_uri += '/setprofile'

    response = redirect(frontend_redirect_uri)
    response.set_cookie('access_token', access_token, max_age=360000, httponly=True)

    return response

class KakaoLogoutView(APIView):
    def get(self, request):
        rest_api_key = getattr(settings, 'KAKAO_APP_ADMIN_KEY')
        if rest_api_key:
            user = request.user
            if user:
                kakao_uid = user.socialaccount_set.get(provider='kakao').uid

                kakao_response = requests.post('https://kapi.kakao.com/v1/user/logout', headers={
                    'Authorization': f'KakaoAK {rest_api_key}'
                }, data={
                    'target_id_type': 'user_id',
                    'target_id': kakao_uid
                })
                if kakao_response.status_code == 200:
                    # 카카오 토큰 만료 성공
                    response = Response({'message': 'Kakao logout successful.'}, status=status.HTTP_200_OK)
                    response.delete_cookie('access_token')
                    return response
        return Response({'message': 'Invalid Kakao token.'}, status=status.HTTP_400_BAD_REQUEST)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CookieAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def current_user(self, request):
        user_serializer = self.serializer_class(request.user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def register(self, request):
        if request.method == 'POST':
            # 회원가입
            nickname = request.data.get('nickname')
            profile_image = request.data.get('profile_image')

            if not nickname:
                return Response({'error': '닉네임은 필수 필드입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=request.user.id)
            user.nickname = nickname
            user.profile_image = profile_image
            user.save()

            user_serializer = self.serializer_class(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        if request.method == 'PATCH':
            nickname = request.data.get('nickname')
            profile_image = request.data.get('profile_image')
            
            if nickname:
                user.nickname = nickname
            
            if profile_image:
                user.profile_image = profile_image

            user.save()
            user_serializer = self.serializer_class(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return super().update(request, *args, **kwargs)
        

    @action(detail=False, methods=['POST'])
    def check_nickname(self, request):
        nickname = request.data.get('nickname')
        try:
            serializer = UserSerializer(data={'nickname': nickname}, context={'request': request})
            serializer.validate_nickname(nickname)
            return Response({'Response': "Success"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'Response': "Fail", 'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)