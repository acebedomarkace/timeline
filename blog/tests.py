from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Subject, Family

class PostModelTest(TestCase):

    def setUp(self):
        # Create a user and a subject for the post
        self.user = User.objects.create_user(username='testuser', password='password')
        self.subject = Subject.objects.create(name='Test Subject')

    def test_post_creation(self):
        """Test that a Post can be created with a title, author, and subject."""
        post = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post',
            content='This is a test post.'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author.username, 'testuser')
        self.assertEqual(post.subject.name, 'Test Subject')
        self.assertEqual(str(post), 'Test Post')

    def test_get_youtube_embed_url(self):
        """Test the get_youtube_embed_url method with various URL formats."""
        post1 = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post 1',
            content='This is a test post.',
            youtube_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        post2 = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post 2',
            content='This is a test post.',
            youtube_url='https://youtu.be/dQw4w9WgXcQ'
        )
        post3 = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post 3',
            content='This is a test post.',
            youtube_url='https://www.youtube.com/embed/dQw4w9WgXcQ'
        )
        post4 = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post 4',
            content='This is a test post.',
            youtube_url='not a valid url'
        )

        self.assertEqual(post1.get_youtube_embed_url(), 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        self.assertEqual(post2.get_youtube_embed_url(), 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        self.assertEqual(post3.get_youtube_embed_url(), 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        self.assertIsNone(post4.get_youtube_embed_url())

class PostViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.subject = Subject.objects.create(name='Test Subject')
        self.post = Post.objects.create(
            author=self.user,
            subject=self.subject,
            title='Test Post',
            content='This is a test post.',
            status='published'
        )

    def test_view_count_increment(self):
        """Test that the view_count is incremented when the post_detail view is accessed."""
        self.client.get(f'/post/{self.post.pk}/')
        self.post.refresh_from_db()
        self.assertEqual(self.post.view_count, 1)

        self.client.get(f'/post/{self.post.pk}/')
        self.post.refresh_from_db()
        self.assertEqual(self.post.view_count, 2)

from django.db import IntegrityError

class FamilyModelTest(TestCase):

    def test_unique_invite_code(self):
        """Test that the invite_code is always unique."""
        Family.objects.create(name='The Simpsons', invite_code='ABC-123')
        with self.assertRaises(IntegrityError):
            Family.objects.create(name='The Flanders', invite_code='ABC-123')

class ProfileModelTest(TestCase):

    def test_profile_creation_signal(self):
        """Test that a Profile is automatically created whenever a new User is created."""
        user = User.objects.create_user(username='newuser', password='password')
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.user, user)
