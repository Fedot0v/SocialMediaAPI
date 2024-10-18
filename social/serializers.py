from django.contrib.auth import authenticate
from rest_framework import serializers

from social.models import User, Comment, Post, Like


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError("Wrong email or password")

        else:
            raise serializers.ValidationError("Email or password is required")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "image"
            "first_name",
            "last_name",
        )


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "image")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("user", "content", "created_at")
        read_only_fields = ("user", "created_at")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "user",
            "content",
            "image",
            "created_at",
            "likes"
        )
        read_only_fields = ("user", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("user",)
