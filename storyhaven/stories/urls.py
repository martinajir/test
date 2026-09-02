from rest_framework.routers import DefaultRouter

from .views import (
    BookmarkViewSet,
    ChapterViewSet,
    CommentViewSet,
    FollowViewSet,
    LikeViewSet,
    StoryViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register('stories', StoryViewSet, basename='story')
router.register('chapters', ChapterViewSet, basename='chapter')
router.register('comments', CommentViewSet, basename='comment')
router.register('likes', LikeViewSet, basename='like')
router.register('follows', FollowViewSet, basename='follow')
router.register('bookmarks', BookmarkViewSet, basename='bookmark')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = router.urls
