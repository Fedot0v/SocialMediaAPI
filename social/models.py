import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify


def create_custom_path(instance, filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower().strip('.')

    if isinstance(instance, Post):
        uploads_dir = os.path.join("user", "post")
        return os.path.join(
            uploads_dir,
            f"{slugify(instance.user)}-{uuid.uuid4()}.{ext}"
        )
    if isinstance(instance, User):
        uploads_dir = os.path.join("user", "profile")
        return os.path.join(
            uploads_dir,
            f"{slugify(instance.email)}-{uuid.uuid4()}.{ext}"
        )


class User(AbstractUser):
    image = models.ImageField(
        upload_to=create_custom_path,
        null=True,
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to=create_custom_path,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.content


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user} liked {self.post}"
