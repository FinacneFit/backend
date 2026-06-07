from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer):
  has_active_investment_profile = serializers.SerializerMethodField()

  class Meta:
    model = User
    fields = ("id", "email", "nickname", "has_active_investment_profile")

  def get_has_active_investment_profile(self, user):
    return False
  

class SignupSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8)
  password_confirm = serializers.CharField(write_only=True, min_length=8)

  class Meta:
    model = User
    fields = ("email", "nickname", "password", "password_confirm")

  def validate_email(self, email):
    if User.objects.filter(email=email).exists():
      raise serializers.ValidationError("이미 사용중인 이메일입니다")
    
    return email
  
  # 비밀번호 일치 여부 확인
  def validate(self, data):
    password = data.get("password")
    password_confirm = data.get("password_confirm")

    if password != password_confirm:
      raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
  
    return data

  def create(self, validated_data):
    validated_data.pop("password_confirm")

    email = validated_data["email"]
    nickname = validated_data["nickname"]
    password = validated_data["password"]

    user = User.objects.create_user(
      username=email,
      email=email,
      nickname=nickname,
      password=password,
    )

    return user


class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)

  # 비밀번호 검증
  def validate(self, data):
    email = data.get("email")
    password = data.get("password")

    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다")

    authenticated_user = authenticate(
      username = user.username,
      password = password,
    )

    if authenticated_user is None:
      raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다")
    
    if not authenticated_user.is_active:
      raise serializers.ValidationError("비활성화된 계정입니다")
    
    data["user"] = authenticated_user

    return data