from django.test import Client, TestCase
from django.core.cache import cache
from django.urls import reverse

from ..models import Group, Post, User

URL_INDEX = reverse("posts:index")


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="TestAuthor")
        cls.group = Group.objects.create(
            title="tgroup",
            slug="tslug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_cache_index_page_exists(self):
        response = self.authorized_author.get(URL_INDEX)
        cached_old = response.content
        Post.objects.all().delete()
        response = self.authorized_author.get(URL_INDEX)
        cached_new = response.content
        self.assertEqual(cached_old, cached_new)

    def test_cache_updates(self):
        response = self.authorized_author.get(URL_INDEX)
        cached_response_content = response.content
        cache.clear()
        Post.objects.create(
            text="test text test", group=self.group, author=self.author
        )
        response = self.authorized_author.get(URL_INDEX)
        self.assertNotEqual(cached_response_content, response.content)
