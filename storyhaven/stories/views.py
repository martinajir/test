from rest_framework import permissions, viewsets

from .models import Bookmark, Chapter, Comment, Follow, Like, Story, Tag
from .serializers import (
    BookmarkSerializer,
    ChapterSerializer,
    CommentSerializer,
    FollowSerializer,
    LikeSerializer,
    StorySerializer,
    TagSerializer,
)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow safe methods to anyone; require ownership for writes."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None) or getattr(
            obj, 'follower', None
        )
        return owner == request.user


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().prefetch_related('tags', 'chapters')
    serializer_class = StorySerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        genre = self.request.query_params.get('genre')
        tag = self.request.query_params.get('tag')
        search = self.request.query_params.get('search')
        if genre:
            qs = qs.filter(genre__iexact=genre)
        if tag:
            qs = qs.filter(tags__slug=tag)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.distinct()


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        story_id = self.request.query_params.get('story')
        if story_id:
            qs = qs.filter(story_id=story_id)
        return qs

    def perform_create(self, serializer):
        story = serializer.validated_data['story']
        if story.author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not own this story.')
        serializer.save()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        chapter_id = self.request.query_params.get('chapter')
        if chapter_id:
            qs = qs.filter(chapter_id=chapter_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)


class BookmarkViewSet(viewsets.ModelViewSet):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthorOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
