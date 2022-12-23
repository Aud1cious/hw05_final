from django.urls import reverse
from django.test import TestCase
from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="NoName")
        cls.group = Group.objects.create(
            title="tgroup",
            slug="tslug",
            description="Тестовое описание",
        )
        cls.posts = [
            Post(
                author=cls.author,
                text=f"Тестовый пост {i}",
                group=cls.group,
            )
            for i in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def test_num_of_records(self):
        pages_to_test = ["", "?page=2"]
        records_per_page = [10, 3]
        for page_num in range(len(pages_to_test)):
            response = self.client.get(
                reverse("posts:index") + pages_to_test[page_num]
            )
            num_of_posts = response.context.get("page_obj").object_list
            self.assertEqual(len(num_of_posts), records_per_page[page_num])
