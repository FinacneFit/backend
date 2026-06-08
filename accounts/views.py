from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import UserSerializer, SignupSerializer, LoginSerializer

class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serialzier = SignupSerializer(data=request.data)

        if serialzier.is_valid():
            user = serialzier.save()

            login(request, user)

            context = {
                "message" : "회원가입 완료",
                "user" : UserSerializer(user).data,
            }

            return Response(context, status=status.HTTP_201_CREATED)
    
        context = {
            "message" : "회원가입 입력값이 올바르지 않습니다",
            "errors" : serialzier.errors,
        }

        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serialzier = LoginSerializer(data=request.data)

        if serialzier.is_valid():
            user = serialzier.validated_data["user"]

            login(request, user)

            context = {
                "message" : "로그인 완료",
                "user" : UserSerializer(user).data,
            }

            return Response(context, status=status.HTTP_200_OK)
        
        context = {
            "message" : "로그인 입력값이 올바르지 않습니다",
            "errors" : serialzier.errors,
        }

        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)

        context = {
            "message" : "로그아웃 완료"
        }

        return Response(context, status=status.HTTP_200_OK)
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            "user" : UserSerializer(request.user).data,
        }

        return Response(context, status=status.HTTP_200_OK)