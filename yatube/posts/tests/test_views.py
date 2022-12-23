from django.test import TestCase
from django import forms

from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User


class ViewTests(TestCase):
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
        cls.url_index = ("posts:index", "posts/index.html")
        cls.url_group = ("posts:group_list", "posts/group_list.html")

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def multiple_assertion(
        self, list_of_vars, list_of_expected_results, test_name=None
    ):
        for var, expected_value in zip(
            list_of_vars, list_of_expected_results
        ):
            with self.subTest(
                f"{test_name}: {var} is not equal to {expected_value}"
            ):
                self.assertEqual(var, expected_value)

    def test_right_template(self):
        templates = {
            reverse(self.url_index[0]): "posts/index.html",
            reverse(
                self.url_group[0], kwargs={"slug": self.group.slug}
            ): self.url_group[1],
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.pk}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.pk}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates.items():
            with self.subTest(template=template):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        url, page = self.url_index
        response = self.authorized_client.get(reverse(url))
        author = response.context.get("page_obj")[0].author.username
        post_text = response.context.get("page_obj")[0].text
        group_title = response.context.get("page_obj")[0].group.title
        vars_to_test = [post_text, author, group_title]
        expected_values = ["Тестовый пост", "TestAuthor", "tgroup"]
        self.multiple_assertion(
            vars_to_test, expected_values, "index_context"
        )

    def test_group_list_context(self):
        url = reverse(self.url_group[0], kwargs={"slug": self.group.slug})
        response = self.authorized_client.get(url)
        title = response.context.get("group").title
        slug = response.context.get("group").slug
        description = response.context.get("group").description
        vars_to_test = [title, description, slug]
        expected_values = ["tgroup", "Тестовое описание", "tslug"]
        self.multiple_assertion(
            vars_to_test, expected_values, "group_list_context"
        )

    def test_profile_context(self):
        url = reverse("posts:profile", kwargs={"username": self.author})
        response = self.authorized_author.get(url)
        author = response.context.get("page_obj")[0].author.username
        text = response.context.get("page_obj")[0].text
        group_title = response.context.get("page_obj")[0].group.title
        vars_to_test = [text, author, group_title]
        expected_values = ["Тестовый пост", "TestAuthor", "tgroup"]
        self.multiple_assertion(
            vars_to_test, expected_values, "profile_context"
        )

    def test_post_detail_context(self):
        url = reverse("posts:post_detail", kwargs={"post_id": self.post.pk})
        response = self.authorized_author.get(url)
        post_author = response.context.get("post").author.username
        post_text = response.context.get("post").text
        group_post = response.context.get("post").group.title
        vars_to_test = [post_text, post_author, group_post]
        expected_values = ["Тестовый пост", "TestAuthor", "tgroup"]
        self.multiple_assertion(
            vars_to_test, expected_values, "post_detail_context"
        )

    def test_post_edit_context(self):
        url = reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        response = self.authorized_author.get(url)
        self.assertTrue(response.context.get("is_edit"))
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertEqual(response.context.get("form").instance, self.post)

    def test_create_post_context(self):
        url = reverse("posts:post_create")
        response = self.authorized_client.get(url)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get("form").fields[field]
                self.assertIsInstance(form_field, expected)

    def test_post_shows(self):
        urls = (
            reverse(self.url_index[0]),
            reverse(self.url_group[0], kwargs={"slug": self.group.slug}),
            reverse(
                "posts:profile", kwargs={"username": self.author.username}
            ),
        )
        for url in urls:
            response = self.authorized_author.get(url)
            self.assertEqual(
                len(response.context["page_obj"].object_list), 1
            )

    def test_post_group(self):
        new_group = Group.objects.create(
            title="New test group",
            slug="new_group",
            description="Доп группа для теста, что пост не попал сюда",
        )
        response = self.authorized_client.get(
            reverse(self.url_group[0], kwargs={"slug": new_group.slug})
        )
        self.assertEqual(len(response.context["page_obj"]), 0)
