from rest_framework import serializers

from .models import Bookmark, Chapter, Comment, Follow, Like, Story, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = [
            'id', 'story', 'title', 'order', 'content',
            'is_published', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ChapterListSerializer(serializers.ModelSerializer):
    """Lightweight chapter representation used when nested inside a Story."""

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'is_published']


class StorySerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), write_only=True, required=False
    )
    chapters = ChapterListSerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = [
            'id', 'author', 'title', 'slug', 'summary', 'cover_image',
            'genre', 'tags', 'tag_names', 'status', 'chapters',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        story = Story.objects.create(**validated_data)
        self._set_tags(story, tag_names)
        return story

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_names is not None:
            self._set_tags(instance, tag_names)
        return instance

    @staticmethod
    def _set_tags(story, tag_names):
        if not tag_names:
            return
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        story.tags.set(tags)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'chapter', 'author', 'body', 'created_at']
        read_only_fields = ['created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'user', 'chapter', 'created_at']
        read_only_fields = ['created_at']


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.ReadOnlyField(source='follower.username')

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'followed_user', 'followed_story', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, attrs):
        followed_user = attrs.get('followed_user')
        followed_story = attrs.get('followed_story')
        if bool(followed_user) == bool(followed_story):
            raise serializers.ValidationError(
                'Provide exactly one of followed_user or followed_story.'
            )
        return attrs


class BookmarkSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'story', 'last_read_chapter', 'created_at']
        read_only_fields = ['created_at']
