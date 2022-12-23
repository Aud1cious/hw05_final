from django.test import TestCase

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user("test_user")
        cls.author = User.objects.create_user("test_author")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.group_meta = Group.objects.create(
            title="Мета группа",
            slug="Мета слаг",
            description="Мета описание",
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
        )

        cls.form = PostForm()

    def setUp(self):
        self.client_user = Client()
        self.client_user.force_login(TaskCreateFormTests.user)
        self.client_author = Client()
        self.client_author.force_login(TaskCreateFormTests.author)
        self.client_anonymous = Client()

    def test_task_creation_db(self):
        post_nums = Post.objects.count()
        post_data = {
            "text": "Текст формы",
            "group": self.group.pk,
        }
        response = self.client_user.post(
            reverse("posts:post_create"), data=post_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile", kwargs={"username": self.user.username}
            ),
        )
        self.assertEqual(Post.objects.count(), post_nums + 1)
        self.assertTrue(Post.objects.filter(text="Текст формы").exists())

    def test_post_changed(self):
        post_data = {
            "text": "Текст формы",
            "group": self.group.pk,
        }
        self.client_author.post(
            reverse("posts:post_create"), data=post_data, follow=True
        )
        post = Post.objects.get(id=self.group.pk)
        self.client_author.get(f"/posts/{post.pk}/edit/")
        form_data = {
            "text": "Поменял, проверил",
            "group": self.group.pk,
        }
        response = self.client_author.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.group.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_edit.text, "Поменял, проверил")
        post = Post.objects.get(id=self.group.pk)
        self.client_author.get(f"/posts/{post.pk}/edit/")
        form_data = {
            "text": "Новая группа",
            "group": self.group_meta.pk,
        }
        response = self.client_author.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.group.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_edit.group.title, "Мета группа")

    def test_anonymous_creation(self):
        post_nums = Post.objects.count()
        post_data = {
            "text": "Текст формы",
            "group": self.group.pk,
        }
        self.client_anonymous.post(
            reverse("posts:post_create"), data=post_data, follow=True
        )
        self.assertEqual(Post.objects.count(), post_nums)

    def test_anonymous_post_changed(self):
        form_data = {
            "text": "Поменял за анонима!",
            "group": self.group.pk,
        }
        response = self.client_anonymous.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.group.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_edit.text, "Тестовый пост")

    def test_non_author_post_changed(self):
        form_data = {
            "text": "Поменял, не за автора!",
            "group": self.group.pk,
        }
        response = self.client_user.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.group.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post_edit.text, "Тестовый пост")
