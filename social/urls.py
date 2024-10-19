from django.urls import path
from rest_framework import routers

from social import views


app_name = "social"

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, basename="users")
router.register("posts", views.PostViewSet, basename="posts")
router.register("comments", views.CommentViewSet, basename="comments")
router.register("likes", views.LikeViewSet, basename="likes")

urlpatterns = router.urls + [
    path(
        "login/",
        views.UserViewSet.as_view({"post": "login"}),
        name="user-login"
    ),
    path(
        "register/",
        views.UserViewSet.as_view({"post": "create"}),
        name="user-register"
    ),
    path(
        "schedule-post/",
        views.schedule_post_creation,
        name="schedule-post-creation"
    ),
]
