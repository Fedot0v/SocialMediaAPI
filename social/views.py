from datetime import datetime

from celery.utils.time import make_aware
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from social.models import User, Comment, Post, Like
from social.serializers import (
    UserSerializer,
    UserListSerializer,
    RegistrationSerializer,
    LoginSerializer, CommentSerializer, PostSerializer, LikeSerializer
)
from social.tasks import create_post_at_a_certain_time


@api_view(["POST"])
def schedule_post_creation(request):
    content = request.data.get("content")
    image = request.data.get("image")
    author_id = request.user.id

    scheduled_time_str = request.data.get("time")
    scheduled_time = make_aware(
        datetime.strptime(
            scheduled_time_str,
            "%Y-%m-%d %H:%M:%S"
        )
    )

    create_post_at_a_certain_time.apply_async(
        args=[content, image, author_id],
        eta=scheduled_time
    )

    return Response(
        {"message": "Post creation scheduled"},
        status=status.HTTP_201_CREATED
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["create", "login"]:
            return (AllowAny(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset

        username = self.request.query_params.get("username", None)

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer

        if self.action == "create":
            return RegistrationSerializer

        if self.action == "login":
            return LoginSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED
        )

    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "login successful",
                "username": user.username,
                "token": token.key,
            },
            status=status.HTTP_200_OK
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        post = Post.objects.filter(id=request.data["id"]).first()

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            like.delete()
            post.likes -= 1
            return Response(
                {"message": "Like removed"},
                status = status.HTTP_204_NO_CONTENT
            )
        post.likes += 1
        post.save()

        return Response(
            {"message": "Post liked"},
            status=status.HTTP_201_CREATED
        )

    def list(self, request, *args, **kwargs):
        post_id = request.query_params.get("id", None)

        if not post_id:
            return Response(
                {"error": "Post ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        post = Post.objects.filter(id=post_id).first()

        if not post:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        likes = Like.objects.filter(post=post)
        return Response(
            {"likes": likes.count()},
            status=status.HTTP_200_OK
        )
