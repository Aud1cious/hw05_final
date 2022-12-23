from django.test import TestCase
from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="Noname")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_model_post_have_correct_object_names(self):
        post = PostModelTest.post
        post_text = post.text[:15]
        self.assertEqual(post_text, str(post))

    def test_model_group_have_correct_object_names(self):
        group = PostModelTest.group
        group_name = group.title
        self.assertEqual(group_name, str(group))
