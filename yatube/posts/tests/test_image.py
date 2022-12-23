import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_gif = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        cls.create_gif = SimpleUploadedFile(
            name="create.gif",
            content=cls.test_gif,
            content_type="image/gif",
        )
        cls.paginator_gif = SimpleUploadedFile(
            name="paginator.gif",
            content=cls.test_gif,
            content_type="image/gif",
        )
        cls.user = User.objects.create_user(username="Noname")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="tslug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

        cls.post_with_image = Post.objects.create(
            author=cls.user,
            text="Тест контекста",
            group=cls.group,
            image=cls.paginator_gif,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_image(self):
        count = Post.objects.count()
        form_data = {
            "text": "Пост с картинкой.",
            "image": self.create_gif,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", args=[self.user])
        )
        self.assertEqual(Post.objects.count(), count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text="Пост с картинкой.",
                image="posts/create.gif",
            ).exists()
        )

    def test_paginator_image(self):
        urls = [
            reverse("posts:index"),
            reverse("posts:group_list", args=["tslug"]),
            reverse("posts:profile", args=["auth"]),
        ]

        for url in urls:
            response = self.authorized_client.get(url)
            try:
                posts = list(response.context.get("page_obj").object_list)
                ind = posts.index(self.post_with_image)
            except Exception as e:
                self.assertFalse(False)

            with self.subTest(url=url):
                self.assertEqual(
                    posts[ind].image,
                    self.post_with_image.image,
                )

    def test_post_detail_image(self):
        url = reverse("posts:post_detail", args=[self.post_with_image.pk])
        response = self.authorized_client.get(url)
        post = response.context["post"]
        self.assertEqual(
            post.image,
            self.post_with_image.image,
        )
