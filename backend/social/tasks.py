from celery import shared_task
from .models import Post


@shared_task
def process_new_post(post_id):
    try:
        post = Post.objects.get(id=post_id)
        # Add your background logic here, e.g., send notifications, analyze post
        print(f'Processing post by {post.author.username}: {post.title}')
    except Post.DoesNotExist:
        print(f'Post with id {post_id} does not exist')
