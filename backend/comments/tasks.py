from celery import shared_task
from .models import Comment


@shared_task
def process_new_comment(comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        # Add background logic here, e.g., notify users
        print(f'Processing comment: {comment.content}')
    except Comment.DoesNotExist:
        print(f'Comment with id {comment_id} does not exist')
