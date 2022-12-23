from django.test import TestCase, Client
from ..models import User, Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Noname")
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_homepage(self):
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_non_exist(self):
        response = self.guest_client.get("/non_exist/")
        self.assertEqual(response.status_code, 404)

    def test_author_page(self):
        response = self.authorized_author.get(
            f"/posts/{self.post.pk}/edit/"
        )
        self.assertEqual(response.status_code, 200)

    def test_authorized_create_page(self):
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_all(self):
        template_url_names = (
            "/",
            "/group/tslug/",
            "/profile/TestAuthor/",
            f"/posts/{self.post.pk}/",
        )
        for address in template_url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_templates(self):
        templates_url_names = {
            "posts/index.html": "/",
            "posts/group_list.html": "/group/tslug/",
            "posts/profile.html": "/profile/TestAuthor/",
            "posts/create_post.html": "/create/",
            "posts/post_detail.html": f"/posts/{self.post.pk}/",
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
