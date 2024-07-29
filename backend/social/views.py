# backend/social/views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        post = self.get_object()
        image = request.FILES.get('image')
        if image:
            post.images.create(image=image)
            return Response({'status': 'image added'})
        return Response({'status': 'no image provided'}, status=400)
