from django.contrib import admin

from .models import Bookmark, Chapter, Comment, Follow, Like, Story, Tag


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ['order', 'title', 'is_published']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'status', 'updated_at']
    list_filter = ['status', 'genre']
    search_fields = ['title', 'summary', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['story', 'order', 'title', 'is_published']
    list_filter = ['is_published']
    search_fields = ['title', 'story__title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['chapter', 'author', 'created_at']
    search_fields = ['body']


admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Bookmark)
