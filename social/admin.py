from django.contrib import admin

from social.models import User, Like, Post, Comment

admin.register(User)
admin.register(Post)
admin.register(Comment)
admin.register(Like)

