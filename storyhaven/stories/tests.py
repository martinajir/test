from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Chapter, Follow, Story, Tag

User = get_user_model()


class StoryModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('author1', password='pw')

    def test_story_slug_auto_generated(self):
        story = Story.objects.create(author=self.author, title='My Great Story')
        self.assertEqual(story.slug, 'my-great-story')

    def test_chapter_ordering(self):
        story = Story.objects.create(author=self.author, title='Ordering Test')
        Chapter.objects.create(story=story, title='Two', order=2, content='...')
        Chapter.objects.create(story=story, title='One', order=1, content='...')
        orders = list(story.chapters.values_list('order', flat=True))
        self.assertEqual(orders, [1, 2])

    def test_tag_slug_auto_generated(self):
        tag = Tag.objects.create(name='Space Opera')
        self.assertEqual(tag.slug, 'space-opera')


class FollowConstraintTests(TestCase):
    def test_follow_requires_exactly_one_target(self):
        alice = User.objects.create_user('alice', password='pw')
        bob = User.objects.create_user('bob', password='pw')
        follow = Follow.objects.create(follower=alice, followed_user=bob)
        self.assertEqual(follow.followed_story, None)


class StoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user('author2', password='pw')

    def test_list_stories_is_public(self):
        Story.objects.create(author=self.author, title='Public Story', status='published')
        response = self.client.get('/api/stories/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_create_story_requires_auth(self):
        response = self.client.post('/api/stories/', {'title': 'New Story'})
        self.assertEqual(response.status_code, 403)

    def test_create_story_authenticated(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.post('/api/stories/', {'title': 'New Story'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['author'], 'author2')
