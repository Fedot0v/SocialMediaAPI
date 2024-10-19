from django.utils import timezone

from social.models import Post, User

from celery import shared_task



@shared_task
def create_post_at_a_certain_time(content, image, user_id):
    user = User.objects.get(id=user_id)
    post = Post.objects.create(
        content=content,
        image=image,
        user=user,
        created_at=timezone.now()
    )
    return post.id
