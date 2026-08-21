from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Story(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        COMPLETED = 'completed', 'Completed'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    summary = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='stories')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'stories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Chapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['story', 'order']
        unique_together = ('story', 'order')

    def __str__(self):
        return f'{self.story.title} - Ch. {self.order}: {self.title}'


class Comment(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.chapter}'


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes'
    )
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chapter')

    def __str__(self):
        return f'{self.user} likes {self.chapter}'


class Follow(models.Model):
    """A user following either another user (author) or a story."""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following'
    )
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
        null=True,
        blank=True,
    )
    followed_story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='followers',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'followed_user'], name='unique_user_follow'
            ),
            models.UniqueConstraint(
                fields=['follower', 'followed_story'], name='unique_story_follow'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(followed_user__isnull=False, followed_story__isnull=True)
                    | models.Q(followed_user__isnull=True, followed_story__isnull=False)
                ),
                name='follow_exactly_one_target',
            ),
        ]

    def __str__(self):
        target = self.followed_user or self.followed_story
        return f'{self.follower} follows {target}'


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks'
    )
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='bookmarked_by')
    last_read_chapter = models.ForeignKey(
        Chapter, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story')

    def __str__(self):
        return f'{self.user} bookmarked {self.story}'
